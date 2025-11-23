# 🔐 Secure File Portal - Flask Application

A secure web application built with Flask that provides user authentication and **AES-256 encrypted file storage**. Files are automatically encrypted on upload and decrypted on download, ensuring data protection at rest.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🔑 Authentication & Access Control
- **Secure Login System** using Flask-Login
- **Password Hashing** with Werkzeug (bcrypt)
- **Session Management** with secure cookies
- **Protected Routes** requiring authentication

### 🔒 File Encryption
- **AES-256 Encryption** using PyCryptodome
- **CBC Mode** with unique IVs per file
- **Automatic Encryption** on upload
- **Automatic Decryption** on download
- **Secure Key Management** (development-ready)

### 🛡️ Security Features
- **Path Validation** prevents directory traversal attacks
- **Filename Sanitization** prevents injection attacks
- **File Size Limits** (16MB max)
- **Secure Session Handling**

### 🎨 Modern UI
- Responsive HTML/CSS/JavaScript interface
- User-friendly file upload/download interface
- Flash message notifications
- Clean, modern design

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/flask-secure-app.git
cd flask-secure-app
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

4. **Open your browser:**
```
http://localhost:5000
```

### Default Credentials

For testing purposes, the following accounts are available:

- **Username:** `admin` | **Password:** `admin123`
- **Username:** `user1` | **Password:** `password123`

⚠️ **Change these credentials before production use!**

## 📁 Project Structure

```
flask-secure-app/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── SECURITY_OVERVIEW.md        # Detailed encryption documentation
├── WALKTHROUGH_VIDEO_SCRIPT.md # Video walkthrough script
├── .gitignore                  # Git ignore rules
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── login.html             # Login page
│   └── dashboard.html         # File management dashboard
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Stylesheet
│   └── js/
│       └── main.js            # JavaScript
│
├── protected_files/            # Encrypted file storage (auto-created)
└── keys/                       # Encryption keys (auto-created)
```

## 🔐 Encryption Overview

The application uses **AES-256 (Advanced Encryption Standard)** in **CBC (Cipher Block Chaining)** mode to encrypt all uploaded files.

### How It Works

1. **Upload**: File is encrypted using AES-256 with a randomly generated IV
2. **Storage**: Encrypted file is saved with `.enc` extension
3. **Download**: File is decrypted on-the-fly and sent to the user

### Key Features

- **256-bit keys** (2^256 possible keys - computationally secure)
- **Unique IVs** per file (prevents pattern analysis)
- **PKCS7 Padding** (standard padding scheme)
- **Secure Key Generation** (cryptographically secure random)

For detailed information, see [SECURITY_OVERVIEW.md](SECURITY_OVERVIEW.md).

## 📖 Documentation

- **[README.md](README.md)** - This file (getting started guide)
- **[SECURITY_OVERVIEW.md](SECURITY_OVERVIEW.md)** - Detailed encryption and security documentation
- **[WALKTHROUGH_VIDEO_SCRIPT.md](WALKTHROUGH_VIDEO_SCRIPT.md)** - Video walkthrough script

## 🛠️ Technology Stack

- **Backend**: Flask 3.0
- **Authentication**: Flask-Login
- **Encryption**: PyCryptodome (AES-256)
- **Security**: Werkzeug (password hashing, filename sanitization)
- **Frontend**: HTML5, CSS3, JavaScript

## 🔒 Security Considerations

### ✅ Implemented

- Password hashing (bcrypt)
- AES-256 file encryption
- Path traversal prevention
- Filename sanitization
- Session-based authentication
- Secure secret key generation

### ⚠️ Production Recommendations

Before deploying to production, consider:

- [ ] Use a **database** instead of in-memory user storage
- [ ] Store encryption keys in a **Key Management Service** (AWS KMS, Azure Key Vault, etc.)
- [ ] Use **HTTPS** instead of HTTP
- [ ] Implement **rate limiting** on authentication endpoints
- [ ] Add **CSRF protection** to forms
- [ ] Set **security headers** (CSP, HSTS, X-Frame-Options, etc.)
- [ ] Use **environment variables** for secret keys
- [ ] Implement **comprehensive logging** and monitoring
- [ ] Add **file type validation**
- [ ] Implement **key rotation** policies
- [ ] Disable **debug mode**

See [SECURITY_OVERVIEW.md](SECURITY_OVERVIEW.md) for detailed security information.

## 🧪 Testing

### Manual Testing

1. **Login Test**: Verify authentication works with default credentials
2. **Upload Test**: Upload a file and verify it's encrypted
3. **Download Test**: Download a file and verify it decrypts correctly
4. **Security Test**: Try path traversal attacks (should be blocked)

### Security Testing

The application has been tested for:
- ✅ SQL Injection (not applicable - no database)
- ✅ XSS (Cross-Site Scripting)
- ✅ Path Traversal
- ✅ CSRF (needs improvement - see recommendations)
- ✅ Authentication Bypass

## 📝 Code Examples

### Encryption Function
```python
def encrypt_file(file_data):
    """Encrypt file data using AES-256"""
    key = get_encryption_key()  # 32-byte (256-bit) key
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv  # Random 16-byte IV
    padded_data = pad(file_data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return iv + encrypted_data  # IV + encrypted data
```

### Decryption Function
```python
def decrypt_file(encrypted_data):
    """Decrypt file data using AES-256"""
    key = get_encryption_key()
    iv = encrypted_data[:16]  # Extract IV
    ciphertext = encrypted_data[16:]  # Extract ciphertext
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, AES.block_size)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This is a **demonstration application** for educational purposes. While it implements strong security practices, it should be thoroughly reviewed and enhanced before use in production environments.

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Made with ❤️ using Flask and PyCryptodome**

