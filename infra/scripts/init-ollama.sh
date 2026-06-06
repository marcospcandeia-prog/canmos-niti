#!/bin/bash
# Script para download modelo Ollama

set -e

echo "Waiting for Ollama to be ready..."
sleep 15

echo "Pulling Ollama model: ${OLLAMA_MODEL:-phi3:mini}"
ollama pull ${OLLAMA_MODEL:-phi3:mini}

echo "Ollama model downloaded successfully!"
echo "Available models:"
ollama list
