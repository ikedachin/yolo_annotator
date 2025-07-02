# YOLOアノテーター

このレポジトリは**Ultralytics YOLO**シリーズ用の矩形アノテーション作成を効率的に行うWebアプリケーションです。機械学習の物体検出モデル訓練に必要なYOLO形式のアノテーションデータを、直感的なWebインターフェースで作成できます。

## 📋 アプリケーション構成

### ディレクトリ構造
```
yolo_annotator/
├── main.py                      # メインエントリーポイント
├── pyproject.toml              # プロジェクト設定とパッケージ管理
├── README.md                   # このファイル
├── base_images/                # アノテーション対象の画像フォルダ
├── output/                     # 分割後のデータセット
│   ├── images/                 # 分割後の画像フォルダ
│   │   ├── train/
│   │   └── valid/
│   └── labels/                 # 分割後のラベルフォルダ
│       ├── train/
│       └── valid/
└── yolo_annotator/             # Djangoプロジェクトフォルダ
    ├── manage.py               # Django管理コマンド
    ├── annotator/              # Djangoアプリ
    │   ├── static/             # CSS・JavaScript
    │   ├── templates/          # HTMLテンプレート
    │   │   └── annotator/      # アプリ専用テンプレート
    │   ├── models.py           # データモデル
    │   ├── views.py            # ビュー関数
    │   ├── urls.py             # URLルーティング
    │   ├── admin.py            # 管理画面設定
    │   └── management/commands/ # 管理コマンド
    └── yolo_annotator/         # Djangoプロジェクト設定
        ├── settings.py         # Django設定
        ├── urls.py             # メインURLルーティング
        └── wsgi.py             # WSGIエントリーポイント
```

### 技術スタック
- **Backend**: Django 5.2.3 + Django REST Framework 3.14.0
- **Frontend**: HTML5 + Bootstrap 5 + Canvas API + Vanilla JavaScript
- **Database**: SQLite3（軽量・移植性重視）
- **Image Processing**: Pillow 10.0+（PIL）
- **Package Management**: uv（高速Python パッケージマネージャー）
- **Python**: 3.12以上

## 🚀 セットアップと起動

### 0. 前提条件
Python 3.12以上とuvが必要です。uvが未インストールの場合：
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 1. 依存関係のインストール
```bash
uv sync
```

### 2. データベースの初期化
```bash
cd yolo_annotator
uv run python manage.py migrate
uv run python manage.py createsuperuser  # 管理画面用（任意）
```

**注意**: ラベルの初期化コマンド（`init_labels`）は不要です。アプリケーション内でラベルを動的に管理できます。

### 3. アプリケーションの起動

#### 方法1: メインスクリプトから起動（推奨）
```bash
uv run python main.py
```

#### 方法2: uvスクリプトから起動
```bash
uv run yolo-annotator
```

#### 方法3: Djangoプロジェクトから直接起動
```bash
cd yolo_annotator
uv run python manage.py runserver
```

### 4. アクセス
- **メインアプリ**: http://127.0.0.1:8000/
- **管理画面**: http://127.0.0.1:8000/admin/
- **ラベル管理**: http://127.0.0.1:8000/admin/annotator/label/ （アノテーションの種類を追加・編集）

💡 **ヒント**: メインアプリの各画面からも管理画面とラベル管理へのリンクがあります。

## 📖 使用方法

### 1. 画像の準備
`base_images`フォルダに画像ファイル（JPG、PNG、BMP等）を配置してください。

### 2. 画像の読み込み
- トップページで「画像を読み込み」ボタンをクリック
- base_imagesフォルダの画像がデータベースに登録されます

### 3. アノテーション作業
1. 画像一覧から「アノテーション」ボタンをクリック
2. 右側のパネルからラベルを選択（または新規作成）
3. 画像上でドラッグして矩形（バウンディングボックス）を描画
4. 複数のオブジェクトに対してアノテーションを追加
5. 「保存」ボタンでアノテーションを保存
6. ナビゲーション機能で効率的に作業：
   - 「前」ボタンまたは←キーで前の画像に戻る
   - 「次」ボタンまたは→キーで次の画像に進む
   - Ctrl+Sキーで素早く保存

#### ラベル管理機能
- **ラベル追加**: 「ラベル追加」ボタンから新しいラベルを作成
- **ラベル編集**: 既存ラベルの編集ボタン（鉛筆アイコン）で名前や色を変更
- **ラベル削除**: 削除ボタン（ゴミ箱アイコン）でラベルを削除（使用中のラベルは削除不可）

### 4. データセット分割
1. 全ての画像のアノテーションが完了したら、「データセット分割」ボタンをクリック
2. 分割比率（7:3、8:2、9:1）を選択
3. 自動的に`output/images/train`、`output/images/valid`、`output/labels/train`、`output/labels/valid`フォルダに分割されます

## 🔧 主な機能

### ✅ 実装済み機能
- **画像管理システム**: 
  - `base_images`フォルダからの自動読み込み
  - 対応形式：JPG、PNG、BMP、TIFF等
  - 画像一覧のグリッド/リスト表示切り替え
  - アノテーション進捗の可視化
