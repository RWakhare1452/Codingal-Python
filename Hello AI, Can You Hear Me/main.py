import threading
import time
import sys
import wave
from datetime import datetime
import pyaudio
import numpy as np
import speech_recognition as sr
from speech_recognition import AudioData
import matplotlib.pyplot as plt

class AudioRecorder:
    def __init__(self, rate=16000, channels=1, chunk=1024):
        self.rate = rate
        self.channels = channels
        self.chunk = chunk
        self.format = pyaudio.paInt16
        self.stop_event = threading.Event()
        self.frames = []

    def _wait_for_enter(self):
        input("Press Enter to stop recording...\n")
        self.stop_event.set()

    def _show_spinner(self):
        spinner = ['|', '/', '-', '\\']
        idx = 0
        while not self.stop_event.is_set():
            sys.stdout.write(f"\rRecording... {spinner[idx % len(spinner)]}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
        sys.stdout.write("\rRecording stopped.          \n")
        sys.stdout.flush()

    def record(self):
        p = pyaudio.PyAudio()

        try:
            stream = p.open(format=self.format,
                            channels=self.channels,
                            rate=self.rate,
                            input=True,
                            frames_per_buffer=self.chunk)

            threading.Thread(target=self._wait_for_enter, daemon=True).start()
            threading.Thread(target=self._show_spinner, daemon=True).start() 

            while not self.stop_event.is_set():
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)

                except Exception as e:
                    print(f"\nError while recording: {e}")
                    break

            stream.stop_stream()
            stream.close()
            sample_width = p.get_sample_size(self.format)

        except Exception as e:
            print(f"Error initializing audio stream: {e}")
            return None, None, None

        finally:
            p.terminate()

        audio_data = b''.join(self.frames)
        return audio_data, sample_width, self.rate
    

class AudioProcessor:
    @staticmethod
    def save_audio(data, rate, width, filename):
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(width)
                wf.setframerate(rate)
                wf.writeframes(data)
            print(f"✅ Audio saved to {filename}")
            return True

        except Exception as e:
            print(f"Error saving audio: {e}")
            return False

    @staticmethod
    def transcribe_audio(data, rate, width, filename="transcript.txt"):
        recognizer = sr.Recognizer()
        audio = AudioData(data, rate, width)

        print("Transcribing audio...")
        try:
            text = recognizer.recognize_google(audio)
            print(f"\n{'='*60}")
            print("TRANSCRIPTION:")
            print(f"{'='*60}")
            print(text)
            print(f"{'='*60}\n")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ Transcript saved to {filename}")
            return text

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None

    @staticmethod
    def show_waveform(data, rate, save_plot=False):
        try:
            samples = np.frombuffer(data, dtype=np.int16)
            time_axis = np.linspace(0, len(samples) / rate, num=len(samples))

            plt.figure(figsize=(12, 4))
            plt.plot(time_axis, samples, linewidth=0.5)
            plt.title("Audio Waveform", fontsize=16, fontweight='bold')
            plt.xlabel("Time (s)", fontsize=14)
            plt.ylabel("Amplitude", fontsize=14)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            if save_plot:
                try:
                    img_filename = f"waveform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    plt.savefig(img_filename)
                    print(f"✅ Waveform image saved to {img_filename}")
                except Exception as e:
                    print(f"Error saving waveform image: {e}")
            else:
                try:
                    plt.show()
                except Exception:
                    # In headless environments plt.show() may fail — save to a file instead
                    img_filename = f"waveform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    try:
                        plt.savefig(img_filename)
                        print(f"✅ Waveform image saved to {img_filename}")
                    except Exception as e:
                        print(f"Could not display or save waveform: {e}")

        except Exception as e:
            print(f"Error plotting waveform: {e}")
            return False

        return True


if __name__ == "__main__":
    recorder = AudioRecorder()

    print("Press Enter to start recording...")
    input()
    print("Recording started. Press Enter to stop.")

    data, width, rate = recorder.record()
    if data is None:
        print("Recording failed or could not access audio device.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    wav_filename = f"recording_{timestamp}.wav"
    AudioProcessor.save_audio(data, rate, width, wav_filename)

    transcript_filename = f"transcript_{timestamp}.txt"
    AudioProcessor.transcribe_audio(data, rate, width, filename=transcript_filename)

    show_now = input("Show waveform now? (y/N): ").strip().lower() == 'y'
    if show_now:
        AudioProcessor.show_waveform(data, rate, save_plot=False)
    else:
        save_plot = input("Save waveform image instead? (y/N): ").strip().lower() == 'y'
        if save_plot:
            AudioProcessor.show_waveform(data, rate, save_plot=True)

    print("Done.")
