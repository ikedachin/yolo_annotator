from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
import json
import shutil
import random
import mimetypes
from .models import ImageFile, Label, Annotation


def index(request):
    """画像一覧ページ"""
    images = ImageFile.objects.all().order_by('filename')
    labels = Label.objects.all()
    return render(request, 'annotator/index.html', {
        'images': images,
        'labels': labels
    })


def annotate(request, image_id):
    """アノテーション画面"""
    image = get_object_or_404(ImageFile, id=image_id)
    labels = Label.objects.all()
    annotations = Annotation.objects.filter(image=image)
    
    # 次の画像を取得
    next_image = ImageFile.objects.filter(id__gt=image_id).first()
    
    return render(request, 'annotator/annotate.html', {
        'image': image,
        'labels': labels,
        'annotations': annotations,
        'next_image': next_image
    })


@csrf_exempt
@require_http_methods(["POST"])
def save_annotations(request, image_id):
    """アノテーションデータを保存"""
    image = get_object_or_404(ImageFile, id=image_id)
    
    try:
        data = json.loads(request.body)
        annotations_data = data.get('annotations', [])
        
        # 既存のアノテーションを削除
        Annotation.objects.filter(image=image).delete()
        
        # 新しいアノテーションを保存
        for ann_data in annotations_data:
            label = get_object_or_404(Label, id=ann_data['label_id'])
            Annotation.objects.create(
                image=image,
                label=label,
                x_center=ann_data['x_center'],
                y_center=ann_data['y_center'],
                width=ann_data['width'],
                height=ann_data['height']
            )
        
        # 画像をアノテーション済みにマーク
        image.is_annotated = True
        image.save()
        
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def load_images(request):
    """base_imagesフォルダから画像を読み込み"""
    try:
        base_images_dir = settings.BASE_IMAGES_DIR
        if not os.path.exists(base_images_dir):
            os.makedirs(base_images_dir)
            return JsonResponse({'status': 'error', 'message': 'base_imagesフォルダが見つかりません'})
        
        # 画像ファイルを検索
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        image_files = [f for f in os.listdir(base_images_dir) 
                      if f.lower().endswith(image_extensions)]
        
        created_count = 0
        for filename in image_files:
            if not ImageFile.objects.filter(filename=filename).exists():
                filepath = os.path.join(base_images_dir, filename)
                try:
                    from PIL import Image
                    with Image.open(filepath) as img:
                        width, height = img.size
                    
                    ImageFile.objects.create(
                        filename=filename,
                        width=width,
                        height=height
                    )
                    created_count += 1
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        return JsonResponse({
            'status': 'success', 
            'message': f'{created_count}個の新しい画像を読み込みました'
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def split_dataset(request):
    """データセットをtrain/validに分割"""
    try:
        data = json.loads(request.body)
        split_ratio = float(data.get('split_ratio', 0.8))  # デフォルト8:2
        
        # アノテーション済みの画像のみを対象
        annotated_images = ImageFile.objects.filter(is_annotated=True)
        
        if not annotated_images.exists():
            return JsonResponse({'status': 'error', 'message': 'アノテーション済みの画像がありません'})
        
        # ランダムに分割
        images_list = list(annotated_images)
        random.shuffle(images_list)
        
        train_count = int(len(images_list) * split_ratio)
        train_images = images_list[:train_count]
        valid_images = images_list[train_count:]
        
        # ファイルをコピー
        for images, target_img_dir, target_label_dir in [
            (train_images, settings.TRAIN_IMAGES_DIR, settings.TRAIN_LABELS_DIR),
            (valid_images, settings.VALID_IMAGES_DIR, settings.VALID_LABELS_DIR)
        ]:
            os.makedirs(target_img_dir, exist_ok=True)
            os.makedirs(target_label_dir, exist_ok=True)
            
            for image in images:
                # 画像ファイルをコピー
                src_img = os.path.join(settings.BASE_IMAGES_DIR, image.filename)
                dst_img = os.path.join(target_img_dir, image.filename)
                shutil.copy2(src_img, dst_img)
                
                # ラベルファイルを作成
                label_filename = os.path.splitext(image.filename)[0] + '.txt'
                label_path = os.path.join(target_label_dir, label_filename)
                
                with open(label_path, 'w') as f:
                    annotations = Annotation.objects.filter(image=image)
                    for ann in annotations:
                        f.write(ann.to_yolo_format() + '\n')
        
        return JsonResponse({
            'status': 'success',
            'message': f'データセットを分割しました (train: {len(train_images)}, valid: {len(valid_images)})'
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def add_label(request):
    """ラベルを追加"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        color = data.get('color', '#FF0000')
        
        if not name:
            return JsonResponse({'status': 'error', 'message': 'ラベル名が必要です'})
        
        if Label.objects.filter(name=name).exists():
            return JsonResponse({'status': 'error', 'message': 'このラベル名は既に存在します'})
        
        label = Label.objects.create(name=name, color=color)
        
        return JsonResponse({
            'status': 'success',
            'label': {
                'id': label.id,
                'name': label.name,
                'color': label.color
            }
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def delete_label(request, label_id):
    """ラベルを削除"""
    try:
        label = get_object_or_404(Label, id=label_id)
        
        # このラベルを使用しているアノテーションがあるかチェック
        annotation_count = Annotation.objects.filter(label=label).count()
        if annotation_count > 0:
            return JsonResponse({
                'status': 'error', 
                'message': f'このラベルは{annotation_count}個のアノテーションで使用されているため削除できません'
            })
        
        label_name = label.name
        label.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'ラベル「{label_name}」を削除しました'
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def update_label(request, label_id):
    """ラベルを更新"""
    try:
        label = get_object_or_404(Label, id=label_id)
        data = json.loads(request.body)
        
        name = data.get('name', '').strip()
        color = data.get('color', label.color)
        
        if not name:
            return JsonResponse({'status': 'error', 'message': 'ラベル名が必要です'})
        
        # 名前が変更されている場合、重複チェック
        if name != label.name and Label.objects.filter(name=name).exists():
            return JsonResponse({'status': 'error', 'message': 'このラベル名は既に存在します'})
        
        label.name = name
        label.color = color
        label.save()
        
        return JsonResponse({
            'status': 'success',
            'label': {
                'id': label.id,
                'name': label.name,
                'color': label.color
            }
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def serve_image(request, filename):
    """base_images フォルダから画像を配信"""
    print(f"=== 画像リクエスト受信: {filename} ===")
    
    try:
        file_path = os.path.join(settings.BASE_IMAGES_DIR, filename)
        print(f"ファイルパス: {file_path}")
        print(f"BASE_IMAGES_DIR: {settings.BASE_IMAGES_DIR}")
        
        if not os.path.exists(file_path):
            print(f"ファイルが見つかりません: {file_path}")
            raise Http404("画像が見つかりません")
        
        print(f"ファイル存在確認: OK")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        print(f"画像配信成功: {filename}, サイズ: {len(content)}, content-type: {content_type}")
        response = HttpResponse(content, content_type=content_type)
        response['Cache-Control'] = 'max-age=3600'  # 1時間キャッシュ
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    except Exception as e:
        print(f"画像配信エラー: {str(e)}")
        raise Http404(f"画像の読み込みに失敗しました: {str(e)}")
