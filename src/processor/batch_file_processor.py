import logging

from constants import common_constants as constant
from files import copy_and_transfer_file as transfer_file
from model.batch_config_model import BatchConfig
from model.batch_inputs_model import BatchInput
from src.load import fetch_file_name, file_content_reader
from src.utils import config_reader_utils
from src.utils import setup as config_setup
from src.validation import input_validator, config_validator


# Invoke batch processing
def invoke_batch_processor(batch_inputs: BatchInput):
    """
    This function invokes the batch processor according to the configuration and file type
    :param batch_inputs: Batch Input model
    :return: None
    """

    # Read and validate batch procesing inputs
    is_valid_input = input_validator.validate_batch_processor_inputs(batch_inputs)
    if not is_valid_input:
        logging.error(f"Batch processor input validation failed")
        return None

    # Read, validate and create all required config & session data
    batch_config = load_and_validate_required_config(batch_inputs)
    if not batch_config or batch_config is None:
        logging.error(f"Batch processor input validation failed")
        return None

    source_file_type = batch_config.data_pipeline_config.get(
        constant.CONFIG_KEY_SOURCE_FILE_TYPE.format(source_system=batch_inputs.source_system))
    if (not source_file_type or source_file_type is None or not isinstance(source_file_type, str)
            or source_file_type not in [constant.FILE_EXTENSION_CSV, constant.FILE_EXTENSION_JSON,
                                        constant.FILE_EXTENSION_PARQUET]):
        logging.error(f"Source file type {source_file_type} is not processable as per current system")
        return None

    load_file_and_process(source_file_type, batch_inputs, batch_config)


# Load configuration and set in config_model object
def load_and_validate_required_config(batch_inputs: BatchInput) -> BatchConfig | None:
    """
    This function initializes the configurations required for the batch processor execution
    :return: BatchConfig object with all required configuration objcets or None in case of failure
    """

    # Read and validate pipeline config data
    data_pipeline_config = config_reader_utils.read_config(constant.DATA_PIPELINE_CONFIG_FILE)
    is_data_pipeline_config_valid = config_validator.validate_data_pipeline_config(
        data_pipeline_config, batch_inputs.source_system)
    if not is_data_pipeline_config_valid:
        logging.error(f"Data pipeline config validation failed")
        return None

    # Load and validate minio config
    minio_config = config_setup.load_and_validate_minio_config(batch_inputs.environment)
    if minio_config is None:
        logging.error(f"Minio config validation failed")
        return None

    # Fetch spark session
    spark_session = config_setup.initialize_spark_session(batch_inputs.environment, minio_config)
    minio_connection = config_setup.setup_minio_connection(batch_inputs.environment, minio_config)
    if minio_connection is None or spark_session is None:
        logging.error(f'Minio client or spark session setup is incomplete, can not process data')
        return None

    batch_config = BatchConfig(
        minio_config=minio_config,
        data_pipeline_config=data_pipeline_config,
        postgres_config=None,  # TODO: read & populate later
        spark_session=spark_session,
        minio_connection=minio_connection
    )
    return batch_config


# Load the data from file, invoke transfomrmation if required and upload file in separate bucket
def load_file_and_process(source_file_type: str, batch_inputs: BatchInput,
                          batch_config: BatchConfig):
    """
    This method loads file and reads as data frame and invoke further processing based on the processing layer
    :param source_file_type: Source file type (Extension)
    :param batch_inputs: Batch Input model
    :param batch_config: Batch Config model
    :return: None
    """
    # Switch case of file type for processing further
    file_name = fetch_file_name.fetch_processing_file_name(source_file_type, batch_inputs, batch_config)
    if file_name is None:
        logging.error(f"Processing file {file_name} failed")
        return None

    data_frame_file_content = file_content_reader.read_file_and_convert_into_data_frame(
        batch_inputs,
        batch_config,
        file_name,
        source_file_type
    )

    if data_frame_file_content is None:
        logging.error(f"Reading file content from: {file_name} failed")
        return None

    match batch_inputs.processing_layer.lower():
        case constant.BRONZE_LAYER:
            # TODO: Load into raw table
            source_bucket_name = batch_config.minio_config.get(constant.MINIO_BUCKET_FILE_PATH.format(
                processing_layer=batch_inputs.processing_layer))
            minio_object_file_path = constant.MINIO_OBJECT_NAME_WITHOUT_BUCKET.format(
                ingestion_date=batch_inputs.batch_run_date,
                batch_run_time=batch_inputs.batch_run_time,
                file_name_with_extension=file_name
            )

            transfer_file.transfer_copied_file_to_target(
                constant.SILVER_LAYER,  # Transfer the file in Silver layer for next processing
                batch_config.minio_config,
                source_bucket_name,
                minio_object_file_path,
                batch_config.minio_connection
            )
            logging.info(f"Transfer complete for file: {file_name} "
                         f"at layer: {batch_inputs.processing_layer} is complete")

        case constant.SILVER_LAYER:
            # Invoke bronze -> silver transfomration
            pass
        case constant.GOLD_LAYER:
            # Invoke Silver -> Gold transformation
            pass
        case _:
            logging.warning(f'{file_extension} file type is not supported as of now')
            return None
