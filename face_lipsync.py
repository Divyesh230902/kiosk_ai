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
        "source_url": "https://tusker-baps-video-bucket.s3.ap-south-1.amazonaws.com/demo/shared_image.jpeg"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic MjAwMTAzMDYyMDMyQHNpbHZlcm9ha3VuaS5hYy5pbg:CRmIRXcHjx95qv2KovSYM'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_dict = eval(response.text)
    print(response.text)

    # Your code before the pause
    print("Starting process...")

    # Pause for 13 seconds
    time.sleep(13)

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