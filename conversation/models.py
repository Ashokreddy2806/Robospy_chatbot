from django.db import models

class Scene(models.Model):
    title = models.CharField(max_length=200)
    text_content = models.TextField()
    image_url = models.URLField(blank=True, null=True) # This will store the generated image URL
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title