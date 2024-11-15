#!/bin/bash

# Define ports and log files (optional)

SPEECH_RECOGNIZER_LOG="speech_recognizer.log"


VENV_PATH="/home/touti/dev/speech_recognizer/.venv_sr"


echo "activating the virtual environment..."
source  "$VENV_PATH/bin/activate"
# Start the Rasa server
echo "Starting the speech recognizer ..."
python speech_recognizer.py > $SPEECH_RECOGNIZER_LOG 2>&1 &



trap "deactivate" EXIT