// アノテーション機能のJavaScript
class AnnotationCanvas {
    constructor(canvasId) {
        console.log('AnnotationCanvas constructor called with:', canvasId);
        this.canvas = document.getElementById(canvasId);
        
        if (!this.canvas) {
            console.error('Canvas element not found:', canvasId);
            alert('Canvas要素が見つかりません: ' + canvasId);
            return;
        }
        
        console.log('Canvas element found:', this.canvas);
        this.ctx = this.canvas.getContext('2d');
        console.log('Canvas context:', this.ctx);
        
        this.image = new Image();
        this.annotations = [];
        this.currentAnnotation = null;
        this.selectedLabelId = null;
        this.selectedLabelName = null;
        this.selectedLabelColor = '#FF0000';
        this.isDrawing = false;
        this.startX = 0;
        this.startY = 0;
        this.scale = 1;
        this.offsetX = 0;
        this.offsetY = 0;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
        this.canvas.addEventListener('click', this.onCanvasClick.bind(this));
    }
    
    loadImage(imageUrl) {
        console.log('画像を読み込み中:', imageUrl);
        
        // 画像読み込み前にCanvasを初期化
        this.canvas.width = 800;
        this.canvas.height = 600;
        this.ctx.fillStyle = '#f8f9fa';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // ローディング表示
        this.ctx.fillStyle = '#6c757d';
        this.ctx.font = '18px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('画像を読み込み中...', this.canvas.width / 2, this.canvas.height / 2);
        this.ctx.textAlign = 'left';
        
        this.image.onload = () => {
            console.log('画像読み込み成功');
            console.log('画像の自然サイズ:', this.image.naturalWidth, 'x', this.image.naturalHeight);
            this.resizeCanvas();
            this.redraw();
        };
        
        this.image.onerror = (e) => {
            console.error('画像読み込み失敗:', e);
            console.error('URL:', imageUrl);
            
            // エラー表示
            this.ctx.fillStyle = '#f8d7da';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.fillStyle = '#721c24';
            this.ctx.font = '16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('画像の読み込みに失敗しました', this.canvas.width / 2, this.canvas.height / 2 - 20);
            this.ctx.fillText('URL: ' + imageUrl, this.canvas.width / 2, this.canvas.height / 2 + 10);
            this.ctx.textAlign = 'left';
            
            // アラートも表示
            setTimeout(() => {
                alert('画像の読み込みに失敗しました。URLを確認してください: ' + imageUrl);
            }, 100);
        };
        
        // 画像読み込み開始
        this.image.crossOrigin = 'anonymous';
        const cacheBuster = '?t=' + Date.now();
        this.image.src = imageUrl + cacheBuster;
        
        console.log('画像読み込み開始:', this.image.src);
    }
    
    resizeCanvas() {
        console.log('resizeCanvas called');
        
        if (!this.image || !this.image.naturalWidth || !this.image.naturalHeight) {
            console.error('Invalid image for resizing');
            return;
        }
        
        console.log('Image natural dimensions:', this.image.naturalWidth, 'x', this.image.naturalHeight);
        
        // コンテナサイズを取得
        const container = this.canvas.parentElement;
        const containerWidth = container.clientWidth - 40; // パディングを考慮
        const maxHeight = Math.min(window.innerHeight * 0.7, 600); // 最大高さを制限
        
        console.log('Container constraints:', containerWidth, 'x', maxHeight);
        
        // 画像のアスペクト比を維持してキャンバスサイズを計算
        const imageAspectRatio = this.image.naturalWidth / this.image.naturalHeight;
        const containerAspectRatio = containerWidth / maxHeight;
        
        if (imageAspectRatio > containerAspectRatio) {
            // 幅が制限要因
            this.canvas.width = containerWidth;
            this.canvas.height = containerWidth / imageAspectRatio;
        } else {
            // 高さが制限要因
            this.canvas.height = maxHeight;
            this.canvas.width = maxHeight * imageAspectRatio;
        }
        
        // スケール係数を計算
        this.scale = this.canvas.width / this.image.naturalWidth;
        
        console.log('Canvas resized to:', this.canvas.width, 'x', this.canvas.height);
        console.log('Scale factor:', this.scale);
        
        // CSSでキャンバスサイズを明示的に設定
        this.canvas.style.width = this.canvas.width + 'px';
        this.canvas.style.height = this.canvas.height + 'px';
    }
    
