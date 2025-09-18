# helper_scripts/huggingface_service.py
'''import os
from huggingface_hub import InferenceClient
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import uuid

def generate_replicate_image(prompt: str, model: str) -> str | None:
    """
    Calls the Replicate provider via Hugging Face to generate an image from a text prompt.
    Saves the image to Django's media storage and returns the URL.
    """
    try:
        print(f"[HF SERVICE] Initializing client for model: {model}")
        client = InferenceClient(
            provider="replicate",
            model=model,
            token=os.getenv("HF_TOKEN"),
        )

        print(f"[HF SERVICE] Sending prompt to Replicate: '{prompt[:50]}...'")
        # Use text_to_image for generating from a prompt
        pil_image = client.text_to_image(prompt)

        # Save the returned image and get its URL
        image_format = 'PNG'
        file_name = f'scenes/{uuid.uuid4()}.png'
        
        image_file = ContentFile(b'')
        pil_image.save(image_file, format=image_format)

        path = default_storage.save(file_name, image_file)
        image_url = default_storage.url(path)
        
        print(f"[HF SERVICE] Success! Image saved at URL: {image_url}")
        return image_url

    except Exception as e:
        print(f"[HF SERVICE ERROR] An error occurred: {e}")
        return None'''