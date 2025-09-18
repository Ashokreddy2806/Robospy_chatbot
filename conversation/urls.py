from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("answer/", views.answer, name="answer"),
    path("list_prompts/", views.list_prompt_files, name="list_prompts"),
    path('reset_chat/', views.reset_chat, name='reset_chat'),
    path('scenes/<int:scene_id>/', views.scene_view, name='scene-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)