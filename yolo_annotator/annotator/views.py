from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count
import os
import json
import shutil
import random
import mimetypes
from .models import ImageFile, Label, Annotation


def index(request):
    """画像一覧ページ"""
    images = ImageFile.objects.all().order_by('filename')
    
    # ラベルの使用回数を取得
    labels = Label.objects.annotate(usage_count=Count('annotation')).order_by('name')
    
    # アノテーション済み画像数を計算
    annotated_count = images.filter(is_annotated=True).count()
    
    return render(request, 'annotator/index.html', {
        'images': images,
        'labels': labels,
        'annotated_count': annotated_count
    })


def annotate(request, image_id):
    """アノテーション画面"""
    image = get_object_or_404(ImageFile, id=image_id)
    labels = Label.objects.all()
    annotations = Annotation.objects.filter(image=image)
    
    # 次の画像と前の画像を取得
    next_image = ImageFile.objects.filter(id__gt=image_id).first()
    prev_image = ImageFile.objects.filter(id__lt=image_id).order_by('-id').first()
    
    return render(request, 'annotator/annotate.html', {
        'image': image,
        'labels': labels,
        'annotations': annotations,
        'next_image': next_image,
        'prev_image': prev_image
    })


@csrf_exempt
@require_http_methods(["POST"]) # POSTリクエストのみを許可
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
    """データセットをtrain/validに分割し、学習用YAMLファイルを生成"""
    try:
        data = json.loads(request.body)
        split_ratio = float(data.get('split_ratio', 0.8))  # デフォルト8:2
        target_size = int(data.get('image_size', 640))  # デフォルト640x640
        
        # アノテーション済みの画像のみを対象
        annotated_images = ImageFile.objects.filter(is_annotated=True)
        
        if not annotated_images.exists():
            return JsonResponse({'status': 'error', 'message': 'アノテーション済みの画像がありません'})
        
        # 現在の日時を取得してフォルダ名に使用
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 日付付きの出力フォルダを作成
        dated_output_dir = settings.PROJECT_ROOT / 'output' / f'output_{timestamp}'
        train_images_dir = dated_output_dir / 'images' / 'train'
        valid_images_dir = dated_output_dir / 'images' / 'valid'
        train_labels_dir = dated_output_dir / 'labels' / 'train'
        valid_labels_dir = dated_output_dir / 'labels' / 'valid'
        
        # ランダムに分割
        images_list = list(annotated_images)
        random.shuffle(images_list)
        
        train_count = int(len(images_list) * split_ratio)
        train_images = images_list[:train_count]
        valid_images = images_list[train_count:]
        
        # 画像処理に必要なライブラリをインポート
        from PIL import Image, ImageOps
        
        # ファイルをコピー・リサイズ
        for images, target_img_dir, target_label_dir in [
            (train_images, train_images_dir, train_labels_dir),
            (valid_images, valid_images_dir, valid_labels_dir)
        ]:
            os.makedirs(target_img_dir, exist_ok=True)
            os.makedirs(target_label_dir, exist_ok=True)
            
            for image in images:
                # 画像ファイルを読み込み
                src_img_path = os.path.join(settings.BASE_IMAGES_DIR, image.filename)
                dst_img_path = os.path.join(target_img_dir, image.filename)
                
                # 画像をリサイズ・パディング
                with Image.open(src_img_path) as img:
                    # RGBに変換（必要に応じて）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    original_width, original_height = img.size
                    
                    # 画像をターゲットサイズに合わせてリサイズ（アスペクト比を保持）
                    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
                    resized_width, resized_height = img.size
                    
                    # 正方形のキャンバスを作成（白でパディング）
                    new_img = Image.new('RGB', (target_size, target_size), (255, 255, 255))
                    
                    # 画像をキャンバスの左上に配置
                    paste_x = 0
                    paste_y = 0
                    new_img.paste(img, (paste_x, paste_y))
                    
                    # リサイズした画像を保存
                    new_img.save(dst_img_path, quality=95)
                    
                    # スケール比とオフセットを計算
                    scale_x = resized_width / original_width
                    scale_y = resized_height / original_height
                    offset_x = paste_x / target_size
                    offset_y = paste_y / target_size
                
                # ラベルファイルを作成（座標を変換）
                label_filename = os.path.splitext(image.filename)[0] + '.txt'
                label_path = os.path.join(target_label_dir, label_filename)
                
                with open(label_path, 'w') as f:
                    annotations = Annotation.objects.filter(image=image)
                    for ann in annotations:
                        # 元の座標を取得
                        orig_x_center = ann.x_center
                        orig_y_center = ann.y_center
                        orig_width = ann.width
                        orig_height = ann.height
                        
                        # 元の画像サイズでの絶対座標に変換
                        abs_x_center = orig_x_center * original_width
                        abs_y_center = orig_y_center * original_height
                        abs_width = orig_width * original_width
                        abs_height = orig_height * original_height
                        
                        # リサイズ後の絶対座標に変換
                        new_abs_x_center = abs_x_center * scale_x + paste_x
                        new_abs_y_center = abs_y_center * scale_y + paste_y
                        new_abs_width = abs_width * scale_x
                        new_abs_height = abs_height * scale_y
                        
                        # 新しい画像サイズでの相対座標に変換
                        new_x_center = new_abs_x_center / target_size
                        new_y_center = new_abs_y_center / target_size
                        new_width = new_abs_width / target_size
                        new_height = new_abs_height / target_size
                        
                        # 座標が範囲内に収まるようにクリップ
                        new_x_center = max(0, min(1, new_x_center))
                        new_y_center = max(0, min(1, new_y_center))
                        new_width = max(0, min(1, new_width))
                        new_height = max(0, min(1, new_height))
                        
                        # YOLO形式で出力
                        f.write(f"{ann.label.id} {new_x_center:.6f} {new_y_center:.6f} {new_width:.6f} {new_height:.6f}\n")
        
        # YAMLファイルを生成（日付付きフォルダ内に）
        yaml_dir = dated_output_dir
        os.makedirs(yaml_dir, exist_ok=True)
        
        # ファイル名に日時を含める
        yaml_filename = f"dataset_{target_size}x{target_size}_{timestamp}.yaml"
        yaml_path = os.path.join(yaml_dir, yaml_filename)
        
        # ラベルの情報を取得
        all_labels = Label.objects.all().order_by('id')
        label_names = {label.id: label.name for label in all_labels}
        
        # データセットのルートパスを日付付きフォルダからの相対パスで設定
        # データセットのルートパスはmanage.pyからの相対パスで設定
        dataset_root = f"../output/output_{timestamp}"
        
        # YAMLファイルの内容を作成
        yaml_content = f"""# Train/val/test sets as 1) dir: path/to/imgs, 2) file: path/to/imgs.txt, or 3) list: [path/to/imgs1, path/to/imgs2, ..]
path: {dataset_root} # dataset root dir
train: images/train # train images
val: images/valid # val images
test: # test images (optional)

# Classes
names:
"""
        
        # クラス名の部分を追加
        for label_id, label_name in label_names.items():
            yaml_content += f"  {label_id}: {label_name}\n"
        
        # YAMLファイルを保存
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        return JsonResponse({
            'status': 'success',
            'message': f'データセットを分割しました (train: {len(train_images)}, valid: {len(valid_images)})\n画像サイズ: {target_size}x{target_size}\n出力フォルダ: output_{timestamp}\nYAMLファイルを生成しました: {yaml_filename}'
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
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSONデータの形式が正しくありません'})
    except Exception as e:
        # データベースの整合性制約エラーの場合
        if 'UNIQUE constraint failed' in str(e):
            return JsonResponse({'status': 'error', 'message': 'このラベル名は既に使用されています'})
        return JsonResponse({'status': 'error', 'message': f'ラベルの作成に失敗しました: {str(e)}'})


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
@require_http_methods(["POST", "PUT"]) # ラベルの更新はPOST,PUTリクエストのみ
def update_label(request, label_id):
    """ラベルを更新"""
    try:
        label = get_object_or_404(Label, id=label_id)
        data = json.loads(request.body)
        
        name = data.get('name', '').strip()
        color = data.get('color', label.color)
        
        print(f"ラベル更新要求: ID={label_id}, 現在の名前='{label.name}', 新しい名前='{name}'")
        
        if not name:
            return JsonResponse({'status': 'error', 'message': 'ラベル名が必要です'})
        
        # 名前が変更されている場合のみ重複チェック
        if name != label.name:
            existing_label = Label.objects.filter(name=name).first()
            if existing_label:
                print(f"重複チェック: ラベル名 '{name}' は既に存在します (ID: {existing_label.id})")
                return JsonResponse({'status': 'error', 'message': 'このラベル名は既に存在します'})
        
        # ラベル情報を更新（使用中でも編集可能）
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
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSONデータの形式が正しくありません'})
    except Exception as e:
        # データベースの整合性制約エラーの場合
        if 'UNIQUE constraint failed' in str(e):
            return JsonResponse({'status': 'error', 'message': 'このラベル名は既に使用されています'})
        return JsonResponse({'status': 'error', 'message': f'ラベルの更新に失敗しました: {str(e)}'})


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



