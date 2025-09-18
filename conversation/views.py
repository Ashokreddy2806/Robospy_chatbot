import os
from datetime import datetime
import json
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Import your services and models
from . import llm_service, text_analysis
from .models import Scene
from .tasks import generate_image_for_scene
import litellm


def file_count():
    """Checks for saved_chats folder and counts files."""
    folder_path = os.path.join(settings.BASE_DIR, 'saved_chats')
    os.makedirs(folder_path, exist_ok=True)
    try:
        file_count = sum(
            1 for entry in os.scandir(folder_path) if entry.is_file()
        )
    except FileNotFoundError:
        file_count = 0
    return file_count

def index(request):
    files = file_count()
    context = {
        "file_count": files,
    }
    return render(request, 'index.html', context)

def dashboard(request):
    t = text_analysis.TextAnalyzer()
    stats = t.get_stats()
    context = stats
    context["file_count"] = file_count()
    t.load_texts()
    return render(request, 'dashboard.html', context)

def list_prompt_files(request):
    prompt_dir = find("promptfiles")
    files = []
    if prompt_dir:
        for file in os.listdir(prompt_dir):
            if file.endswith(".txt") and "robopsy" in file:
                files.append(file)
    files.sort()
    return JsonResponse({"files": files})

def load_prompt(filename="promptsheet_robopsy_eng_limited.txt"):
    file_path = find(f"promptfiles/{filename}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Prompt file not found."

def get_log_file_path(request):
    if "chat_log_filename" not in request.session:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"chat_{timestamp}.txt"
        log_path = os.path.join(settings.BASE_DIR, "saved_chats", filename)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        request.session["chat_log_filename"] = log_path
    return request.session["chat_log_filename"]

def save_conversation(request, history):
    log_file = get_log_file_path(request)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n--- Robopsy-Chat at {} ---\n".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        for entry in history:
            role = entry.get("role", "unknown").upper()
            content = entry.get("content", "")
            f.write(f"{role}: {content}\n\n")

@csrf_exempt
def answer(request):
    data = json.loads(request.body)
    message = data.get("message", "")
    history = data.get("history", [])
    model = data.get("model", "openai/gpt-4o") # Or your mistral model

    prompt_file = data.get("prompt", "promptsheet_robopsy_eng_limited.txt")
    system_prompt = load_prompt(prompt_file)
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    if message.strip():
        messages.append({"role": "user", "content": message})

    save_conversation(request, history)

    try:
        response_object = litellm.completion(model=model, messages=messages, stream=False)
        bot_response_text = response_object.choices[0].message.content

        scene_title = f"Scene after user says: '{message[:30]}...'"
        new_scene = Scene.objects.create(
            title=scene_title,
            text_content=bot_response_text
        )
        print(f"Successfully created Scene with ID: {new_scene.id}")

        generate_image_for_scene.delay(new_scene.id)
        print(f"Celery task dispatched for Scene ID: {new_scene.id}")

        return JsonResponse({"response": bot_response_text, "scene_id": new_scene.id})

    except Exception as e:
        print(f"An error occurred calling the LLM or creating the scene: {e}")
        return JsonResponse({"error": "Failed to get a response from the model."}, status=500)


@csrf_exempt
def reset_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        raw_html = data.get("html", "")
        log_file_path = get_log_file_path(request)

        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("==== Final Chat Transcript ====\n")
            f.write(raw_html)

        request.session.pop("chat_log_filename", None)
        return JsonResponse({"status": "saved and reset"})

    return JsonResponse({"error": "Invalid method"}, status=400)


# --- THIS IS THE MISSING FUNCTION ---
def scene_view(request, scene_id):
    try:
        scene = Scene.objects.get(pk=scene_id)
    except Scene.DoesNotExist:
        return render(request, '404.html')

    return render(request, 'scene.html', {'scene': scene})