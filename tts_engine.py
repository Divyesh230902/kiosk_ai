# import pyttsx3
# import os
# from datetime import datetime
# from gtts import gTTS

# def speak(text):

#     output_dir = 'output/'
#     # Generate the file name with the current date and time
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     file_name = f"{output_dir}response_{timestamp}.mp3"
#     # file_path = os.path.join(output_dir, file_name)
#     file_path = os.path.abspath(file_name)

#     tts = gTTS(text,lang="en")
#     tts.save(file_path)
#     return file_name

# def speak(text):
#     output_dir = 'output/'
#     # Generate the file name with the current date and time
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     file_name = f"response_{timestamp}.mp3"
#     file_path = os.path.join(output_dir, file_name)

#     # Initialize the TTS engine
#     engine = pyttsx3.init()

#     # Save the speech to a file
#     engine.save_to_file(text, file_path)

#     # Run the engine
#     engine.runAndWait()

#     return file_path

from TTS.api import TTS
from datetime import datetime
import os
from scipy.io import wavfile
import noisereduce as nr


def speak(text):
    # Initialize TTS model
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    output_dir = 'output/'
#    Generate the file name with the current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{output_dir}response_{timestamp}.mp3"
    # file_path = os.path.join(output_dir, file_name)
    file_path = os.path.abspath(file_name)

    # Generate speech to file
    output_path = "output.wav"
    rate, data = wavfile.read(output_path)

    # Perform noise reduction
    reduced_noise = nr.reduce_noise(y=data, sr=rate)

    # Write noise-reduced audio to file
    output_reduced_noise_path = "output_reduced_noise.wav"
    wavfile.write(output_reduced_noise_path, rate, reduced_noise)
    tts.tts_to_file(text=text, file_path=file_path,
                    speaker_wav=output_reduced_noise_path, language="hi", split_sentences=True)
    return file_path


# Example usage
if __name__ == "__main__":
    speak(text="It took me quite a long time to develop a voice, and now that I have it I'm not going to be silent.")
