# ナビゲーション機能詳細ドキュメント

## 概要

YOLOアノテーターの効率的ナビゲーション機能について詳しく説明します。この機能は、アノテーション作業の効率性を大幅に向上させ、作業者の操作負荷を軽減することを目的として実装されました。

## 機能の背景

### 解決した課題
1. **一方向移動の制限**: 従来は「次の画像」ボタンのみで、前の画像に戻れない
2. **マウス依存の操作**: キーボードでの操作ができないため、効率的な作業が困難
3. **修正作業の困難**: 前の画像の修正が必要な場合、最初からやり直しが必要
4. **作業フローの中断**: 画像間移動のたびにマウス操作が必要

### 実装した解決策
1. **双方向ナビゲーション**: 前/次ボタンによる自由な画像間移動
2. **キーボードショートカット**: ←/→キー、Ctrl+Sによる高速操作
3. **スマートUI**: 画像位置に応じた適切なボタン表示
4. **自動保存機能**: 画像移動時の自動保存による作業効率向上

## 機能詳細

### 1. 双方向ナビゲーション
- **前の画像**: IDが小さい順で最後の画像に移動
- **次の画像**: IDが大きい順で最初の画像に移動
- **境界制御**: 最初/最後の画像での適切なボタン表示

### 2. キーボードショートカット
- **←キー**: 前の画像に移動
- **→キー**: 次の画像に移動
- **Ctrl+S**: アノテーション保存
- **自動保存**: 画像移動時の自動保存機能

### 3. スマートUI機能
- **動的ボタン表示**: 画像位置に応じたボタンの表示/非表示
- **視覚的フィードバック**: ホバー効果とアニメーション
- **レスポンシブ対応**: モバイルデバイスでの適切な表示

### 4. 統合された作業フロー
- **シームレス移動**: アノテーション→保存→移動の一連操作
- **作業状態保持**: 選択中のラベルとUI状態の維持
- **エラーハンドリング**: 移動時のエラー検出と適切な処理

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

## 実装詳細

### 1. Backend実装（views.py）

#### 核心的な実装
```python
def annotate(request, image_id):
    """アノテーション画面（ナビゲーション機能付き）"""
    image = get_object_or_404(ImageFile, id=image_id)
    labels = Label.objects.all()
    annotations = Annotation.objects.filter(image=image)
    
    # 効率的な双方向ナビゲーションクエリ
    next_image = ImageFile.objects.filter(id__gt=image_id).first()
    prev_image = ImageFile.objects.filter(id__lt=image_id).order_by('-id').first()
    
    return render(request, 'annotator/annotate.html', {
        'image': image,
        'labels': labels,
        'annotations': annotations,
        'next_image': next_image,    # None if last image
        'prev_image': prev_image     # None if first image
    })
```

#### データベースクエリの最適化
- **next_image**: `filter(id__gt=image_id).first()`
  - 現在の画像IDより大きいIDの画像を昇順で取得
  - `first()`により最初の1件のみ取得（効率的）
- **prev_image**: `filter(id__lt=image_id).order_by('-id').first()`
  - 現在の画像IDより小さいIDの画像を降順で取得
  - 最も近い前の画像を効率的に取得

### 2. Frontend実装（annotate.html）

#### テンプレート構造
```html
<div class="btn-group" role="group">
    {% if prev_image %}
    <a href="{% url 'annotator:annotate' prev_image.id %}" 
       id="prev-btn" class="btn btn-outline-primary btn-sm" 
       title="前の画像">
        <i class="bi bi-chevron-left"></i> 前
    </a>
    {% endif %}
    
    {% if next_image %}
    <a href="{% url 'annotator:annotate' next_image.id %}" 
       id="next-btn" class="btn btn-outline-primary btn-sm" 
       title="次の画像">
        次 <i class="bi bi-chevron-right"></i>
    </a>
    {% endif %}
    
    {% if not next_image and not prev_image %}
    <a href="{% url 'annotator:index' %}" 
       class="btn btn-secondary btn-sm">一覧に戻る</a>
    {% endif %}
</div>
```

#### スマートUI機能
- **条件付き表示**: 前/次の画像が存在する場合のみボタン表示
- **単一画像対応**: 画像が1つのみの場合は「一覧に戻る」ボタン
- **Bootstrap アイコン**: 視覚的にわかりやすいアイコン使用

### 3. JavaScript実装（annotator.js）

#### キーボードショートカット
```javascript
document.addEventListener('keydown', function(e) {
    // アノテーション作業中のキーボードショートカット
    if (e.key === 'ArrowLeft' && document.getElementById('prev-btn')) {
        // 前の画像に移動（自動保存付き）
        saveAnnotationsAndNavigate('prev');
    } else if (e.key === 'ArrowRight' && document.getElementById('next-btn')) {
        // 次の画像に移動（自動保存付き）
        saveAnnotationsAndNavigate('next');
    } else if (e.ctrlKey && e.key === 's') {
        // Ctrl+S: 保存
        e.preventDefault();
        saveAnnotations();
    }
});

function saveAnnotationsAndNavigate(direction) {
    // 現在のアノテーションを保存してから移動
    saveAnnotations().then(() => {
        const btn = document.getElementById(direction + '-btn');
        if (btn) {
            window.location.href = btn.href;
        }
    });
}
```

#### 自動保存機能
- **画像移動時**: 次/前ボタンクリック時に自動保存
- **キーボード移動**: ←/→キー使用時も自動保存
- **エラーハンドリング**: 保存失敗時の適切な処理

### 4. 統合された作業フロー

#### 効率的な作業パターン
1. **画像表示** → **ラベル選択** → **アノテーション作成**
2. **Ctrl+S で保存** または **→キーで次に移動（自動保存）**
3. **修正が必要な場合は ←キーで前に戻る**
4. **繰り返し**

#### パフォーマンス最適化
- **プリロード**: 隣接画像の事前読み込み（将来実装予定）
- **効率的なクエリ**: 必要最小限のデータベースアクセス
- **キャッシュ活用**: ブラウザキャッシュによる高速化

## 使用方法

### 基本操作
1. **マウス操作**: 前/次ボタンをクリック
2. **キーボード操作**: ←/→キーで移動
3. **保存**: Ctrl+Sキーまたは保存ボタン

### 効率的な作業手順
1. **最初の画像から開始**: 順次アノテーション作業
2. **→キーで次へ**: 自動保存機能により効率的に進む
3. **修正時は←キーで戻る**: 前の画像の修正が容易
4. **Ctrl+Sで随時保存**: 作業内容の安全な保存

### トラブルシューティング
- **キーボードが効かない**: ページの再読み込み（F5）
- **自動保存されない**: ネットワーク接続の確認
- **ボタンが表示されない**: 画像データベースの確認

## 技術的メリット

### 開発面
- **モジュール化**: 既存コードへの影響最小限
- **拡張性**: 将来的な機能追加に対応
- **保守性**: 明確な責任分離

### ユーザー体験
- **作業効率向上**: マウス/キーボード両対応
- **直感的操作**: 自然なナビゲーション
- **エラー防止**: 自動保存による作業内容保護

### パフォーマンス
- **高速移動**: 効率的なデータベースクエリ
- **メモリ効率**: 必要最小限のデータ読み込み
- **レスポンシブ**: 軽快な操作感