- **高性能アノテーション機能**: 
  - HTML5 Canvas APIによる滑らかな描画
  - ドラッグ&ドロップによる直感的なバウンディングボックス描画
  - リアルタイムプレビュー機能
  - 既存アノテーションの表示・編集・削除
- **効率的ナビゲーション機能**: 
  - 双方向ナビゲーション（前/次ボタン）
  - キーボードショートカット（←/→キー、Ctrl+S）
  - スマートUI（最初/最後の画像で適切なボタン表示）
  - 自動保存機能（画像移動時）
- **動的ラベル管理**: 
  - アプリ内でのリアルタイム追加・編集・削除
  - 視覚的識別のための色分け機能
  - ラベル使用回数の表示
  - 使用中ラベルの削除防止機能
- **YOLO形式出力**: 
  - 正規化座標での自動保存
  - 標準的なYOLO形式（class_id x_center y_center width height）
- **データセット自動分割**: 
  - 7:3、8:2、9:1の比率選択
  - 画像サイズの統一化（640x640、1280x1280等）
  - 適切なパディング処理
  - 学習用YAMLファイルの自動生成
- **レスポンシブデザイン**: 
  - モバイルデバイス対応
  - Bootstrap 5ベースのモダンUI
- **管理機能**:
  - Django管理画面との統合
  - データベース管理とバックアップ対応

### 🛠 管理機能
- **メインダッシュボード**: 
  - 画像一覧とアノテーション進捗の一覧表示
  - ラベル管理（追加・編集・削除）
  - 統計情報（総画像数、アノテーション済み数）
- **アノテーション管理**: 
  - 各画像のアノテーション状況確認
  - アノテーション一覧の表示・削除
  - 保存とナビゲーション機能の統合
- **Django管理画面**: 
  - **ラベル管理**: http://127.0.0.1:8000/admin/annotator/label/
  - **アノテーション管理**: http://127.0.0.1:8000/admin/annotator/annotation/
  - **画像管理**: http://127.0.0.1:8000/admin/annotator/imagefile/
- **データセット出力**: 
  - タイムスタンプ付きの出力フォルダ
  - 学習用YAMLファイルの自動生成
  - 統一画像サイズでの出力

## 📊 データ形式

### YOLO形式
アノテーションはYOLO形式で保存されます：
```
<class_id> <x_center> <y_center> <width> <height>
```
- 座標は画像サイズで正規化（0-1の範囲）
- class_idはラベルのID

### 出力ファイル構造
```
output/
├── output_20250702_143000/    # タイムスタンプ付きフォルダ
│   ├── images/
│   │   ├── train/             # 訓練用画像（統一サイズ）
│   │   └── valid/             # 検証用画像（統一サイズ）
│   ├── labels/
│   │   ├── train/             # 訓練用ラベル（.txtファイル）
│   │   └── valid/             # 検証用ラベル（.txtファイル）
│   └── dataset_640x640_20250702_143000.yaml  # 学習用設定ファイル
└── ... （複数の出力セット）
```

### 学習用YAMLファイル
```yaml
# Train/val/test sets
path: ../output/output_20250702_143000  # dataset root dir
train: images/train
val: images/valid
test: # test images (optional)

# Classes
names:
  0: person
  1: car
  2: bicycle
```

## 🎯 操作のコツ

1. **効率的なアノテーション**
   - 最初にラベルを選択してから描画開始
   - 矩形はドラッグで直感的に描画可能
   - 既存のアノテーションをクリックでハイライト

2. **ナビゲーション効率化**
   - ←/→キーで高速画像移動
   - Ctrl+Sで素早い保存
   - 「前」「次」ボタンも利用可能
   - キーボードとマウス操作の組み合わせで最大効率を実現

3. **品質管理**
   - アノテーション一覧で位置確認
   - 削除ボタン（×）で不要なアノテーションを削除
   - 保存前に内容を確認

5. **データセット管理**
   - 全画像のアノテーション完了後に分割実行
   - 分割比率（7:3、8:2、9:1）の選択
   - 画像サイズ（640x640、416x416等）の選択
   - 分割後のタイムスタンプ付きフォルダ管理
   - 学習用YAMLファイルの確認

6. **ラベル管理**
   - メイン画面とアノテーション画面での一元管理
   - 視覚的識別のための色分け
   - 使用頻度の確認
   - 使用中ラベルの安全な削除防止

## 🔧 カスタマイズ

### ラベルの追加・編集
アノテーションの種類（ラベル）は以下の方法で管理できます：

#### 1. インアプリ管理（推奨）
- **メイン画面**: ラベル一覧エリアの「ラベル追加」ボタン
- **アノテーション画面**: 右側パネルの「ラベル追加」ボタン
- **編集・削除**: 各ラベルの編集（鉛筆）・削除（ゴミ箱）ボタン
- **リアルタイム反映**: 変更は即座にUIに反映されます

