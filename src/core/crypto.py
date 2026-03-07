"""
加密工具模块
使用Fernet对称加密保护敏感数据
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ENCRYPTION_KEY_FILE = "data/.secret_key"
SALT_FILE = "data/.salt"


def _get_or_create_key() -> bytes:
    """获取或创建加密密钥"""
    data_dir = os.path.dirname(ENCRYPTION_KEY_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
    
    key = Fernet.generate_key()
    with open(ENCRYPTION_KEY_FILE, 'wb') as f:
        f.write(key)
    
    os.chmod(ENCRYPTION_KEY_FILE, 0o600)
    
    return key


def _get_or_create_salt() -> bytes:
    """获取或创建盐值"""
    data_dir = os.path.dirname(SALT_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, 'rb') as f:
            return f.read()
    
    salt = os.urandom(16)
    with open(SALT_FILE, 'wb') as f:
        f.write(salt)
    
    os.chmod(SALT_FILE, 0o600)
    
    return salt


_fernet_instance = None


def _get_fernet() -> Fernet:
    """获取Fernet实例"""
    global _fernet_instance
    if _fernet_instance is None:
        key = _get_or_create_key()
        _fernet_instance = Fernet(key)
    return _fernet_instance


def encrypt_value(plain_text: str) -> str:
    """加密字符串"""
    if not plain_text:
        return ""
    
    fernet = _get_fernet()
    encrypted = fernet.encrypt(plain_text.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_value(encrypted_text: str) -> str:
    """解密字符串"""
    if not encrypted_text:
        return ""
    
    try:
        fernet = _get_fernet()
        encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Decryption failed: {e}")
        return encrypted_text


def is_encrypted(value: str) -> bool:
    """检查值是否已加密"""
    if not value:
        return False
    
    try:
        decoded = base64.b64decode(value.encode('utf-8'))
        return len(decoded) > 0 and decoded.startswith(b'gAAAA')
    except Exception:
        return False
