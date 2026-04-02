import os
import uuid
import shutil
from fastapi import UploadFile

def save_uploaded_file(upload_file: UploadFile) -> str:
    """
    将上传文件保存到临时目录，并返回保存后的绝对路径。
    """
    upload_dir = os.path.join(os.getcwd(), "data", "temp_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(upload_file.filename)[1] or ".zip"
    file_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, file_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)

    return file_path
