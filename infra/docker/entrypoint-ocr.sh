#!/bin/bash
# OCR Service Entrypoint
# Starts both the OCR API server and the background worker

set -e

echo "Starting OCR API server on port 8001..."
uvicorn app.modules.ocr.ocr_api:app --host 0.0.0.0 --port 8001 &
API_PID=$!

echo "Starting OCR Worker (polling)..."
python -m app.modules.ocr.worker &
WORKER_PID=$!

echo "OCR Service started. API PID=$API_PID, Worker PID=$WORKER_PID"

# Trap SIGTERM and SIGINT to gracefully stop both processes
trap "kill $API_PID $WORKER_PID 2>/dev/null; exit 0" SIGTERM SIGINT

# Wait for either process to exit
wait -n $API_PID $WORKER_PID

echo "OCR Service stopped."
exit 1
