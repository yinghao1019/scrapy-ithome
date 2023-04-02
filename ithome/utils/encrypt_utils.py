# Get the value of the environment variable
import base64
import os

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

key = os.environ.get('ENCRYPT_KEY').encode()
iv = os.environ.get('ENCRYPT_IV').encode()


def encrypt(data: str) -> str:
    # Encrypt the password
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(data.encode(), AES.block_size))
    # Encode the ciphertext as base64
    return base64.b64encode(ciphertext).decode()


def decrypt(ciphertext: str) -> str:
    ciphertext = base64.b64decode(ciphertext.encode())
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    return ciphertext.decode()
