import argparse
import riva.client
from riva.client.argparse_utils import (
    add_asr_config_argparse_parameters,
    add_connection_argparse_parameters,
)
import riva.client.audio_io
from config import riva_config, asr_config
import pyaudio
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


class RivaASRNode(Node):
    def __init__(self):
        super().__init__("riva_asr_node")
        self.cli = self.create_client(Trigger, "get_audio_playback_status")

        self.publisher_ = self.create_publisher(String, "transcripts", 10)
        self.get_logger().info("Riva ASR Node started")
        self.args = self.parse_args()
        self.auth = riva.client.Auth(
            self.args.ssl_cert,
            self.args.use_ssl,
            riva_config["RIVA_SPEECH_API_URL"],
            self.args.metadata,
        )
        self.asr_service = riva.client.ASRService(self.auth)
        self.input_device = self.select_input_device()
        self.config = self.create_asr_config()
        print(self.args)
        self.stream_and_publish()

    def parse_args(self):
        default_device_info = riva.client.audio_io.get_default_input_device_info()
        default_device_index = (
            None if default_device_info is None else default_device_info["index"]
        )
        parser = argparse.ArgumentParser()
        parser = add_asr_config_argparse_parameters(parser, profanity_filter=True)
        parser = add_connection_argparse_parameters(parser)
        parser.add_argument("--sample-rate-hz", type=int, default=16000)
        parser.add_argument("--file-streaming-chunk", type=int, default=1600)
        parser.add_argument("--input-device", type=int, default=default_device_index)
        return parser.parse_args([])  # Override with `[]` for ROS-safe run

    def select_input_device(self):
        input_device = 0
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info["maxInputChannels"] < 1:
                continue
            if "webcam" in info["name"].lower() or "default" in info["name"].lower():
                input_device = info["index"]
                break
        p.terminate()
        return input_device

    def create_asr_config(self):
        config = riva.client.StreamingRecognitionConfig(
            config=riva.client.RecognitionConfig(
                encoding=riva.client.AudioEncoding.LINEAR_PCM,
                language_code=riva_config["LANGUAGE_CODE"],
                max_alternatives=1,
                profanity_filter=self.args.profanity_filter,
                enable_automatic_punctuation=asr_config["ENABLE_AUTOMATIC_PUNCTUATION"],
                verbatim_transcripts=asr_config["VERBATIM_TRANSCRIPTS"],
                sample_rate_hertz=self.args.sample_rate_hz,
                audio_channel_count=1,
            ),
            interim_results=True,
        )
        return config

    def filtered_audio_chunks(self, audio_chunk_iterator, check_playing_fn):
        for chunk in audio_chunk_iterator:
            if not check_playing_fn():  # Only yield if audio is not playing
                yield chunk

    def stream_and_publish(self):
        with riva.client.audio_io.MicrophoneStream(
            self.args.sample_rate_hz,
            self.args.file_streaming_chunk,
            device=self.input_device,
        ) as audio_chunk_iterator:

            responses = self.asr_service.streaming_response_generator(
                audio_chunks=self.filtered_audio_chunks(
                    audio_chunk_iterator, self.is_audio_playing
                ),
                streaming_config=self.config,
            )
            for response in responses:
                if not response.results:
                    continue
                for result in response.results:
                    if not result.alternatives:
                        continue
                    if result.is_final:
                        transcript = result.alternatives[0].transcript
                        self.get_logger().info(f"Transcript: {transcript}")
                        msg = String()
                        msg.data = transcript
                        msg.data = f"{riva_config["LANGUAGE_CODE"]}:{transcript}"
                        self.publisher_.publish(msg)

    def is_audio_playing(self):

        if not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Playback status service unavailable.")
            return False  # Fail safe: assume not playing

        request = Trigger.Request()
        future = self.cli.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)

        if future.done():
            return future.result().success
        return False


def main(args=None):
    rclpy.init(args=args)
    node = RivaASRNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
