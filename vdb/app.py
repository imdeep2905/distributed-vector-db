import grpc
import time
import psutil
import json
import chromadb
from concurrent import futures
from protos import vdb_service_pb2, vdb_service_pb2_grpc


class VDBServicer(vdb_service_pb2_grpc.VDBServiceServicer):
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="default")
    num_request_served = 0
    total_time_taken_ms = 0.0

    @staticmethod
    def measure_execution_time(func):
        def wrapper(self, request, context):
            start_time = time.time()
            try:
                result = func(self, request, context)
            finally:
                end_time = time.time()
                execution_time_ms = (end_time - start_time) * 1000
                self.num_request_served += 1
                self.total_time_taken_ms += execution_time_ms
            return result

        return wrapper

    @staticmethod
    def get_system_info():
        memory_info = psutil.virtual_memory()
        used_ram = memory_info.used / (1024**2)  # in megabytes
        total_ram = memory_info.total / (1024**2)  # in megabytes

        cpu_percent = psutil.cpu_percent(interval=1)

        return used_ram, total_ram, cpu_percent

    def health(self, request, context):
        used_ram, total_ram, cpu_percent = VDBServicer.get_system_info()

        return vdb_service_pb2.HealthResponse(
            used_ram=used_ram,
            total_ram=total_ram,
            used_cpu=cpu_percent,
            avg_response_time=self.total_time_taken_ms
            / max(1, self.num_request_served),
        )

    @measure_execution_time
    def addText(self, request, context):
        try:
            self.collection.add(
                documents=list(request.documents),
                metadatas=[json.loads(x) for x in request.metadatas],
                ids=list(request.ids),
            )
            return vdb_service_pb2.AddTextResponse(ok=True)
        except Exception:
            return vdb_service_pb2.AddTextResponse(ok=False)

    @measure_execution_time
    def similaritySearch(self, request, context):
        search_result = self.collection.query(
            query_texts=request.query_texts, n_results=request.n_results
        )
        return vdb_service_pb2.SimilaritySearchResponse(
            ids=search_result["ids"][0],
            distances=search_result["distances"][0],
            metadatas=[json.dumps(x) for x in search_result["metadatas"][0]],
            documents=search_result["documents"][0],
        )


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vdb_service_pb2_grpc.add_VDBServiceServicer_to_server(
        VDBServicer(), server
    )
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


def main():
    serve()


if __name__ == "__main__":
    main()
