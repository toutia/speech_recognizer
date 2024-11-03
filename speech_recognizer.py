import argparse

import riva.client
from riva.client.argparse_utils import add_asr_config_argparse_parameters, add_connection_argparse_parameters

import riva.client.audio_io
from config import chatbot_config, riva_config, asr_config, tts_config  
import requests 




def parse_args() -> argparse.Namespace:
    default_device_info = riva.client.audio_io.get_default_input_device_info()
    default_device_index = None if default_device_info is None else default_device_info['index']
    parser = argparse.ArgumentParser(
        description="Streaming transcription from microphone via Riva AI Services",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input-device", type=int, default=default_device_index, help="An input audio device to use.")
    parser.add_argument("--list-devices", action="store_true", help="List input audio device indices.")
    parser = add_asr_config_argparse_parameters(parser, profanity_filter=True)
    parser = add_connection_argparse_parameters(parser)
    parser.add_argument(
        "--sample-rate-hz",
        type=int,
        help="A number of frames per second in audio streamed from a microphone.",
        default=16000,
    )
    parser.add_argument(
        "--file-streaming-chunk",
        type=int,
        default=1600,
        help="A maximum number of frames in a audio chunk sent to server.",
    )
    args = parser.parse_args()

    print(args)
    return args


def send_transcript(text, bot_name="sample_bot", user_conversation_index=1):
    url = chatbot_config['URL']
    data = {
        "message": text,
        "sender": "user123",
    }
    responses=[]
    try:
        response = requests.post(url, json=data)
        response_data = response.json()
        for e_resp in response_data:
             responses.append(e_resp.get('text'))
    except requests.exceptions.RequestException as e:
        print("Error during request:", e)

    # send to tts 
    url = tts_config['TTS_API_URL']
    

    for e_resp in responses:
        payload = {
            "voice":"English-US.Female-1",
            "text": e_resp
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise an error for bad responses
        except requests.RequestException as e:
            print(f"Failed to send message to endpoint: {e}")



# Example usage
new_transcript_text = "Hello! Welcome to your personal assistant. How can I assist you today?"
# new_transcript_text = "Hello!"

send_transcript(new_transcript_text)
def main() -> None:
    args = parse_args()
    if args.list_devices:
        riva.client.audio_io.list_input_devices()
        return
    auth = riva.client.Auth(args.ssl_cert, args.use_ssl,riva_config['RIVA_SPEECH_API_URL'], args.metadata)
    asr_service = riva.client.ASRService(auth)
    config = riva.client.StreamingRecognitionConfig(
        config=riva.client.RecognitionConfig(
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            language_code=args.language_code,
            max_alternatives=1,
            profanity_filter=args.profanity_filter,
            enable_automatic_punctuation=asr_config['ENABLE_AUTOMATIC_PUNCTUATION'],
            verbatim_transcripts=asr_config['VERBATIM_TRANSCRIPTS'],
            sample_rate_hertz=args.sample_rate_hz,
            audio_channel_count=1,
        ),
        interim_results=True,
    )
    riva.client.add_word_boosting_to_config(config, args.boosted_lm_words, args.boosted_lm_score)
    riva.client.add_endpoint_parameters_to_config(
        config,
        args.start_history,
        args.start_threshold,
        args.stop_history,
        args.stop_history_eou,
        args.stop_threshold,                                                                                                                                                                                                                                                    
        args.stop_threshold_eou
    )
    with riva.client.audio_io.MicrophoneStream(
        args.sample_rate_hz,
        args.file_streaming_chunk,
        device=args.input_device,
    ) as audio_chunk_iterator:
        
            responses=asr_service.streaming_response_generator(
                audio_chunks=audio_chunk_iterator,
                streaming_config=config,
            )
            for response in responses:
                if not response.results:
                    continue
                for result in response.results:
                    if not result.alternatives:
                        continue
                    transcript = result.alternatives[0].transcript
                    if result.is_final:
                    
                        for i, alternative in enumerate(result.alternatives):
                                # send this automatically to rasa
                                send_transcript(alternative.transcript)
                                print(alternative.transcript)
      
       


if __name__ == '__main__':
    main()
