from pydantic import BaseModel


class HealthResponse(BaseModel):
    address: str
    used_ram: float
    total_ram: float
    used_cpu: float
    avg_response_time: float


class SimilaritySearchResponse(BaseModel):
    ids: list[str]
    distances: list[float]
    metadatas: list[dict]
    documents: list[str]


class AddTextRequest(BaseModel):
    documents: list[str]
    metadatas: list[dict]
    ids: list[str]


class AddTextResponse(BaseModel):
    ok: bool


class AddBigTextRequest(BaseModel):
    document: str
    metadata: dict
    id: str
    n_paragraph_sentences: int = 8


class SimilaritySearchRequest(BaseModel):
    query_texts: list[str]
    n_results: int = 1
