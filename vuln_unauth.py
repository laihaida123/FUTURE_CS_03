"""
漏洞版本1：未授权访问漏洞
移除所有JWT和登录验证，任何人都可以访问所有文件
端口：5001
"""

import os
import secrets
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import datetime

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'protected_files'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('keys', exist_ok=True)

def get_encryption_key():
    """获取加密密钥"""
    key_file = Path('keys/encryption_key.key')
    if key_file.exists():
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = get_random_bytes(32)
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

def encrypt_file(file_data):
    """加密文件"""
    key = get_encryption_key()
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    padded_data = pad(file_data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return iv + encrypted_data

def decrypt_file(encrypted_data):
    """解密文件"""
    key = get_encryption_key()
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, AES.block_size)

def is_safe_path(basedir, path):
    """路径验证"""
    try:
        resolved_path = Path(basedir).resolve() / path
        return Path(basedir).resolve() in resolved_path.parents or Path(basedir).resolve() == resolved_path.parent
    except (OSError, ValueError):
        return False

@app.route('/')
def index():
    return jsonify({'message': '漏洞版本：未授权访问，端口5001'})

# ========== 这里是漏洞：移除了所有认证 ==========
# 注意：没有token_required装饰器，也没有login端点
# 任何人都可以直接访问所有API

@app.route('/api/files', methods=['GET'])
def api_list_files():
    # 漏洞：不需要登录就可以查看文件列表
    files = []
    files_dir = Path(app.config['UPLOAD_FOLDER'])
    if files_dir.exists():
        for file_path in files_dir.glob('*.enc'):
            files.append({
                'name': file_path.stem,
                'size': file_path.stat().st_size,
                'encrypted_name': file_path.name
            })
    
    return jsonify({'files': files})

@app.route('/api/upload', methods=['POST'])
def api_upload_file():
    # 漏洞：不需要登录就可以上传文件
    if 'file' not in request.files:
        return jsonify({'message': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # 文件名清理（保留此安全功能）
    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({'message': 'Invalid filename'}), 400
    
    file_data = file.read()
    encrypted_data = encrypt_file(file_data)
    
    encrypted_filename = filename + '.enc'
    file_path = Path(app.config['UPLOAD_FOLDER']) / encrypted_filename
    
    # 路径验证（保留此安全功能）
    if not is_safe_path(app.config['UPLOAD_FOLDER'], encrypted_filename):
        return jsonify({'message': 'Invalid file path'}), 400
    
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)
    
    return jsonify({
        'message': f'File {filename} uploaded and encrypted successfully!',
        'success': True
    })

@app.route('/api/download/<filename>', methods=['GET'])
def api_download_file(filename):
    # 漏洞：不需要登录就可以下载文件
    safe_filename = secure_filename(filename)
    if not safe_filename or safe_filename != filename:
        return jsonify({'message': 'Invalid filename'}), 400
    
    encrypted_filename = safe_filename + '.enc'
    file_path = Path(app.config['UPLOAD_FOLDER']) / encrypted_filename
    
    if not is_safe_path(app.config['UPLOAD_FOLDER'], encrypted_filename):
        return jsonify({'message': 'Invalid file path'}), 400
    
    if not file_path.exists():
        return jsonify({'message': 'File not found'}), 404
    
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = decrypt_file(encrypted_data)
        
        from io import BytesIO
        file_obj = BytesIO(decrypted_data)
        file_obj.seek(0)
        
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'message': f'Error decrypting file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # 注意端口改为5001