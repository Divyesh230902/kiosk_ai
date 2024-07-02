import requests
import json
import time
import os
from datetime import datetime
import subprocess

def download_video_from_api(input_text):
    print("Face API Invoked")
    # Calling POST request
    url = "https://api.d-id.com/talks"
    payload = json.dumps({
        "script": {
            "type": "text",
            "input": input_text
        },
        "source_url": "https://cdn.pixabay.com/photo/2023/04/02/11/19/ai-generated-7894413_1280.jpg"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic MjAwMTAzMDYyMDIwQHNpbHZlcm9ha3VuaS5hYy5pbg:5RKXYBDYLFHg8s5uYyCSB'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_dict = eval(response.text)
    print(response.text)

    # Your code before the pause
    print("Starting process...")

    # Pause for 13 seconds
    time.sleep(10)

    # Your code after the pause
    print("Resuming next process...")

    # Calling GET request
    url = url + "/" + response_dict["id"]
    response1 = requests.request("GET", url, headers=headers, data=payload)
    print(response1.text)

    # Parse the JSON response to extract data
    response1_dict = json.loads(response1.text)

    # Check if the expected key exists in the response dictionary
    if "result_url" in response1_dict:
        result_url = response1_dict["result_url"]

        output_folder = 'output'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Generate filename with current date and time
        current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_filename = os.path.join(output_folder, f"video_{current_datetime}.mp4")

        # Downloading the video using FFmpeg
        subprocess.run(["ffmpeg", "-i", result_url, "-c", "copy", output_filename])

        print("File downloaded successfully and saved as", output_filename)
        return output_filename

# Example usage
downloaded_video = download_video_from_api('''Sure, here are the benefits of studying in Silver Oak University:

 Affordable education: The university offers various scholarship programs and financial
aid options to make education accessible.
 Diverse and vibrant student community: Students from all walks of life come together to
 create a friendly and inclusive environment.
 Handson learning: Silver Oak University emphasizes practical learning, giving students
the opportunity to apply their knowledge in realworld situations.''')
print("Downloaded video path:", downloaded_video)
