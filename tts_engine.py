import pyttsx3
import os
from datetime import datetime
from gtts import gTTS

def speak(text):

    output_dir = 'output/'
    # Generate the file name with the current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{output_dir}response_{timestamp}.mp3"
    # file_path = os.path.join(output_dir, file_name)
    file_path = os.path.abspath(file_name)

    tts = gTTS(text,lang="en")
    tts.save(file_path)
    return file_name

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


