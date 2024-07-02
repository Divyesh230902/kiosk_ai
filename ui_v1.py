import streamlit as st
import llm
from tts_engine import speak
import os
import speech_recognition as sr
import sounddevice as sd
import random
import scipy.io.wavfile as wav
from face_lipsync import download_video_from_api

# Constants
USERNAME = "admin"
PASSWORD = "admin"
FUN_FACTS = [
    "The university hosts an annual cultural fest entitled 'Junoon' of 4-5 days having more than 200 performances in each day.",
    "Silver Oak University has a strong alumni network with graduates working in top companies worldwide and often they are invited to campus to guide the students.",
    "The university offers over 15 different clubs and organizations for students to join for 360 degree development.",
    "Silver Oak University has an AI-powered campus with numerous student projects. This AI system is one example of AI projects which makes Silver Oak University an AI Hub for the students.",
    "Silver Oak University has an International Organization entitled 'IEEE STUDENT BRANCH' which is Region 10's (i.e Asia-pacific) Outstanding Student Branch."
]

def record_and_transcribe_audio():
    recognizer = sr.Recognizer()
    duration = 7
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
        except Exception as e:
            st.error(f"An error occurred while recording and transcribing audio: {e}")

    return None

# Streamlit page configuration
st.set_page_config(page_title="SOU AI", page_icon='assets/Silver Oak University (Favicon).svg')

def show_fun_fact():
    st.write("Until the response is being generated, I think you should know this fact below:")
    st.info(random.choice(FUN_FACTS))

def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

def trim_response(response):
    words = response.split()
    if len(words) > 60:
        trimmed_response = ' '.join(words[:60])
        last_period = trimmed_response.rfind('.')
        if last_period != -1:
            trimmed_response = trimmed_response[:last_period + 1]
        else:
            trimmed_response += '...'
        trimmed_response += " For more information kindly scan the below QR code and explore the university's website."
        return trimmed_response
    return response

def handle_response_generation(text, response_type):
    if text:
        show_fun_fact()
        with st.spinner("Generating response..."):
            try:
                chatbot = llm.UniversityChatbot()
                response = chatbot.chat(text)

                if response_type == "Text":
                    trimmed_response = trim_response(response)
                    st.success("Response generated!")  # Show success message for text response
                    st.write(f"Response: {trimmed_response}")
                    if len(response.split()) > 60:
                        st.image("assets/qr-code.png", width=200)

                elif response_type == "Audio":
                    try:
                        trimmed_response = trim_response(response)
                        # Convert the response to speech and save it as an audio file
                        audio_file_path = speak(trimmed_response)
                        if audio_file_path:
                            st.success("Response generated!")  # Show success when audio is ready
                            # Play the audio file using Streamlit
                            with open(audio_file_path, "rb") as f:
                                audio_bytes = f.read()
                                st.audio(audio_bytes, format="audio/mp3", autoplay=True)

                            # Wait for the audio to finish playing before showing the response text
                            st.write(f"Response: {trimmed_response}")
                            if len(response.split()) > 60:
                                st.image("assets/qr-code.png", width=200)
                    except Exception as e:
                        st.error(f"An error occurred while generating audio: {e}")

                elif response_type == "Video":
                    try:
                        trimmed_response = trim_response(response)
                        # Convert the response to a video
                        video_file_path = download_video_from_api(trimmed_response)
                        if os.path.exists(video_file_path):
                            st.success("Response generated!")  # Show success when video is ready
                            # Play the video file using Streamlit
                            st.video(video_file_path, autoplay=True)

                            # Wait for the video to finish playing before showing the response text
                            st.write(f"Response: {trimmed_response}")
                            if len(response.split()) > 60:
                                st.image("assets/qr-code.png", width=200)
                        else:
                            st.error(f"An error occurred while generating video: {video_file_path}")
                    except Exception as e:
                        st.error(f"An error occurred while generating video: {e}")

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")

# Main application
def main():
    st.sidebar.image("assets/Silver Oak University.svg", width=300)
    st.markdown('<style>button[title="View fullscreen"]{visibility: hidden;}</style>', unsafe_allow_html=True)
    st.title("Silver Oak University's AI Assistant")
    st.header("AI Is Here To Provide You Information")

    # Sidebar options
    st.sidebar.title("AI Configurations")
    input_mode = st.sidebar.radio("Select Input Mode", ('Voice', 'Text'))
    response_type = st.sidebar.radio("Select Response Type", ('Text', 'Audio', 'Video'))

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    if input_mode == 'Voice':
        st.write("Click the button below for your questions")
        if st.button("Start Asking", key="ask_button"):
            text = record_and_transcribe_audio()
            if text:
                handle_response_generation(text, response_type)
    else:
        user_input = st.text_input("Enter your question:")
        if st.button("Submit"):
            if user_input:
                handle_response_generation(user_input, response_type)

# Authentication page
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Check login state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main()
else:
    login()