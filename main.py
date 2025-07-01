#!/usr/bin/env python
"""
YOLOアノテーターのメインエントリーポイント
Djangoサーバーを起動します。
"""
import os
import sys
import subprocess
from pathlib import Path


def main():
    """Djangoサーバーを起動します。"""
    print("🚀 YOLO Annotator を起動しています...")
    
    # プロジェクトのルートディレクトリ
    project_root = Path(__file__).parent
    django_project_dir = project_root / "yolo_annotator"
    
    # Djangoプロジェクトディレクトリに移動
    os.chdir(django_project_dir)
    
    # manage.pyのパス
    manage_py = django_project_dir / "manage.py"
    
    if not manage_py.exists():
        print("❌ manage.py が見つかりません。")
        print(f"   期待されるパス: {manage_py}")
        sys.exit(1)
    
    print(f"📁 プロジェクトディレクトリ: {django_project_dir}")
    print("🌐 サーバーを起動中...")
    print("   アクセス先: http://127.0.0.1:8000/")
    print("   管理画面: http://127.0.0.1:8000/admin/")
    print("   停止: Ctrl+C")
    print("-" * 50)
    
    try:
        # Djangoサーバーを起動
        subprocess.run([
            sys.executable, "manage.py", "runserver"
        ], check=True)
    except KeyboardInterrupt:
        print("\n✋ サーバーを停止しました。")
    except subprocess.CalledProcessError as e:
        print(f"❌ サーバーの起動に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
