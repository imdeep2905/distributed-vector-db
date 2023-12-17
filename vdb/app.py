import grpc
import time
import psutil
import json
import socket
import subprocess
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
    
    @staticmethod
    def get_current_container_id():
        try:
            result = subprocess.run(["cat", "../etc/hostname"], stdout=subprocess.PIPE, text=True, check=True)
            container_id = result.stdout.strip()
            return container_id
        except Exception as e:
            print(e)

    @staticmethod
    def parse_memory(memory_str):
        # Parse memory string and convert to MiB
        if 'KiB' in memory_str:
            return float(memory_str.replace('KiB', '')) / 1024
        elif 'MiB' in memory_str:
            return float(memory_str.replace('MiB', ''))
        elif 'GiB' in memory_str:
            return float(memory_str.replace('GiB', '')) * 1024
        else:
            return 0.0  # Default to 0 if not recognized

    @staticmethod
    def get_container_info():
        # Get the current container ID
        container_id = VDBServicer.get_current_container_id()

        # Initialize variables
        used_ram = 0
        total_ram = 0
        cpu_percent = 0

        try:
            # Execute "docker stats" command
            command = [
                "docker",
                "stats",
                "--no-stream",
                container_id,
                "--format",
                "'{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}'"
            ]

            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, text=True)
            # Parse the output
            stats_parts = result.stdout.strip().split('|')
            cpu_percent = float(stats_parts[0][1:].replace('%', ''))
            mem_usage, mem_limit = map(str.strip, stats_parts[1].split('/'))
            used_ram = VDBServicer.parse_memory(mem_usage)
            total_ram = VDBServicer.parse_memory(mem_limit)
        except Exception as e:
            print(f"Error retrieving container info: {e}")

        return used_ram, total_ram, cpu_percent

    def health(self, request, context):
        used_ram, total_ram, cpu_percent = VDBServicer.get_container_info()

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


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vdb_service_pb2_grpc.add_VDBServiceServicer_to_server(
        VDBServicer(), server
    )
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print("Server started, listening on " + str(port))
    server.wait_for_termination()


if __name__ == "__main__":
    serve(50051)
