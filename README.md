# YOLOアノテーター

このレポジトリはUltralytics YOLOシリーズ用の矩形アノテーションを行うWebアプリケーションです。私は1行もコードを書かずにAgentさんに作ってもらいました。

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
- **Backend**: Django 5.2.3 + Django REST Framework
- **Frontend**: HTML + Bootstrap + Canvas API
- **Database**: SQLite
- **Image Processing**: Pillow
- **Package Management**: uv

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
uv run python manage.py createsuperuser
uv run python manage.py init_labels
```

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
6. 「次の画像」ボタンで次の画像に進む

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
- **画像一覧表示**: base_imagesから自動読み込み
- **バウンディングボックス描画**: Canvas APIを使用した直感的な操作
- **ラベル管理**: 
  - アプリ内でのラベル追加・編集・削除
  - 色付きで視覚的に区別可能
  - 使用中ラベルの削除防止機能
- **自動保存**: 次の画像に進む際に自動保存
- **YOLO形式出力**: 正規化された座標形式で保存
- **データセット分割**: 指定比率でtrain/valid分割
- **レスポンシブデザイン**: モバイルデバイスでも使用可能
- **アノテーション編集**: 既存のアノテーションの表示・削除
- **画像順送り**: 効率的なアノテーション作業フロー

### 🛠 管理機能
- **インアプリ ラベル管理**: メイン画面から直接ラベルの追加・編集・削除が可能
- **管理画面**: 
  - **ラベル管理**: http://127.0.0.1:8000/admin/annotator/label/ でアノテーション種類を追加・編集・削除
  - **アノテーション管理**: http://127.0.0.1:8000/admin/annotator/annotation/ で全アノテーションを確認・編集
  - **画像管理**: http://127.0.0.1:8000/admin/annotator/imagefile/ で登録画像の状況確認
- データベース管理とバックアップ

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
├── images/
│   ├── train/    # 訓練用画像
│   └── valid/    # 検証用画像
└── labels/
    ├── train/    # 訓練用ラベル（.txtファイル）
    └── valid/    # 検証用ラベル（.txtファイル）
```

## 🎯 操作のコツ

1. **効率的なアノテーション**
   - 最初にラベルを選択してから描画開始
   - 矩形はドラッグで直感的に描画可能
   - 既存のアノテーションをクリックでハイライト

2. **品質管理**
   - アノテーション一覧で位置確認
   - 削除ボタン（×）で不要なアノテーションを削除
   - 保存前に内容を確認

3. **データセット管理**
   - 全画像のアノテーション完了後に分割実行
   - 分割比率は学習の目的に応じて選択
   - 分割後は`output/images`と`output/labels`フォルダを学習に使用

4. **ラベル管理**
   - メイン画面から直接ラベル追加・編集・削除が可能
   - アノテーション画面でもその場でラベル管理
   - 使用中のラベルは安全機能により削除不可

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
`yolo_annotator/yolo_annotator/settings.py`でディレクトリパスや設定を変更可能です。

### 開発モード
開発時には以下のコマンドで直接Djangoサーバーを起動できます：
```bash
cd yolo_annotator
uv run python manage.py runserver --settings=yolo_annotator.settings
```

### プロジェクト構造の詳細
- **main.py**: アプリケーションのエントリーポイント
- **yolo_annotator/**: Djangoプロジェクトのルート
- **base_images/**: 元画像ディレクトリ（プロジェクトルートに配置）
- **output/**: 分割後のデータセット（プロジェクトルートに配置）

## ⚡ 新機能・改善点

### ✨ 最新の改善（テンプレート修正）
- **不要ファイル削除**: 重複していたテンプレートファイルを削除
- **エラー修正**: JavaScriptとCSSの構文エラーを解決
- **動的色設定**: ラベルの色をJavaScriptで安全に適用
- **テンプレート構造最適化**: `annotator/`サブディレクトリ内のテンプレートのみ使用

### 🎯 ラベル管理機能の強化
- **リアルタイム追加**: その場でラベルを追加してすぐに使用可能
- **安全な削除**: 使用中のラベルは削除できない安全機能
- **視覚的フィードバック**: 色付きラベルで視覚的に区別
- **モーダルUI**: 直感的な操作インターフェース

## 🙅‍♂️ トラブルシューティング

### よくある問題と解決方法

#### 1. テンプレートエラー
```
TemplateDoesNotExist: annotator/index.html
```
**解決方法**: テンプレートが正しい場所にあることを確認
- 使用するテンプレート: `yolo_annotator/annotator/templates/annotator/`内のファイル
- 重複ファイルは削除済み

#### 2. 画像が表示されない
**確認項目**:
- `base_images/`フォルダが存在するか
- 画像ファイルが対応形式か（JPG、PNG、BMP等）
- 「画像を読み込み」ボタンをクリックしたか

#### 3. ラベルの色が表示されない
**解決方法**: ブラウザのキャッシュをクリアして再読み込み

#### 4. アノテーションが保存されない
**確認項目**:
- ラベルが選択されているか
- ネットワーク接続が正常か
- ブラウザの開発者ツールでエラーをチェック

#### 5. データベースエラー
**解決方法**: マイグレーションを再実行
```bash
cd yolo_annotator
uv run python manage.py migrate
```

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。


