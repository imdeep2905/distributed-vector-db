#!/bin/bash
mkdir -p server/protos
mkdir -p vdb/protos
rm -rf server/protos/*
rm -rf vdb/protos/*
python -m grpc_tools.protoc -I. --python_out=./server/ --grpc_python_out=./server/ ./protos/vdb_service.proto
python -m grpc_tools.protoc -I. --python_out=./vdb/ --grpc_python_out=./vdb/ ./protos/vdb_service.proto