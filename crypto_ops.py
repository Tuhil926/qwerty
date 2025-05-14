from Crypto.Cipher import AES
import hashlib
import os

QWERTY_FILENAME = "qwerty.txt"
MAGIC = "qwertyuiopasdfghjklzxcvbnm"
start_hash = None
end_hash = None

def encrypt(text: str, pwd: str):
    salt = os.urandom(AES.block_size)
    key = hashlib.sha256(salt + pwd.encode('utf-8')).digest()
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    return salt + iv + cipher.encrypt(text.encode('utf-8'))


def decrypt(data: bytes, pwd: str):
    salt = data[:AES.block_size]
    key = hashlib.sha256(salt + pwd.encode('utf-8')).digest()
    iv = data[AES.block_size:2 * AES.block_size]
    ciphertext = data[2 * AES.block_size:]
    decrypt_cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    return decrypt_cipher.decrypt(ciphertext).decode('utf-8')

def try_decrypt(pwd):
    global start_hash
    enc_file = open(QWERTY_FILENAME, 'rb')
    data = enc_file.read()
    enc_file.close()
    try:
        decrypted = decrypt(data, pwd)
    except:
        return None
    start_hash = hashlib.sha256(decrypted.encode('utf-8')).digest()
    lines = decrypted.split('\n')
    if lines[0] != MAGIC:
        return None
    entries = []
    for i in range(1, len(lines), 2):
        if i + 1 >= len(lines):
            break
        entries.append((lines[i], lines[i + 1]))
    return entries

def save_entries(text, pwd):
    global end_hash
    enc_data = encrypt(MAGIC + '\n' + text, pwd)
    with open(QWERTY_FILENAME, 'wb') as qwerty_file:
        qwerty_file.write(enc_data)
    end_hash = hashlib.sha256((MAGIC + '\n' + text).encode('utf-8')).digest()
    return start_hash != end_hash

try:
    file = open(QWERTY_FILENAME, "r")
    file.close()
except FileNotFoundError:
    qwertfile = open(QWERTY_FILENAME, "wb")
    init_data = MAGIC + '\n' + 'it\n' + 'works\n'
    pwd = "qwerty"
    qwertfile.write(encrypt(init_data, pwd))
    qwertfile.close()

