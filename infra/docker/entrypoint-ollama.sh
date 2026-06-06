#!/bin/bash
# Ollama entrypoint: start server and pull model on first run

ollama serve &
OLLAMA_PID=$!

sleep 2

if ! ollama list 2>/dev/null | grep -q "${OLLAMA_MODEL}"; then
    echo "Pulling model: ${OLLAMA_MODEL}"
    ollama pull "${OLLAMA_MODEL}"
fi

wait $OLLAMA_PID
