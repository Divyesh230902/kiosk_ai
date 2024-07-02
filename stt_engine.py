import speech_recognition as sr
import sounddevice as sd
import scipy.io.wavfile as wav
import streamlit as st


def record_and_transcribe_audio():
    recognizer = sr.Recognizer()
    duration = 6
    sample_rate = 16000

    with st.spinner("Listening..."):
        try:
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
            sd.wait()  # Wait until the recording is finished
            wav.write("output.wav", sample_rate, recording)  # Save the recording as a WAV file

            with sr.AudioFile("output.wav") as source:
                audio = recognizer.record(source)
                query = recognizer.recognize_google(audio)
                st.success(f"Your Question: {query}")
                return query
        except sr.UnknownValueError:
            st.error("Sorry, I did not understand that.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")

    return None






# def record_and_transcribe_audio():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         recognizer.adjust_for_ambient_noise(source, duration=1)
#         with st.spinner("Listening..."):
#             try:
#                 audio = recognizer.listen(source, phrase_time_limit=7)
#                 query = recognizer.recognize_google(audio)
#                 st.success(f"Your Question: {query}")
#                 return query
#             except sr.UnknownValueError:
#                 st.error("Sorry, I did not understand that.")
#             except sr.RequestError as e:
#                 st.error(f"Could not request results; {e}")
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")
#     return None





# import streamlit as st
# from streamlit_mic_recorder import speech_to_text


# def record_and_transcribe_audio():
#     with st.spinner("Listening..."):
#         text = speech_to_text(
#             language='en',
#             start_prompt="Start recording",
#             stop_prompt="Stop recording",
#             just_once=False,
#             use_container_width=False,
#             callback=None,
#             args=(),
#             kwargs={},
#             key=None
#         )
#         st.success(f"Your Question: {text}")
#         return text




