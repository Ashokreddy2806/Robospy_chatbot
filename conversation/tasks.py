# conversation/tasks.py
from celery import shared_task
from .models import Scene
from helper_scripts.replicate_service import generate_replicate_image

@shared_task
def generate_image_for_scene(scene_id):
    try:
        scene = Scene.objects.get(pk=scene_id)
        prompt = scene.text_content
        
        # Use the correct, working model from your example
        model_to_use = "black-forest-labs/flux-dev"
        
        image_url = generate_replicate_image(prompt=prompt, model=model_to_use)
        
        if image_url:
            scene.image_url = image_url
            scene.save()
            print(f"Successfully generated and saved image for scene {scene_id}")
        else:
            print(f"Failed to generate image for scene {scene_id}")

    except Scene.DoesNotExist:
        print(f"Scene with ID {scene_id} not found.")