import requests
from PIL import Image
import time
import os
from dotenv import load_dotenv

#%%
def generate_image_from_text(api_key, text_prompts, output_path_images, image_name):
    url = f"https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*"  # "application/json"
    }

    body = {
        "prompt": text_prompts,
        "style_preset": "cinematic",
        "output_format": "png",
    }

    response = requests.post(url, headers=headers, files={"none": ''}, data=body, )

    # image_path = os.path.join(output_directory, f'{book_name}.png')

    file_name_path = f"{output_path_images}{image_name}.png"

    if response.status_code == 200:
        with open(file_name_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(str(response.json()))

    return file_name_path


#%%
def resize_image(input_path, width=768, height=768):
    # Load the image
    img = Image.open(input_path)

    # Resize the image
    img_resized = img.resize((width, height))

    # Save the resized image
    img_resized.save(input_path)


#%%
def get_generation_id(api_key, image_path, cfg_scale, motion_bucket_id):
    """
    cfg_scale [1, 10]: How strongly the video sticks to the original image. Use lower values to allow the model more freedom to make changes and higher values to correct motion distortions.

    motion_bucket_id [1, 255]: Lower values generally result in less motion in the output video, while higher values generally result in more motion.
    """

    url = f"https://api.stability.ai/v2beta/image-to-video"

    headers = {"authorization": f"Bearer {api_key}"}

    file = {"image": open(image_path, "rb")}

    data = {
        "seed": 0,
        "cfg_scale": cfg_scale,
        "motion_bucket_id": motion_bucket_id
    }

    response = requests.post(url, headers=headers, files=file, data=data, )

    return response.json().get('id')


#%%

def download_generated_video(api_key, generation_id, output_path_video, video_name, retries=6, wait_time=10):

    """
    :param api_key:
    :param generation_id:
    :param output_path_video:
    :param video_name:
    :param retries:
    :param wait_time: Should be around 30 seconds
    :return:
    """
    url = f"https://api.stability.ai/v2beta/image-to-video/result/{generation_id}"

    headers = {
        'accept': "video/*",  # Use 'application/json' to receive base64 encoded JSON
        'authorization': f"Bearer {api_key}"
    }

    file_name_path = f"{output_path_video}{video_name}.mp4"

    for attempt in range(retries):
        response = requests.request("GET", url, headers=headers)  # , timeout=(5, 14)

        if response.status_code == 200:
            print("Generation complete!")
            with open(file_name_path, 'wb') as file:
                file.write(response.content)
            return  # Success, exit the loop

        elif response.status_code == 202:
            print(f"Generation in-progress, retrying attempt {attempt + 1} of {retries} in {wait_time} seconds.")
            time.sleep(wait_time)
        else:
            raise Exception(str(response.json()))

    raise Exception("Failed to download video after all retries.")


#%%

def generate_and_download_video(stability_api_key: str, text_prompts: str, book_name: str, output_path_images: str, output_path_video:str, cfg_scale: float, motion_bucket_id: float) -> None:
    """
    Generate an image and animate it via Stability AI API.
    Creates folder "book_name" with "book_name/Images" and "book_name/Videos".
    Stores created images and animation to corresponding folders.

    :param stability_api_key: Stability AI API key
    :param text_prompts: Text to generate image from (e.g. text_prompts = [ prompt_1, prompt_2, ...])

    :param book_name:

    :param output_path_video:
    :param output_path_images:

    :param cfg_scale: [1, 10] How strongly the video sticks to the original image.
    Use lower values to allow the model more freedom to make changes and higher values to correct motion distortions.

    :param motion_bucket_id: [1, 255] Lower values generally result in less motion in the output video, while higher
    values generally result in more motion.

    Note: ----- - Make sure to create .env file in the main directory where you create a string variable "API_KEY"
    with your actual Stability AI API key.
    """
    #
    # os.makedirs(output_path_images, exist_ok=True)
    #
    # os.makedirs(output_path_video, exist_ok=True)

    image_name = generate_image_from_text(stability_api_key, text_prompts, output_path_images, book_name)

    resize_image(image_name, width=768, height=768)

    video_id = get_generation_id(stability_api_key, image_name, cfg_scale, motion_bucket_id)

    download_generated_video(stability_api_key, video_id, output_path_video, book_name)

#%%
