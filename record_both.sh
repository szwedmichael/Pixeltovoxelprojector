#!/bin/bash
# Record from cameras 0 and 2 simultaneously

DURATION=${1:-10}  # Default 10 seconds, or use first argument

echo "Starting synchronized recording for ${DURATION} seconds..."
echo "Camera 0 -> cam0_sky.mp4"
echo "Camera 2 -> cam2_sky.mp4"
echo ""

# Start both cameras in background using pipenv
pipenv run python webcam_recorder.py --camera 0 --output cam0_sky.mp4 --duration ${DURATION} &
PID1=$!

pipenv run python webcam_recorder.py --camera 2 --output cam2_sky.mp4 --duration ${DURATION} &
PID2=$!

# Wait for both to complete
wait $PID1
wait $PID2

echo ""
echo "Recording complete!"
echo "Files saved: cam0_sky.mp4, cam2_sky.mp4"
