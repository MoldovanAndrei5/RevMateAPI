from utils.s3 import generate_presigned_upload_url

class UploadRepository:
    def generate_presigned_url(self, folder: str, file_name: str, content_type: str) -> dict:
        return generate_presigned_upload_url(
            folder=folder,
            file_name=file_name,
            content_type=content_type
        )