import logging

from constants import common_constants as constant
from files import minio_client
from model.batch_config_model import BatchConfig
from model.batch_inputs_model import BatchInput


def fetch_processing_file_name(file_type: str, batch_input: BatchInput,
                               batch_config: BatchConfig) -> str | None:
    """
    This method is used to fetch processing file name, to be propagated for processing it
    :param file_type: type of file to be fetched and processed
    :param batch_input: BatchInput model
    :param batch_config: BatchConfig model
    :return: The processing file name
    """

    # Append bucket name with sub folder and validate configured bucket name is string
    bucket_name = batch_config.minio_config.get(constant.MINIO_BUCKET_FILE_PATH.format(
        processing_layer=batch_input.processing_layer))
    if bucket_name is None or not bucket_name or not isinstance(bucket_name, str):
        logging.error(
            f'Bucket name: {bucket_name} is not in valid string format for {batch_input.processing_layer} layer')
        return None

    # the sub folder based on processing layer & bucket in which intended file should be present
    sub_folder = constant.ONLY_SUBFOLDER_TEMPLATE_WITHOUT_FILE_NAME.format(
        sub_directory=batch_config.data_pipeline_config.get(
            constant.SOURCE_FILE_SUB_DIRECTORY_KEY.format(source_system=batch_input.source_system)),
        ingestion_date=batch_input.batch_run_date,
        batch_run_time=batch_input.batch_run_time
    )

    file_name = minio_client.connect_minio_and_fetch_file(
        batch_config.minio_connection,
        bucket_name,
        sub_folder,
        file_type
    )

    return file_name
