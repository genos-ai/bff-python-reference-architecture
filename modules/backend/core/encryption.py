"""
Encryption utilities — AES-256-GCM for API key storage.

Usage:
    from modules.backend.core.encryption import encrypt, decrypt, load_encryption_key

    key = load_encryption_key()
    ciphertext, nonce = encrypt("my-api-key", key)
    plaintext = decrypt(ciphertext, nonce, key)
"""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from modules.backend.core.config import get_settings
from modules.backend.core.logging import get_logger

logger = get_logger(__name__)


def load_encryption_key() -> bytes:
    """Load the 32-byte encryption key from settings (base64-encoded)."""
    raw = get_settings().encryption_key
    if not raw:
        raise RuntimeError("ENCRYPTION_KEY not set in config/.env")
    key = base64.b64decode(raw)
    if len(key) != 32:
        raise RuntimeError(f"ENCRYPTION_KEY must decode to 32 bytes, got {len(key)}")
    return key


def encrypt(plaintext: str, key: bytes) -> tuple[bytes, bytes]:
    """Encrypt plaintext with AES-256-GCM. Returns (ciphertext, nonce)."""
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return ciphertext, nonce


def decrypt(ciphertext: bytes, nonce: bytes, key: bytes) -> str:
    """Decrypt ciphertext with AES-256-GCM. Returns plaintext string."""
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
