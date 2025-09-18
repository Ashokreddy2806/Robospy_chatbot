# helper_scripts/flux_service.py
''' import requests
import os
from dotenv import load_dotenv

# Directly load the .env file from the project root
load_dotenv()

def generate_flux_image(prompt: str) -> str | None:
    """
    Calls the FLUX API to generate an image.
    """
    print("  [FLUX SERVICE] Reached generate_flux_image function.")
    # Read variables directly from the environment
    api_endpoint = os.getenv('FLUX_API_ENDPOINT')
    api_key = os.getenv('FLUX_API_KEY')

    if not api_endpoint or not api_key:
        print("  [FLUX SERVICE ERROR] FLUX_API_ENDPOINT or FLUX_API_KEY not found in .env file.")
        return None
    
    print(f"  [FLUX SERVICE INFO] Endpoint: {api_endpoint}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "prompt": prompt,
    }

    try:
        print("  [FLUX SERVICE INFO] Sending POST request to FLUX API...")
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=180)
        response.raise_for_status()

        # NOTE: The API response key might be different. 
        # Check the Flux documentation. Common patterns are 'url' or 'image_url'.
        # This code checks for a few common patterns.
        json_response = response.json()
        image_url = json_response.get('image_url') or json_response.get('url')
        if not image_url and 'data' in json_response and len(json_response['data']) > 0:
            image_url = json_response['data'][0].get('url')

        if image_url:
            print(f"  [FLUX SERVICE SUCCESS] Received image URL: {image_url}")
            return image_url
        else:
            print(f"  [FLUX SERVICE ERROR] API response did not contain a recognizable image URL. Response: {response.text}")
            return None

    except requests.exceptions.HTTPError as e:
        print(f"  [FLUX SERVICE HTTP ERROR] The API returned an error status code: {e.response.status_code}")
        print(f"  [FLUX SERVICE HTTP ERROR] Response body: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  [FLUX SERVICE REQUEST ERROR] An error occurred while calling the API: {e}")
        return None '''