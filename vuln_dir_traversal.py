"""
漏洞版本2：目录遍历漏洞
移除路径验证和文件名清理，可以尝试访问系统文件
端口：5002
"""

import os
import secrets
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'protected_files'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)

CORS(app, resources={r"/api/*": {"origins": "*"}})

login_manager = LoginManager()
login_manager.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('keys', exist_ok=True)

users = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'id': 1
    },
    'user1': {
        'password': generate_password_hash('password123'),
        'id': 2
    }
}

class User(UserMixin):
    def __init__(self, username, user_id):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    for username, user_data in users.items():
        if user_data['id'] == int(user_id):
            return User(username, user_data['id'])
    return None

def get_encryption_key():
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
    key = get_encryption_key()
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    padded_data = pad(file_data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return iv + encrypted_data

def decrypt_file(encrypted_data):
    key = get_encryption_key()
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, AES.block_size)

# ========== 这里是漏洞：总是返回True，不验证路径 ==========
def is_safe_path(basedir, path):
    """漏洞版本：总是允许任何路径"""
    return True  # 危险！允许任何路径访问

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
                
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User(data['username'], data['id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
            
        return f(current_user, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

@app.route('/')
def index():
    return jsonify({'message': '漏洞版本：目录遍历漏洞，端口5002'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    if username in users and check_password_hash(users[username]['password'], password):
        token = jwt.encode({
            'username': username,
            'id': users[username]['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'message': 'Login successful'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

@app.route('/api/files', methods=['GET'])
@token_required
def api_list_files(current_user):
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
@token_required
def api_upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # ========== 这里是漏洞：不使用secure_filename ==========
    # filename = secure_filename(file.filename)  # 注释掉这行
    filename = file.filename  # 使用原始文件名，可能包含../等危险字符
    
    if not filename:
        return jsonify({'message': 'Invalid filename'}), 400
    
    file_data = file.read()
    encrypted_data = encrypt_file(file_data)
    
    encrypted_filename = filename + '.enc'
    file_path = Path(app.config['UPLOAD_FOLDER']) / encrypted_filename
    
    # 这里is_safe_path总是返回True，所以任何路径都允许
    if not is_safe_path(app.config['UPLOAD_FOLDER'], encrypted_filename):
        return jsonify({'message': 'Invalid file path'}), 400
    
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)
    
    return jsonify({
        'message': f'File {filename} uploaded!',
        'success': True
    })

@app.route('/api/download/<filename>', methods=['GET'])
@token_required
def api_download_file(current_user, filename):
    # 漏洞：不检查文件名安全性
    # safe_filename = secure_filename(filename)  # 注释掉这行
    safe_filename = filename  # 使用原始文件名
    
    encrypted_filename = safe_filename + '.enc'
    file_path = Path(app.config['UPLOAD_FOLDER']) / encrypted_filename
    
    # 漏洞：路径验证总是通过
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
    app.run(debug=True, host='0.0.0.0', port=5002)