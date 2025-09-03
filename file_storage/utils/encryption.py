import os
from cryptography.fernet import Fernet
from ..models import EncryptedImage
from django.conf import settings

fernet = Fernet(settings.FERNET_KEY.encode())

def encrypt_bytes(data: bytes) -> bytes:
    return fernet.encrypt(data)

def decrypt_bytes(data: bytes) -> bytes:
    return fernet.decrypt(data)

    
def save_encrypted_image(uploaded_file, title):
    # Read bytes from UploadedFile
    img_bytes = uploaded_file.read()
    encrypted = encrypt_bytes(img_bytes)

    folder = os.path.join(settings.MEDIA_ROOT, "images")
    os.makedirs(folder, exist_ok=True)

    filename = f"{title}.bin"
    file_path = os.path.join(folder, filename)

    with open(file_path, "wb") as f:
        f.write(encrypted)

    return EncryptedImage.objects.create(title=title, file_path=file_path)


def get_decrypted_image(image: EncryptedImage):
    with open(image.file_path, "rb") as f:
        encrypted = f.read()

    img_bytes = decrypt_bytes(encrypted)

    return img_bytes