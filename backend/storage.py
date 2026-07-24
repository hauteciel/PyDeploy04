# 파일 저장소 추상화 모듈.
# STORAGE_BACKEND 환경변수에 따라 로컬 디스크(dev) 또는 S3(prod)에 파일을 저장/조회합니다.
# controllers.py는 이 모듈의 함수만 호출하면 되고, 백엔드가 어디서 도는지는 신경 쓸 필요가 없습니다.

import os
from urllib.parse import quote

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")  # local | s3
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "upload")
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)

_s3_client = None
if STORAGE_BACKEND == "s3":
    import boto3

    _s3_client = boto3.client("s3", region_name=AWS_REGION)
else:
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file(unique_filename: str, content: bytes) -> None:
    """업로드된 파일 바이트를 저장소(local 디스크 또는 S3)에 기록합니다."""
    if STORAGE_BACKEND == "s3":
        _s3_client.put_object(Bucket=AWS_S3_BUCKET, Key=unique_filename, Body=content)
    else:
        with open(os.path.join(UPLOAD_DIR, unique_filename), "wb") as f:
            f.write(content)


def file_exists(unique_filename: str) -> bool:
    """저장소에 실제 파일이 존재하는지 확인합니다."""
    if STORAGE_BACKEND == "s3":
        from botocore.exceptions import ClientError

        try:
            _s3_client.head_object(Bucket=AWS_S3_BUCKET, Key=unique_filename)
            return True
        except ClientError:
            return False
    return os.path.exists(os.path.join(UPLOAD_DIR, unique_filename))


def get_local_path(unique_filename: str) -> str:
    """local 백엔드에서 FileResponse에 넘길 실제 파일 경로를 반환합니다."""
    return os.path.join(UPLOAD_DIR, unique_filename)


def get_presigned_url(unique_filename: str, expires_in: int = 300, download_name: str | None = None) -> str:
    """s3 백엔드에서 다운로드/조회용 임시 서명 URL을 발급합니다.

    download_name을 지정하면, S3에 UUID로 저장된 실제 Key와 무관하게
    브라우저가 해당 이름(예: 원본 파일명)으로 다운로드하도록 강제합니다.
    """
    params = {"Bucket": AWS_S3_BUCKET, "Key": unique_filename}

    if download_name:
        try:
            download_name.encode("ascii")
            content_disposition = f'attachment; filename="{download_name}"'
        except UnicodeEncodeError:
            # 한글 등 비-ASCII 파일명은 RFC 5987 형식(filename*)으로 인코딩
            content_disposition = f"attachment; filename*=UTF-8''{quote(download_name)}"
        params["ResponseContentDisposition"] = content_disposition

    return _s3_client.generate_presigned_url(
        "get_object",
        Params=params,
        ExpiresIn=expires_in,
    )
