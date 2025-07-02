# views.py 解説

## 概要
`views.py`は、YOLOアノテーターアプリケーションのDjangoビューを定義するファイルです。画像のアノテーション機能、データセット管理、ラベル管理などの主要機能を提供しています。

## インポート
```python
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
```

## 主要な関数とその機能

### 1. `index(request)`
**機能**: 画像一覧ページの表示
- 全ての画像ファイルをファイル名順で取得
- 全てのラベルを取得し、各ラベルの使用回数（Count）を計算
- アノテーション済み画像数を計算
- `index.html`テンプレートをレンダリング

**データベースクエリ**:
- `Label.objects.annotate(usage_count=Count('annotation'))`: 各ラベルにアノテーション使用回数を追加
- `ImageFile.objects.filter(is_annotated=True).count()`: アノテーション済み画像数を取得

**戻り値**: レンダリングされたHTMLページ（ラベル使用回数情報を含む）

### 2. `annotate(request, image_id)`
**機能**: アノテーション画面の表示
- 指定されたIDの画像を取得
- 全てのラベルとその画像のアノテーションを取得
- 次の画像（IDが大きい順で最初の画像）を取得
- `annotate.html`テンプレートをレンダリング

**パラメータ**:
- `image_id`: アノテーション対象の画像ID

**戻り値**: アノテーション画面のHTMLページ

### 3. `save_annotations(request, image_id)`
**機能**: アノテーションデータの保存
- POSTリクエストのみ許可、CSRF無効
- JSONデータからアノテーション情報を取得
- 既存のアノテーションを削除後、新しいアノテーションを保存
- 画像をアノテーション済みとしてマーク

**パラメータ**:
- `image_id`: 対象画像のID
- リクエストボディ: アノテーション配列を含むJSON

**戻り値**: 成功/失敗のJSONレスポンス

### 4. `load_images(request)`
**機能**: base_imagesフォルダから画像を読み込み
- `settings.BASE_IMAGES_DIR`から画像ファイルを検索
- サポート形式: .jpg, .jpeg, .png, .bmp, .tiff
- PILライブラリを使用して画像の幅・高さを取得
- データベースに新しい画像レコードを作成

**戻り値**: 読み込み結果のJSONレスポンス

### 5. `split_dataset(request)`
**機能**: データセットをtrain/validに分割
- アノテーション済み画像のみを対象
- 指定された比率（デフォルト8:2）でランダム分割
- 画像ファイルを各フォルダにコピー
- YOLOフォーマットのラベルファイルを生成

**パラメータ**:
- リクエストボディ: `split_ratio`（分割比率）を含むJSON

**戻り値**: 分割結果のJSONレスポンス

### 6. `add_label(request)`
**機能**: 新しいラベルの追加
- ラベル名と色情報を受け取り
- 重複チェックを実行
- 新しいラベルをデータベースに保存

**パラメータ**:
- リクエストボディ: `name`（ラベル名）と`color`（色）を含むJSON

**戻り値**: 作成されたラベル情報またはエラーのJSONレスポンス

### 7. `delete_label(request, label_id)`
**機能**: ラベルの削除
- 指定されたIDのラベルを削除
- アノテーションで使用中の場合は削除を拒否

**パラメータ**:
- `label_id`: 削除対象のラベルID

**戻り値**: 削除結果のJSONレスポンス

### 8. `update_label(request, label_id)`
**機能**: ラベル情報の更新
- ラベル名と色の更新
- 名前変更時の重複チェック
- 使用中のラベルでも編集可能

**パラメータ**:
- `label_id`: 更新対象のラベルID
- リクエストボディ: 更新する`name`と`color`を含むJSON

**戻り値**: 更新されたラベル情報またはエラーのJSONレスポンス

### 9. `serve_image(request, filename)`
**機能**: base_imagesフォルダからの画像配信
- 静的ファイル配信機能
- キャッシュ制御ヘッダーの設定
- CORS対応
- MIMEタイプの自動判定

**パラメータ**:
- `filename`: 配信対象の画像ファイル名

**戻り値**: 画像ファイルのHTTPレスポンス

## エラーハンドリング
- JSONデコードエラーの処理
- データベース制約エラー（UNIQUE constraint）の処理
- ファイル操作エラーの処理
- 404エラー（画像が見つからない場合）の処理

## セキュリティ機能
- `@csrf_exempt`: 特定のAPIエンドポイントでCSRF保護を無効化
- `@require_http_methods`: HTTPメソッドの制限
- `get_object_or_404`: 安全なオブジェクト取得

## 設定値の使用
- `settings.BASE_IMAGES_DIR`: 元画像フォルダのパス
- `settings.TRAIN_IMAGES_DIR`: 訓練用画像フォルダのパス
- `settings.TRAIN_LABELS_DIR`: 訓練用ラベルフォルダのパス
- `settings.VALID_IMAGES_DIR`: 検証用画像フォルダのパス
- `settings.VALID_LABELS_DIR`: 検証用ラベルフォルダのパス

## 主要なワークフロー
1. **画像読み込み**: `load_images()` → base_imagesから画像を検索・登録
2. **アノテーション**: `annotate()` → `save_annotations()` → アノテーション作業
3. **ラベル使用状況**: `index()` → ラベル一覧にCount集計による使用回数表示
4. **データセット分割**: `split_dataset()` → 訓練/検証用データの生成
5. **ラベル管理**: `add_label()`, `update_label()`, `delete_label()` → ラベルのCRUD操作

## データベース集計機能
### ラベル使用回数の計算
```python
# index()関数で使用される集計クエリ
labels = Label.objects.annotate(usage_count=Count('annotation')).order_by('name')
```
このクエリにより、各ラベルに対してそのラベルを使用するAnnotationレコードの数が`usage_count`属性として追加されます。これによりテンプレート側で`{{ label.usage_count }}`としてアクセス可能になります。

このファイルは、WebアプリケーションのバックエンドAPIとして機能し、フロントエンド（JavaScript）からのリクエストを処理してYOLOアノテーション作業をサポートしています。
