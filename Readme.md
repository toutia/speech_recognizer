--list-devices to get the input device 
python  transcribe_mic.py --input-device=0

###########################pyaudio related error ########################
pip uninstall pyaudio 


sudo apt-get install portaudio19-dev
pip install pyaudio