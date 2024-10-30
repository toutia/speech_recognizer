# Copy the service file to the systemd directory for custom services
sudo cp speech_recognizer.service /etc/systemd/system/speech_recognizer.service

# Reload the systemd manager configuration to recognize the new service file
sudo systemctl daemon-reload

# Start the speech_recognizer service immediately
sudo systemctl start speech_recognizer.service

# Enable the service to start automatically at boot
sudo systemctl enable speech_recognizer.service

# Check the current status of the speech_recognizer service to ensure it’s running correctly
sudo systemctl status speech_recognizer.service

# View real-time logs for the speech_recognizer service
journalctl -u speech_recognizer.service -f
