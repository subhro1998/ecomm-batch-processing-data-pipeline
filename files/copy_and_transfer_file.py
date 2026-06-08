import logging

from minio import Minio
from minio.commonconfig import CopySource

from constants import common_constants as constant


def transfer_copied_file_to_target(file_target_layer: str, minio_config: dict,
                                   source_bucket_name: str,
                                   file_name_with_sub_folder: str,
                                   minio_connection: Minio) -> None:
    """
    This method is used to copy and transfer the file into other upstream buckets.
    :param file_target_layer: Target bucket / layer to where file should be transferred
    :param minio_config: Minio config dictionary
    :param source_bucket_name: Source bucket name
    :param file_name_with_sub_folder: Source file name with sub folder
    :param minio_connection: Minio connection object
    :return: None
    """

    # Create target bucket if not exists
    target_bucket = minio_config.get(constant.MINIO_BUCKET_FILE_PATH_CONFIG_KEY.format(processing_layer=file_target_layer))
    if target_bucket is None or not isinstance(target_bucket, str):
        logging.error(f"Target bucket name: {target_bucket} is invalid, transfer is cancelled")
        return None

    if not minio_connection.bucket_exists(target_bucket):
        minio_connection.make_bucket(target_bucket)

    result = minio_connection.copy_object(
        target_bucket,
        file_name_with_sub_folder,
        CopySource(source_bucket_name, file_name_with_sub_folder)
    )

    logging.info(f"File successfully transferred to {target_bucket}/{file_name_with_sub_folder}. "
                 f"E-Tag for source file {file_name_with_sub_folder}: is {result.etag}")
    return None  # Explicit return statement
