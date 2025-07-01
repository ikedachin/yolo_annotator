from django.db import models
import os
from PIL import Image


class Label(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#FF0000')  # Hex color for display
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ImageFile(models.Model):
    filename = models.CharField(max_length=255, unique=True)
    width = models.IntegerField()
    height = models.IntegerField()
    is_annotated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.filename
    
    @property
    def file_path(self):
        from django.conf import settings
        return os.path.join(settings.BASE_IMAGES_DIR, self.filename)
    
    def get_image_dimensions(self):
        try:
            with Image.open(self.file_path) as img:
                return img.size
        except Exception:
            return (0, 0)


class Annotation(models.Model):
    image = models.ForeignKey(ImageFile, on_delete=models.CASCADE, related_name='annotations')
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    x_center = models.FloatField()  # YOLO format: center x normalized (0-1)
    y_center = models.FloatField()  # YOLO format: center y normalized (0-1)
    width = models.FloatField()     # YOLO format: width normalized (0-1)
    height = models.FloatField()    # YOLO format: height normalized (0-1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.image.filename} - {self.label.name}"
    
    def to_yolo_format(self):
        """Convert to YOLO format string"""
        return f"{self.label.id} {self.x_center} {self.y_center} {self.width} {self.height}"
