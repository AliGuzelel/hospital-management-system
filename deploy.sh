#!/bin/bash

echo "Stopping old containers..."
docker compose down

echo "Building and starting microservice stack..."
docker compose up --build -d

echo "Deployment complete!"
docker compose ps