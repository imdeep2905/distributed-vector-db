import os
import grpc
import random
import concurrent.futures
import json
import nltk
from google.protobuf.empty_pb2 import Empty
from protos import vdb_service_pb2, vdb_service_pb2_grpc
from models import (
    HealthResponse,
    SimilaritySearchRequest,
    SimilaritySearchResponse,
    AddBigTextRequest,
    AddTextRequest,
    AddTextResponse,
)

STRATEGY = os.environ.get("VDB_INSERTION_STRATEGY", "random_2")


class VDBConnector:
    def __init__(self, vdb_addresses):
        self.num_vdbs = len(vdb_addresses)
        self.vdb_addresses = vdb_addresses
        self.stubs = [
            vdb_service_pb2_grpc.VDBServiceStub(
                grpc.insecure_channel(vdb_address)
            )
            for vdb_address in self.vdb_addresses
        ]

    @staticmethod
    def split_text_into_parts(text, sentences_per_part):
        import ssl

        ssl._create_default_https_context = ssl._create_unverified_context
        nltk.download("punkt")

        sentences = nltk.sent_tokenize(text)

        parts = [
            sentences[i : i + sentences_per_part]
            for i in range(0, len(sentences), sentences_per_part)
        ]

        return parts

    @staticmethod
    def execute_with_threads(fns, args, kwargs, num_workers=10):
        results = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_workers
        ) as executor:
            futures = [
                executor.submit(fn, *arg, **kwarg)
                for (fn, arg, kwarg) in zip(fns, args, kwargs)
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Exception occurred: {e}")
                    results.append("OFFLINE")

        return results

    def healths(self):
        responses = self.execute_with_threads(
            [stub.health for stub in self.stubs],
            [[Empty()] for _ in range(self.num_vdbs)],
            [{} for _ in range(self.num_vdbs)],
            self.num_vdbs,
        )
        healths = []
        for vdb_address, response in zip(self.vdb_addresses, responses):
            if isinstance(response, str):
                healths.append(
                    HealthResponse(
                        address=vdb_address,
                        used_ram=-1,
                        total_ram=-1,
                        used_cpu=-1,
                        avg_response_time=-1,
                    )
                )
            else:
                healths.append(
                    HealthResponse(
                        address=vdb_address,
                        used_ram=round(response.used_ram, 3),
                        total_ram=round(response.total_ram, 3),
                        used_cpu=round(response.used_cpu, 2),
                        avg_response_time=round(response.avg_response_time),
                    )
                )
        return healths

    def similarity_search(self, params: SimilaritySearchRequest):
        responses = self.execute_with_threads(
            [stub.similaritySearch for stub in self.stubs],
            [
                [
                    vdb_service_pb2.SimilaritySearchRequest(
                        query_texts=params.query_texts,
                        n_results=params.n_results,
                    )
                ]
                for _ in range(self.num_vdbs)
            ],
            [{} for _ in range(self.num_vdbs)],
            self.num_vdbs,
        )
        ids, distances, metadatas, documents = [], [], [], []
        for response in responses:
            ids.extend(list(response.ids))
            distances.extend(list(response.distances))
            metadatas.extend(list(response.metadatas))
            documents.extend(list(response.documents))

        dedup_ids, dedup_distances, dedup_metadatas, dedup_documents = (
            [],
            [],
            [],
            [],
        )
        seen_ids = set()
        for id, distance, metadata, document in zip(
            ids, distances, metadatas, documents
        ):
            if id not in seen_ids:
                seen_ids.add(id)
                dedup_ids.append(id)
                dedup_distances.append(distance)
                dedup_documents.append(document)
                dedup_metadatas.append(metadata)

        dedup_ids, dedup_distances, dedup_metadatas, dedup_documents = zip(
            *sorted(
                list(
                    zip(
                        dedup_ids,
                        dedup_distances,
                        dedup_metadatas,
                        dedup_documents,
                    )
                ),
                key=lambda x: x[1],
            )
        )
        return SimilaritySearchResponse(
            ids=dedup_ids,
            distances=dedup_distances,
            metadatas=[json.loads(metadata) for metadata in dedup_metadatas],
            documents=dedup_documents,
        )

    def add_text_in_stub(self, stub_i, document, metadata, id):
        self.stubs[stub_i].addText(
            vdb_service_pb2.AddTextRequest(
                documents=[document],
                metadatas=[json.dumps(metadata)],
                ids=[id],
            )
        )

    def add_texts_to_random2(self, documents, metadatas, ids):
        assert self.num_vdbs >= 2
        for document, metadata, id in zip(documents, metadatas, ids):
            first_i = random.randint(0, self.num_vdbs - 1)
            second_i = random.randint(0, self.num_vdbs - 1)
            while second_i == first_i:
                second_i = random.randint(0, self.num_vdbs - 1)
            self.add_text_in_stub(first_i, document, metadata, id)
            self.add_text_in_stub(second_i, document, metadata, id)

    def add_text(self, params: AddTextRequest):
        if STRATEGY == "random_2":
            self.add_texts_to_random2(
                params.documents, params.metadatas, params.ids
            )
            return AddTextResponse(ok=True)

        raise NotImplementedError("Strategy not found")

    def add_big_text(self, params: AddBigTextRequest):
        documents = self.split_text_into_parts(
            params.document, params.n_paragraph_sentences
        )
        return self.add_text(
            AddTextRequest(
                documents=["".join(d) for d in documents],
                metadatas=[params.metadata for _ in range(len(documents))],
                ids=[f"{params.id}__{i}" for i in range(len(documents))],
            )
        )
