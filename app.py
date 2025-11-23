"""
Flask Secure File Portal
=========================
A secure web application that provides user authentication and AES-256 encrypted file storage.
Files are automatically encrypted on upload and decrypted on download.

Security Features:
- AES-256 encryption (CBC mode) for file storage
- Password hashing with Werkzeug (bcrypt)
- Path validation to prevent directory traversal
- Filename sanitization
- Session-based authentication
"""

import os
import secrets
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import json

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'protected_files'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('keys', exist_ok=True)

# Simple user storage (in production, use a database)
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
    """Get or generate encryption key for file encryption"""
    key_file = Path('keys/encryption_key.key')
    if key_file.exists():
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = get_random_bytes(32)  # AES-256 requires 32 bytes
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

def encrypt_file(file_data):
    """
    Encrypt file data using AES-256 in CBC mode.
    
    Process:
    1. Get encryption key (32 bytes for AES-256)
    2. Create AES cipher in CBC mode (generates random IV)
    3. Pad data to AES block size (16 bytes)
    4. Encrypt padded data
    5. Return IV + encrypted data (IV needed for decryption)
    """
    key = get_encryption_key()
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv  # 16-byte Initialization Vector
    padded_data = pad(file_data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return iv + encrypted_data  # Format: [IV][Encrypted Data]

def decrypt_file(encrypted_data):
    """
    Decrypt file data using AES-256 in CBC mode.
    
    Process:
    1. Get encryption key
    2. Extract IV (first 16 bytes) and ciphertext (remaining bytes)
    3. Create AES cipher with same key and IV
    4. Decrypt ciphertext
    5. Remove padding to get original data
    """
    key = get_encryption_key()
    iv = encrypted_data[:16]  # Extract IV
    ciphertext = encrypted_data[16:]  # Extract encrypted data
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, AES.block_size)  # Remove PKCS7 padding

def is_safe_path(basedir, path):
    """Validate file path to prevent directory traversal attacks"""
    try:
        # Resolve the path to ensure it's absolute
        resolved_path = Path(basedir).resolve() / path
        # Ensure the resolved path is within the base directory
        return Path(basedir).resolve() in resolved_path.parents or Path(basedir).resolve() == resolved_path.parent
    except (OSError, ValueError):
        return False

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username]['password'], password):
            user = User(username, users[username]['id'])
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # List available files
    files = []
    files_dir = Path(app.config['UPLOAD_FOLDER'])
    if files_dir.exists():
        for file_path in files_dir.glob('*.enc'):
            files.append({
                'name': file_path.stem,  # filename without .enc extension
                'size': file_path.stat().st_size,
                'encrypted_name': file_path.name
            })
    
    return render_template('dashboard.html', files=files, username=current_user.username)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('dashboard'))
    
    # Secure filename
    filename = secure_filename(file.filename)
    if not filename:
        flash('Invalid filename', 'error')
        return redirect(url_for('dashboard'))
    
    # Read file data
    file_data = file.read()
    
    # Encrypt the file
    encrypted_data = encrypt_file(file_data)
    
    # Save encrypted file
    encrypted_filename = filename + '.enc'
    file_path = Path(app.config['UPLOAD_FOLDER']) / encrypted_filename
    
    # Validate path to prevent directory traversal
    if not is_safe_path(app.config['UPLOAD_FOLDER'], encrypted_filename):
        flash('Invalid file path', 'error')
        return redirect(url_for('dashboard'))
    
    with open(file_path, 'wb') as f:
        f.write(encrypted_data)
    
    flash(f'File {filename} uploaded and encrypted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    # Secure filename to prevent directory traversal
    safe_filename = secure_filename(filename)
    if not safe_filename or safe_filename != filename:
        flash('Invalid filename', 'error')
        return redirect(url_for('dashboard'))
    
    encrypted_filename = safe_filename + '.enc'
    file_path = Path(app.config['UPLOAD_FOLDER']) / encrypted_filename
    
    # Validate path to prevent directory traversal
    if not is_safe_path(app.config['UPLOAD_FOLDER'], encrypted_filename):
        flash('Invalid file path', 'error')
        return redirect(url_for('dashboard'))
    
    if not file_path.exists():
        flash('File not found', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Read encrypted file
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt the file
        decrypted_data = decrypt_file(encrypted_data)
        
        # Create a temporary file-like object
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
        flash(f'Error decrypting file: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # WARNING: debug=True should be False in production
    # Use a production WSGI server (Gunicorn, uWSGI) for production deployment
    app.run(debug=True, host='0.0.0.0', port=5000)

