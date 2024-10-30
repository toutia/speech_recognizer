
chatbot_config = {
    "URL": "http://localhost:5555/",
    "DEBUG": True, # When this flag is set, the UI displays detailed riva data
    "VERBOSE": True  # print logs/details for diagnostics
}

riva_config = {
    "RIVA_SPEECH_API_URL": "localhost:50051", # Replace the IP port with your hosted RIVA endpoint
    "VERBOSE": True  # print logs/details for diagnostics
}



asr_config = {
    "VERBOSE": True, # Print logs/details for diagnostics
    "SAMPLING_RATE": 16000, # The Sampling Rate for the audio input file. The only value currently supported is 16000
    "LANGUAGE_CODE": "en-US", # The language code as a BCP-47 language tag. The only value currently supported is "en-US"
    "ENABLE_AUTOMATIC_PUNCTUATION": True, # Enable or Disable punctuation in the transcript generated. The only value currently supported by the chatbot is True (Although Riva ASR supports both True & False)
    "VERBATIM_TRANSCRIPTS":True,
    "PROFANITY_FILTER":False,
    "SPEAKER_DIARIZATION":False,
    "DIARIZATION_MAX_SPEAKERS":3
}

