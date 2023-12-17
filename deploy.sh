#!/bin/bash
docker compose down  
docker volume create chromadb-data 
# Export project name
export COMPOSE_PROJECT_NAME="dsd"

VDB_REPLICAS="3"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild | -rb)
            REBUILD=true
            ;;
        --num_vdbs | -n_vdb)
            shift
            VDB_REPLICAS=$1
            ;;
        *)
            # Handle unknown options
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Set VDB_REPLICAS if provided in CLI
if [ -n "$VDB_REPLICAS" ]; then
    export VDB_REPLICAS="$VDB_REPLICAS"
fi

# Set the COMPOSE_PROJECT_NAME
export COMPOSE_PROJECT_NAME

# Build Docker containers if --rebuild or -rb is provided
if [ "$REBUILD" = true ]; then
    docker build -t vdb_worker -f Dockerfile.vdb .
    docker build -t vdb_server -f Dockerfile.server .
fi


# Run Docker Compose
docker compose up --build
