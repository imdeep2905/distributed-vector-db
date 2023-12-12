from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import (
    HealthResponse,
    SimilaritySearchRequest,
    SimilaritySearchResponse,
    AddBigTextRequest,
    AddTextRequest,
    AddTextResponse,
)
from vdb_connector import VDBConnector

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vdb_connector = VDBConnector(
    vdb_addresses=["localhost:50051", "localhost:50051"]
)


@app.get("/health", response_model=list[HealthResponse])
def health():
    return vdb_connector.healths()


@app.post("/add_text", response_model=AddTextResponse)
def add_text(params: AddTextRequest):
    return vdb_connector.add_text(params)


@app.post("/add_big_text", response_model=AddTextResponse)
def add_big_text(params: AddBigTextRequest):
    return vdb_connector.add_big_text(params)


@app.post("/query", response_model=SimilaritySearchResponse)
def similarity_search(params: SimilaritySearchRequest):
    return vdb_connector.similarity_search(params)
