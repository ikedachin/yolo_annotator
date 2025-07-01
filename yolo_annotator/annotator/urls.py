from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'annotator'

urlpatterns = [
    path('', views.index, name='index'),
    path('annotate/<int:image_id>/', views.annotate, name='annotate'),
    path('api/save_annotations/<int:image_id>/', views.save_annotations, name='save_annotations'),
    path('api/load_images/', views.load_images, name='load_images'),
    path('api/split_dataset/', views.split_dataset, name='split_dataset'),
    path('api/add_label/', views.add_label, name='add_label'),
    path('api/delete_label/<int:label_id>/', views.delete_label, name='delete_label'),
    path('api/update_label/<int:label_id>/', views.update_label, name='update_label'),
    path('images/<str:filename>', views.serve_image, name='serve_image'),
]

# 開発環境での画像ファイル配信
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # base_images フォルダの画像を配信
    urlpatterns += static('/base_images/', document_root=settings.BASE_IMAGES_DIR)
