# helper_scripts/replicate_service.py
import replicate

def generate_replicate_image(prompt: str, model: str) -> str | None:
    """
    Calls the official Replicate API to generate an image using the specified model.
    """
    try:
        print(f"[REPLICATE SERVICE] Calling Replicate API with model: {model}")
        
        input_data = {"prompt": prompt}
        
        output = replicate.run(model, input=input_data)
        
        # The output from Replicate for this model is a list of image URLs
        if output and isinstance(output, list) and len(output) > 0:
            image_url = output[0]
            print(f"[REPLICATE SERVICE] Success! Image URL: {image_url}")
            return image_url
        else:
            print(f"[REPLICATE SERVICE ERROR] API returned an unexpected output: {output}")
            return None

    except Exception as e:
        print(f"[REPLICATE SERVICE ERROR] An error occurred: {e}")
        return None