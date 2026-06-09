import logging

from minio import Minio
from pyspark.sql import DataFrame

from constants import common_constants as constant


def upload_file_content_to_target(data_frame: DataFrame, file_target_layer: str,
                                  minio_config: dict, parent_system_sub_folder: str,
                                  target_file_name: str, minio_connection: Minio) -> None:
    """
    This method converts the data frame into provided format and upload the file into target location.

    :param data_frame: The data_frame to be transferred
    :param file_target_layer: Target bucket / layer to where file should be transferred
    :param minio_config: Minio config dictionary
    :param parent_system_sub_folder: Parent system's sub folder
    :param target_file_name: Target file name
    :param minio_connection: Minio connection object
    :return: None
    """

    if data_frame is None:
        logging.error("No non-null data frame provided")
        return None

    # Create target bucket if not exists
    target_bucket = minio_config.get(
        constant.MINIO_BUCKET_FILE_PATH_CONFIG_KEY.format(processing_layer=file_target_layer))
    if target_bucket is None or not isinstance(target_bucket, str):
        logging.error(f"Target bucket name: {target_bucket} is invalid, transfer is cancelled")
        return None

    if not minio_connection.bucket_exists(target_bucket):
        minio_connection.make_bucket(target_bucket)

    target_file_nme_with_dir = f'{target_bucket}/{parent_system_sub_folder}/{target_file_name}'
    target_file_location_full_path = constant.MINIO_SERVER_FILE_PATH \
        .format(bucket_name_with_subfolder=target_file_nme_with_dir)

    # Write the data frame as per configured target file format for next layer
    data_frame.write \
        .mode("overwrite") \
        .parquet(target_file_location_full_path)

    logging.info(f"File successfully transferred to {target_file_location_full_path}")
    return None  # Explicit return statement
