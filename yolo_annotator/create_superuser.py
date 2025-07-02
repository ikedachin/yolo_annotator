#!/usr/bin/env python
import os
import django
import sys

# Django設定の初期化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yolo_annotator.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """スーパーユーザーを作成"""
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'
    
    if User.objects.filter(username=username).exists():
        print(f'スーパーユーザー "{username}" は既に存在しています。')
        return
    
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'スーパーユーザー "{username}" を作成しました。')
    print(f'ユーザー名: {username}')
    print(f'パスワード: {password}')
    print('これらの認証情報を使用してDjango管理サイトにログインできます。')

if __name__ == '__main__':
    create_superuser()