    onMouseDown(e) {
        if (!this.selectedLabelId) {
            alert('ラベルを選択してください');
            return;
        }
        
        const rect = this.canvas.getBoundingClientRect();
        this.startX = e.clientX - rect.left;
        this.startY = e.clientY - rect.top;
        this.isDrawing = true;
    }
    
    onMouseMove(e) {
        if (!this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        this.redraw();
        this.drawCurrentBox(this.startX, this.startY, currentX, currentY);
    }
    
    onMouseUp(e) {
        if (!this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const endX = e.clientX - rect.left;
        const endY = e.clientY - rect.top;
        
        const minX = Math.min(this.startX, endX);
        const minY = Math.min(this.startY, endY);
        const maxX = Math.max(this.startX, endX);
        const maxY = Math.max(this.startY, endY);
        
        const width = maxX - minX;
        const height = maxY - minY;
        
        if (width > 10 && height > 10) {
            // Canvas座標を画像座標に変換してYOLO形式に変換
            const imageX = minX / this.scale;
            const imageY = minY / this.scale;
            const imageWidth = width / this.scale;
            const imageHeight = height / this.scale;
            
            // YOLO形式（正規化された中心座標と幅・高さ）
            const x_center = (imageX + imageWidth / 2) / this.image.naturalWidth;
            const y_center = (imageY + imageHeight / 2) / this.image.naturalHeight;
            const norm_width = imageWidth / this.image.naturalWidth;
            const norm_height = imageHeight / this.image.naturalHeight;
            
            const annotation = {
                id: Date.now(), // 一時的なID
                label_id: this.selectedLabelId,
                label_name: this.selectedLabelName,
                label_color: this.selectedLabelColor,
                x_center: x_center,
                y_center: y_center,
                width: norm_width,
                height: norm_height
            };
            
            this.annotations.push(annotation);
            this.updateAnnotationsList();
        }
        
        this.isDrawing = false;
        this.redraw();
    }
    
    onCanvasClick(e) {
        if (this.isDrawing) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;
        
        // クリックされた座標にあるアノテーションを検索
        for (let i = this.annotations.length - 1; i >= 0; i--) {
            const ann = this.annotations[i];
            const x = (ann.x_center - ann.width / 2) * this.image.naturalWidth * this.scale;
            const y = (ann.y_center - ann.height / 2) * this.image.naturalHeight * this.scale;
            const w = ann.width * this.image.naturalWidth * this.scale;
            const h = ann.height * this.image.naturalHeight * this.scale;
            
            if (clickX >= x && clickX <= x + w && clickY >= y && clickY <= y + h) {
                this.highlightAnnotation(ann.id);
                break;
            }
        }
    }
    
    drawCurrentBox(x1, y1, x2, y2) {
        this.ctx.strokeStyle = this.selectedLabelColor;
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        this.ctx.strokeRect(
            Math.min(x1, x2),
            Math.min(y1, y2),
            Math.abs(x2 - x1),
            Math.abs(y2 - y1)
        );
        this.ctx.setLineDash([]);
    }
    
    redraw() {
        console.log('redraw called');
        
        // キャンバスをクリア
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 画像が準備完了しているかチェック
        if (this.image && this.image.complete && this.image.naturalWidth > 0) {
            console.log('Drawing image to canvas');
            this.ctx.drawImage(this.image, 0, 0, this.canvas.width, this.canvas.height);
        } else {
            console.warn('Image not ready for drawing');
            // 読み込み中の表示
            this.ctx.fillStyle = '#f8f9fa';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.fillStyle = '#6c757d';
            this.ctx.font = '16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('画像を読み込み中...', this.canvas.width / 2, this.canvas.height / 2);
            this.ctx.textAlign = 'left';
            return; // 画像が読み込まれていない場合はアノテーションも描画しない
        }
        
        // 既存のアノテーションを描画
        this.annotations.forEach(ann => {
            this.drawAnnotation(ann);
        });
        
        console.log('redraw completed');
    }
    
    drawAnnotation(annotation) {
        if (!this.image || !this.image.naturalWidth) {
            return; // 画像が読み込まれていない場合は描画しない
        }
        
        // YOLO形式からキャンバス座標に変換
        const x = (annotation.x_center - annotation.width / 2) * this.image.naturalWidth * this.scale;
        const y = (annotation.y_center - annotation.height / 2) * this.image.naturalHeight * this.scale;
        const w = annotation.width * this.image.naturalWidth * this.scale;
        const h = annotation.height * this.image.naturalHeight * this.scale;
        
        // 矩形を描画
        this.ctx.strokeStyle = annotation.label_color;
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(x, y, w, h);
        
        // ラベル名を描画（背景付き）
        this.ctx.font = '14px Arial';
        const textMetrics = this.ctx.measureText(annotation.label_name);
        const textWidth = textMetrics.width;
        const textHeight = 14;
        
        // 背景を描画
        this.ctx.fillStyle = annotation.label_color;
        this.ctx.fillRect(x, y - textHeight - 4, textWidth + 8, textHeight + 4);
        
        // テキストを描画
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillText(annotation.label_name, x + 4, y - 4);
    }
    
    setSelectedLabel(labelId, labelName, labelColor) {
        this.selectedLabelId = labelId;
        this.selectedLabelName = labelName;
        this.selectedLabelColor = labelColor;
        
        document.getElementById('selected-label').textContent = labelName;
    }
    
    loadExistingAnnotations(annotations) {
        this.annotations = annotations;
        this.updateAnnotationsList();
        this.redraw();
    }
    
    updateAnnotationsList() {
        const listContainer = document.getElementById('annotations-list');
        listContainer.innerHTML = '';
        
        this.annotations.forEach((ann, index) => {
            const item = document.createElement('div');
            item.className = 'annotation-item';
            item.dataset.annotationId = ann.id;
            item.innerHTML = `
                <div class="annotation-label" style="color: ${ann.label_color};">
                    ${ann.label_name}
                </div>
                <div class="annotation-coords">
                    位置: (${(ann.x_center * 100).toFixed(1)}%, ${(ann.y_center * 100).toFixed(1)}%)
                    <span class="delete-annotation" onclick="annotationCanvas.deleteAnnotation(${ann.id})">×</span>
                </div>
            `;
            
            item.addEventListener('click', () => {
                this.highlightAnnotation(ann.id);
            });
            
            listContainer.appendChild(item);
        });
    }
    
    highlightAnnotation(annotationId) {
        // リスト内のハイライトを更新
        document.querySelectorAll('.annotation-item').forEach(item => {
            item.classList.remove('highlighted');
        });
        
        const item = document.querySelector(`[data-annotation-id="${annotationId}"]`);
        if (item) {
            item.classList.add('highlighted');
        }
    }
    
    deleteAnnotation(annotationId) {
        this.annotations = this.annotations.filter(ann => ann.id !== annotationId);
        this.updateAnnotationsList();
        this.redraw();
    }
    
    clearAllAnnotations() {
        this.annotations = [];
        this.updateAnnotationsList();
        this.redraw();
    }
    
    getAnnotationsForSave() {
        return this.annotations.map(ann => ({
            label_id: ann.label_id,
            x_center: ann.x_center,
            y_center: ann.y_center,
            width: ann.width,
            height: ann.height
        }));
    }
}

// アプリケーション初期化
let annotationCanvas;

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM読み込み完了');
    
    // データの存在確認
    if (typeof window.imageData === 'undefined') {
        console.error('imageData is not defined');
        alert('画像データの読み込みに失敗しました。ページを再読み込みしてください。');
        return;
    }
    
    if (typeof window.labelsData === 'undefined') {
        console.error('labelsData is not defined');
        alert('ラベルデータの読み込みに失敗しました。ページを再読み込みしてください。');
        return;
    }
    
    if (typeof window.existingAnnotations === 'undefined') {
        console.error('existingAnnotations is not defined');
        window.existingAnnotations = [];
    }
    
    // グローバル変数として設定
    window.imageData = window.imageData;
    window.labelsData = window.labelsData;
    window.existingAnnotations = window.existingAnnotations;
    
    console.log('画像データ:', window.imageData);
    console.log('ラベルデータ:', window.labelsData);
    console.log('既存アノテーション:', window.existingAnnotations);
    
    // アノテーションキャンバスを初期化
    annotationCanvas = new AnnotationCanvas('annotation-canvas');
    
    if (!annotationCanvas.canvas) {
        console.error('Canvas initialization failed');
        alert('キャンバスの初期化に失敗しました。');
        return;
    }
    
    // 画像を読み込み
    console.log('画像読み込み開始:', window.imageData.url);
    annotationCanvas.loadImage(window.imageData.url);
    
    // 既存のアノテーションを読み込み
    annotationCanvas.loadExistingAnnotations(window.existingAnnotations);
    
    // ラベルボタンのイベントリスナー（イベント委譲を使用）
    document.getElementById('label-buttons').addEventListener('click', function(e) {
        if (e.target.closest('.label-btn')) {
            const btn = e.target.closest('.label-btn');
            // アクティブ状態を更新
            document.querySelectorAll('.label-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 選択されたラベルを設定
            annotationCanvas.setSelectedLabel(
                parseInt(btn.dataset.labelId),
                btn.dataset.labelName,
                btn.dataset.labelColor
            );
        }
    });
    
    // 保存ボタン
    document.getElementById('save-btn').addEventListener('click', function() {
        const annotations = annotationCanvas.getAnnotationsForSave();
        
        this.disabled = true;
        this.textContent = '保存中...';
        
        fetch(`/api/save_annotations/${window.imageData.id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                annotations: annotations
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('保存しました');
            } else {
                alert('エラー: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('エラーが発生しました');
        })
        .finally(() => {
            this.disabled = false;
            this.textContent = '保存';
        });
    });
    
    // 全削除ボタン
    document.getElementById('clear-all-btn').addEventListener('click', function() {
        if (confirm('全てのアノテーションを削除しますか？')) {
            annotationCanvas.clearAllAnnotations();
        }
    });
    
    // ウィンドウリサイズ時の処理
    window.addEventListener('resize', function() {
        setTimeout(() => {
            annotationCanvas.resizeCanvas();
            annotationCanvas.redraw();
        }, 100);
    });
    
    // ラベル管理機能
    initLabelManagement();
});

// ラベル管理機能の初期化
function initLabelManagement() {
    let editingLabelId = null;
    
    // ラベル追加ボタン
    document.getElementById('add-label-btn').addEventListener('click', function() {
        editingLabelId = null;
        document.getElementById('labelModalLabel').textContent = 'ラベルを追加';
        document.getElementById('labelName').value = '';
        document.getElementById('labelColor').value = '#FF0000';
        new bootstrap.Modal(document.getElementById('labelModal')).show();
    });
    
    // ラベル編集ボタン
    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-label-btn')) {
            const btn = e.target.closest('.edit-label-btn');
            editingLabelId = btn.dataset.labelId;
            document.getElementById('labelModalLabel').textContent = 'ラベルを編集';
            document.getElementById('labelName').value = btn.dataset.labelName;
            document.getElementById('labelColor').value = btn.dataset.labelColor;
            new bootstrap.Modal(document.getElementById('labelModal')).show();
        }
    });
    
    // ラベル削除ボタン
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-label-btn')) {
            const btn = e.target.closest('.delete-label-btn');
            const labelName = btn.dataset.labelName;
            const labelId = btn.dataset.labelId;
            
            if (confirm(`ラベル「${labelName}」を削除しますか？\n※このラベルが使用されているアノテーションがある場合は削除できません。`)) {
                deleteLabel(labelId);
            }
        }
    });
    
    // ラベル保存ボタン
    document.getElementById('saveLabelBtn').addEventListener('click', function() {
        const name = document.getElementById('labelName').value.trim();
        const color = document.getElementById('labelColor').value;
        
        if (!name) {
            alert('ラベル名を入力してください');
            return;
        }
        
        if (editingLabelId) {
            updateLabel(editingLabelId, name, color);
        } else {
            addLabel(name, color);
        }
    });
}

// ラベル追加
function addLabel(name, color) {
    fetch('/api/add_label/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ name, color })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // ラベル一覧を更新
            addLabelToUI(data.label);
            // モーダルを閉じる
            bootstrap.Modal.getInstance(document.getElementById('labelModal')).hide();
            // グローバルラベルデータも更新
            window.labelsData.push(data.label);
        } else {
            alert('エラー: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('エラーが発生しました');
    });
}

// ラベル更新
function updateLabel(labelId, name, color) {
    fetch(`/api/update_label/${labelId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ name, color })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // ラベル一覧を更新
            updateLabelInUI(data.label);
            // モーダルを閉じる
            bootstrap.Modal.getInstance(document.getElementById('labelModal')).hide();
            // グローバルラベルデータも更新
            const labelIndex = window.labelsData.findIndex(l => l.id == labelId);
            if (labelIndex !== -1) {
                window.labelsData[labelIndex] = data.label;
            }
        } else {
            alert('エラー: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('エラーが発生しました');
    });
}

// ラベル削除
function deleteLabel(labelId) {
    fetch(`/api/delete_label/${labelId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // ラベル一覧から削除
            removeLabelFromUI(labelId);
            // グローバルラベルデータからも削除
            const labelIndex = window.labelsData.findIndex(l => l.id == labelId);
            if (labelIndex !== -1) {
                window.labelsData.splice(labelIndex, 1);
            }
            alert(data.message);
        } else {
            alert('エラー: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('エラーが発生しました');
    });
}

// UIにラベルを追加
function addLabelToUI(label) {
    const labelButtons = document.getElementById('label-buttons');
    const labelItem = document.createElement('div');
    labelItem.className = 'label-item d-flex align-items-center mb-2';
    labelItem.dataset.labelId = label.id;
    labelItem.innerHTML = `
        <button class="btn btn-outline-primary btn-sm me-2 label-btn flex-grow-1" 
                data-label-id="${label.id}" 
                data-label-name="${label.name}"
                data-label-color="${label.color}">
            <span class="color-indicator rounded-circle d-inline-block me-1" 
                  style="width: 12px; height: 12px; background-color: ${label.color};"></span>
            ${label.name}
        </button>
        <div class="btn-group">
            <button class="btn btn-outline-secondary btn-sm edit-label-btn" 
                    data-label-id="${label.id}"
                    data-label-name="${label.name}"
                    data-label-color="${label.color}"
                    title="編集">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-outline-danger btn-sm delete-label-btn" 
                    data-label-id="${label.id}"
                    data-label-name="${label.name}"
                    title="削除">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    labelButtons.appendChild(labelItem);
}

// UIのラベルを更新
function updateLabelInUI(label) {
    const labelItem = document.querySelector(`[data-label-id="${label.id}"]`);
    if (labelItem) {
        const labelBtn = labelItem.querySelector('.label-btn');
        const editBtn = labelItem.querySelector('.edit-label-btn');
        const deleteBtn = labelItem.querySelector('.delete-label-btn');
        const colorIndicator = labelBtn.querySelector('.color-indicator');
        
        // ボタンテキストと色を更新
        labelBtn.innerHTML = `
            <span class="color-indicator rounded-circle d-inline-block me-1" 
                  style="width: 12px; height: 12px; background-color: ${label.color};"></span>
            ${label.name}
        `;
        
        // データ属性を更新
        labelBtn.dataset.labelName = label.name;
        labelBtn.dataset.labelColor = label.color;
        editBtn.dataset.labelName = label.name;
        editBtn.dataset.labelColor = label.color;
        deleteBtn.dataset.labelName = label.name;
    }
}

// UIからラベルを削除
function removeLabelFromUI(labelId) {
    const labelItem = document.querySelector(`[data-label-id="${labelId}"]`);
    if (labelItem) {
        labelItem.remove();
    }
}

// CSRFトークンを取得する関数
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
