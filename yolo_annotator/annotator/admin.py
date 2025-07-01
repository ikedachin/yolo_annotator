from django.contrib import admin
from .models import Label, ImageFile, Annotation


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'width', 'height', 'is_annotated', 'created_at')
    list_filter = ('is_annotated', 'created_at')
    search_fields = ('filename',)
    readonly_fields = ('width', 'height', 'created_at', 'updated_at')


@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('image', 'label', 'x_center', 'y_center', 'width', 'height', 'created_at')
    list_filter = ('label', 'created_at')
    search_fields = ('image__filename', 'label__name')
    readonly_fields = ('created_at', 'updated_at')
