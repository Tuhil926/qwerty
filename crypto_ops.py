from Crypto.Cipher import AES
import hashlib
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from qwerty_oauth import authenticate, find_file_id_by_name, download_file, QWERTY_FILENAME

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

def create_qwertyfile_if_not_exists():
    if not os.path.exists(QWERTY_FILENAME):
        try:
            drive_service = authenticate()
            file_id = find_file_id_by_name(drive_service, QWERTY_FILENAME)
            if not file_id:
                raise Exception("File not found on drive")
            download_file(drive_service, file_id, QWERTY_FILENAME)
        except:
            with open(QWERTY_FILENAME, "wb") as qwertyfile:
                init_data = MAGIC + '\n' + 'it\n' + 'works\n'
                pwd = "qwerty"
                qwertyfile.write(encrypt(init_data, pwd))
