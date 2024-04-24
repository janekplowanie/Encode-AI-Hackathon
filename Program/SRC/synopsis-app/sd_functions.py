import requests
import os
import base64
import time


def generate_image_from_text(api_key, text_prompts, output_directory, book_name):

    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    text_prompts_body = [{"text": text_prompts, "weight": 1}]

    body = {
        "steps": 40,
        "width": 1024,
        "height": 1024,
        "seed": 0,
        "cfg_scale": 5,
        "samples": 1,
        "style_preset": "cinematic",
        #         "style_preset": "3d-model",
        "text_prompts": text_prompts_body,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    image_path = ""
    for i, image in enumerate(data["artifacts"]):
        image_path = os.path.join(output_directory, f'{book_name}_{image["seed"]}.png')
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image["base64"]))
    return image_path


def resize_image(input_path, width=768, height=768):
    from PIL import Image

    # Load the image
    img = Image.open(input_path)

    # Resize the image
    img_resized = img.resize((width, height))

    # Save the resized image
    img_resized.save(input_path)


def get_generation_id(api_key, image_path, cfg_scale, motion_bucket_id):
    import requests

    url = "https://api.stability.ai/v2alpha/generation/image-to-video"

    headers = {"authorization": f"Bearer {api_key}"}

    files = {"image": open(image_path, "rb")}

    data = {"seed": 0, "cfg_scale": cfg_scale, "motion_bucket_id": motion_bucket_id}

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        generation_id = response.json().get("id")
        print("Generation ID:", generation_id)
        return generation_id
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def download_generated_video(api_key, generation_id, output_path):

    import requests
    from time import sleep

    url = f"https://api.stability.ai/v2alpha/generation/image-to-video/result/{generation_id}"

    headers = {
        "Accept": "video/*",  # Use 'application/json' to receive base64 encoded JSON
        "authorization": f"Bearer {api_key}",
    }

    response = requests.get(url, headers=headers)
    print("Response status:", response.status_code)
    while response.status_code != 200:
        if response.status_code == 202:
            print("Generation in-progress, try again in 5 seconds...")
            sleep(5)
            response = requests.get(url, headers=headers)

    print("Generation complete!")

    with open(output_path, "wb") as file:
        file.write(response.content)


def generate_and_download_video(
    videos_list_path, api_key, text_prompts, book_name, cfg_scale=1.8, motion_bucket_id=127
):
    """
        Generate image and animate it via Stability AI API.
        Creates folder "book_name" with "book_name/Images" and "book_name/Videos".
        Stores created images and animation to corresponding folders.

        api_key : Stability AI API key

        text_prompts : Text to generate image from (e.g text_prompts = [
                {"text": "Harry Potter shooting a gun","weight": 1},
                {"text": "blurry, bad", "weight": -1}, ])

        book_name : book name (e.g., book_name = "Harry")

        cfg_scale [1, 10]: How strongly the video sticks to the original image.
        Use lower values to allow the model more freedom to make changes and higher values to correct motion distortions.

        motion_bucket_id [1, 255]: Lower values generally result in less motion in the output video,
    while higher values generally result in more motion.
    """

    output_path_images = f"{book_name}/Images/"
    os.makedirs(output_path_images, exist_ok=True)

    image_path = generate_image_from_text(
        api_key, text_prompts, output_path_images, book_name
    )
    resize_image(image_path)
    image_name = os.path.basename(image_path)

    os.makedirs(videos_list_path, exist_ok=True)

    out_path_videos = f"{videos_list_path}/{os.path.basename(image_path)[:-4]}.mp4"
    generation_id = get_generation_id(api_key, image_path, cfg_scale, motion_bucket_id)

    if generation_id:
        download_generated_video(api_key, generation_id, out_path_videos)
    return out_path_videos
