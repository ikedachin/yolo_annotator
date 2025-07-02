# ナビゲーション機能ドキュメント

## 概要

YOLOアノテーター v1.1で追加されたナビゲーション機能について詳しく説明します。この機能は、アノテーション作業の効率性を大幅に向上させることを目的として実装されました。

## 機能の背景

### 課題
- 従来は「次の画像」ボタンのみで、前の画像に戻れない
- キーボードでの操作ができないため、マウス依存の作業
- 修正作業で前の画像に戻りたいケースに対応できない

### 解決策
- 双方向ナビゲーションボタンの追加
- キーボードショートカットの実装
- 効率的な作業フローの実現

## 実装詳細

### 1. Backend実装（views.py）

#### 修正内容
```python
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
```

#### データベースクエリ詳細
- **next_image**: `filter(id__gt=image_id).first()`
  - 現在の画像IDより大きいIDの画像を昇順で取得
  - 最初に見つかった画像が「次の画像」
- **prev_image**: `filter(id__lt=image_id).order_by('-id').first()`
  - 現在の画像IDより小さいIDの画像を降順で取得
  - 最初に見つかった画像が「前の画像」

### 2. Frontend実装（annotate.html）

#### HTMLテンプレート
```html
<div class="btn-group" role="group">
    {% if prev_image %}
    <a href="{% url 'annotator:annotate' prev_image.id %}" id="prev-btn" class="btn btn-outline-primary btn-sm" title="前の画像">
        <i class="bi bi-chevron-left"></i> 前
    </a>
    {% endif %}
    {% if next_image %}
    <a href="{% url 'annotator:annotate' next_image.id %}" id="next-btn" class="btn btn-outline-primary btn-sm" title="次の画像">
        次 <i class="bi bi-chevron-right"></i>
    </a>
    {% endif %}
</div>
```

#### 設計原則
- **条件表示**: 前/次の画像が存在する場合のみボタンを表示
- **Bootstrap**: btn-groupでボタンをグループ化
- **アイコン**: Bootstrap Iconsで視覚的にわかりやすく
- **レスポンシブ**: モバイルデバイスでも操作しやすい

### 3. JavaScript実装（annotator.js）

#### キーボードナビゲーション関数
```javascript
function initKeyboardNavigation() {
    document.addEventListener('keydown', function(event) {
        // モーダルが開いている場合は無視
        const openModals = document.querySelectorAll('.modal.show');
        if (openModals.length > 0) {
            return;
        }
        
        // 入力フィールドにフォーカスがある場合は無視
        const activeElement = document.activeElement;
        if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
            return;
        }
        
        switch(event.key) {
            case 'ArrowLeft':
                event.preventDefault();
                const prevBtn = document.getElementById('prev-btn');
                if (prevBtn) {
                    prevBtn.click();
                }
                break;
                
            case 'ArrowRight':
                event.preventDefault();
                const nextBtn = document.getElementById('next-btn');
                if (nextBtn) {
                    nextBtn.click();
                }
                break;
                
            case 's':
            case 'S':
                if (event.ctrlKey) {
                    event.preventDefault();
                    const saveBtn = document.getElementById('save-btn');
                    if (saveBtn) {
                        saveBtn.click();
                    }
                }
                break;
        }
    });
}
```

#### 安全機能
1. **モーダル干渉防止**: モーダルが開いている時はキーボードショートカットを無効化
2. **入力フィールド保護**: テキスト入力中はショートカットを無効化
3. **存在チェック**: ボタンが存在する場合のみクリック実行
4. **デフォルト動作防止**: `preventDefault()`でブラウザのデフォルト動作を無効化

## ユーザーインターフェース

### ナビゲーションボタン
- **配置**: アノテーション画面のヘッダー右側
- **グループ化**: Bootstrap btn-groupで統一感のある表示
- **アイコン**: 矢印アイコンで直感的な操作
- **状態管理**: 最初/最後の画像では適切なボタンのみ表示

### キーボードショートカット表示
```html
<div class="card mt-3">
    <div class="card-header">
        <h6>キーボードショートカット</h6>
    </div>
    <div class="card-body">
        <small>
            <ul class="list-unstyled">
                <li><kbd>←</kbd> 前の画像</li>
                <li><kbd>→</kbd> 次の画像</li>
                <li><kbd>Ctrl+S</kbd> 保存</li>
            </ul>
        </small>
    </div>
</div>
```

## 作業効率の向上

### Before（従来）
1. アノテーション作業
2. 「次の画像」ボタンをクリック
3. 前の画像に戻りたい場合は一覧ページから選択

### After（改善後）
1. アノテーション作業
2. →キーまたは「次」ボタンで次の画像
3. ←キーまたは「前」ボタンで前の画像
4. Ctrl+Sで素早い保存

### 効率向上のポイント
- **マウス移動の削減**: キーボードのみでの作業が可能
- **修正作業の簡素化**: 前の画像に瞬時に戻れる
- **作業リズムの向上**: 連続的な作業フローの実現
- **ミス修正の容易性**: すぐに前の画像を確認・修正可能

## 技術的考慮事項

### パフォーマンス
- **軽量実装**: 最小限のJavaScriptコード
- **効率的クエリ**: データベースクエリの最適化
- **メモリ使用量**: 追加メモリ消費は最小限

### セキュリティ
- **CSRF保護**: 既存のセキュリティ機能を維持
- **入力検証**: 不正なimage_idに対する適切な処理
- **権限管理**: 既存の権限システムを継承

### 互換性
- **ブラウザ対応**: モダンブラウザでの動作保証
- **モバイル対応**: タッチデバイスでの操作性
- **既存機能**: 既存の機能に影響を与えない設計

## 今後の改善案

### 短期改善
- **画像プリロード**: 次/前の画像の事前読み込み
- **ショートカットカスタマイズ**: ユーザー設定でキー割り当て変更
- **ジャンプ機能**: 特定の画像番号にジャンプ

### 長期改善
- **画像順序設定**: ファイル名以外の順序オプション
- **バッチ操作**: 複数画像の一括処理
- **作業履歴**: アノテーション作業の履歴管理

## まとめ

ナビゲーション機能の追加により、YOLOアノテーターの使いやすさが大幅に向上しました。特に大量の画像データを扱う際の作業効率改善は顕著で、ユーザーの生産性向上に大きく貢献します。

### 主要メリット
1. **作業効率の向上**: キーボードショートカットによる高速操作
2. **修正作業の簡素化**: 前の画像への即座の戻り
3. **ユーザビリティ向上**: 直感的なナビゲーション
4. **品質向上**: 修正確認の容易性

この機能により、YOLOアノテーターはより実用的で効率的なツールとして、機械学習のワークフローに貢献します。
