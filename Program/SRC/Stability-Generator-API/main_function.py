import requests
import os
import base64
from PIL import Image
from dotenv import load_dotenv
from requests.exceptions import HTTPError


def generate_image_from_text(text_prompts, output_directory, book_name):
    load_dotenv()

    api_key = os.getenv("STABILITY_API_KEY")

    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    # Swapped body for data
    data = {
        "steps": 40,
        "width": 1024,
        "height": 1024,
        "seed": 0,
        "cfg_scale": 5,
        "samples": 1,
        "style_preset": "cinematic",
        "text_prompts": text_prompts,
    }

    headers = {
        "Accept": "application/json",
        # "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    response = requests.post(url, headers=headers, data=data)  # Can be a json=

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    for i, image in enumerate(data["artifacts"]):
        image_path = os.path.join(output_directory, f'{book_name}_{image["seed"]}.png')
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image["base64"]))

    return image_path


#%%
def resize_image(input_path, width=768, height=768):
    # Load the image
    img = Image.open(input_path)

    # Resize the image
    img_resized = img.resize((width, height))

    # Save the resized image
    img_resized.save(input_path)


#%%
def get_generation_id(api_key, image_path):
    url = "https://api.stability.ai/v2alpha/generation/image-to-video"

    headers = {"authorization": f"Bearer {api_key}"}

    files = {"image": open(image_path, "rb")}

    data = {
        "seed": 0,
        "cfg_scale": 1.8,
        "motion_bucket_id": 127
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        generation_id = response.json().get('id')
        print("Generation ID:", generation_id)
        return generation_id
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


#%%
def download_generated_video(api_key, generation_id, output_path):
    url = f"https://api.stability.ai/v2alpha/generation/image-to-video/result/{generation_id}"

    headers = {
        'Accept': "video/*",  # Use 'application/json' to receive base64 encoded JSON
        'authorization': f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 202:
        print("Generation in-progress, try again in 10 seconds.")
    elif response.status_code == 200:
        print("Generation complete!")
        with open(output_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(str(response.json()))


#%%
def generate_and_download_video(api_key, image_path):
    image_name = os.path.basename(image_path)
    output_path = f"Videos/{image_name}.mp4"
    generation_id = get_generation_id(api_key, image_path)

    if generation_id:
        download_generated_video(api_key, generation_id, output_path)

#%%