#### 2. 管理画面
- **管理画面**: http://127.0.0.1:8000/admin/annotator/label/
- **設定項目**: 
  - ラベル名（例：person, car, bike）
  - 表示色（矩形の色として使用）

### 設定の変更
プロジェクト設定は`yolo_annotator/yolo_annotator/settings.py`で管理されています：

```python
# カスタム設定
PROJECT_ROOT = BASE_DIR.parent
BASE_IMAGES_DIR = PROJECT_ROOT / 'base_images'
TRAIN_IMAGES_DIR = PROJECT_ROOT / 'output' / 'images' / 'train'
VALID_IMAGES_DIR = PROJECT_ROOT / 'output' / 'images' / 'valid'
TRAIN_LABELS_DIR = PROJECT_ROOT / 'output' / 'labels' / 'train'
VALID_LABELS_DIR = PROJECT_ROOT / 'output' / 'labels' / 'valid'
```

### 開発モード
開発時には以下のコマンドで直接Djangoサーバーを起動できます：
```bash
cd yolo_annotator
uv run python manage.py runserver
```

### アプリケーションの詳細構造
```
yolo_annotator/
├── main.py                        # エントリーポイント
├── pyproject.toml                 # プロジェクト設定
├── base_images/                   # 元画像（プロジェクトルート）
├── output/                        # 出力データセット（プロジェクトルート）
│   └── output_YYYYMMDD_HHMMSS/   # タイムスタンプ付きフォルダ
└── yolo_annotator/               # Djangoプロジェクト
    ├── manage.py                 # Django管理
    ├── db.sqlite3               # SQLiteデータベース
    ├── annotator/               # メインアプリ
    │   ├── models.py           # データモデル
    │   ├── views.py            # ビューロジック
    │   ├── urls.py             # URLルーティング
    │   ├── admin.py            # 管理画面設定
    │   ├── static/             # CSS・JavaScript
    │   ├── templates/          # HTMLテンプレート
    │   └── migrations/         # データベースマイグレーション
    └── yolo_annotator/         # プロジェクト設定
        ├── settings.py         # Django設定
        ├── urls.py             # メインURLルーティング
        └── wsgi.py             # WSGIエントリーポイント
```

## ⚡ 新機能・改善点

### 🚀 最新の機能強化
- **効率的ナビゲーション機能**: 
  - 双方向ナビゲーション（前/次ボタン）による自由な画像間移動
  - キーボードショートカット（←/→キー、Ctrl+S）
  - スマートUI（最初/最後の画像での適切なボタン表示）
  - 自動保存機能による作業効率向上
- **動的ラベル管理機能**: 
  - リアルタイムラベル追加・編集・削除
  - 色分けによる視覚的識別
  - 使用回数表示と安全な削除防止機能
  - メイン画面とアノテーション画面での統合管理
- **高度なデータセット分割機能**: 
  - タイムスタンプ付き出力フォルダ
  - 統一画像サイズでの出力（640x640、416x416等）
  - 学習用YAMLファイルの自動生成
  - 比率選択（7:3、8:2、9:1）

### ✨ 技術的改善
- **テンプレート構造最適化**: 重複ファイル削除と構造整理
- **エラーハンドリング強化**: JavaScriptとCSS構文エラーの解決
- **パフォーマンス向上**: Canvas描画の最適化とメモリ管理
- **セキュリティ強化**: CSRF保護とSQLインジェクション対策

## 📝 トラブルシューティング

### よくある問題と解決方法

#### 1. 初回セットアップ時の問題
```bash
# 問題: uvが見つからない
# 解決方法: uvをインストール
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 問題: Python 3.12が見つからない
# 解決方法: Python 3.12以上をインストール、またはuvでインストール
uv python install 3.12
```

#### 2. データベース関連エラー
```bash
# 問題: マイグレーションエラー
# 解決方法: マイグレーションを再実行
cd yolo_annotator
uv run python manage.py migrate

# 問題: 管理画面にアクセスできない
# 解決方法: スーパーユーザーを作成
uv run python manage.py createsuperuser
```

#### 3. 画像表示問題
**確認項目**:
- `base_images/`フォルダが存在するか
- 画像ファイルが対応形式か（JPG、PNG、BMP、TIFF等）
- 「画像を読み込み」ボタンをクリックしたか
- ファイル名に特殊文字が含まれていないか

#### 4. アノテーション保存エラー
**確認項目**:
- ラベルが選択されているか
- ネットワーク接続が正常か
- ブラウザの開発者ツール（F12）でエラーをチェック
- JavaScriptが有効になっているか

#### 5. ナビゲーション機能が動作しない
**解決方法**: 
- ブラウザのキャッシュをクリア
- ページを再読み込み（Ctrl+F5）
- ブラウザがHTML5 Canvasに対応しているか確認

#### 6. データセット分割エラー
**確認項目**:
- アノテーション済みの画像が存在するか
- `output/`フォルダの書き込み権限があるか
- ディスク容量が十分にあるか

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。


