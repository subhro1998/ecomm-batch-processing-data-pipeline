import logging

from src.constants import common_constants
from src.files import upload_transfer_file as transfer_file
from src.load import fetch_file_name, file_content_reader
from src.model.batch_config_model import BatchConfig
from src.model.batch_inputs_model import BatchInput
from src.utils import config_reader_utils, date_utils, common_utils
from src.utils import setup as config_setup
from src.validation import input_validator, config_validator


# Invoke batch processing
def invoke_batch_processor(batch_inputs: BatchInput):
    """
    This function invokes the batch processor according to the configuration and file type
    :param batch_inputs: Batch Input model
    :return: None
    """

    # Read and validate batch processing inputs
    is_valid_input = input_validator.validate_batch_processor_inputs(batch_inputs)
    if not is_valid_input:
        logging.error(f"Batch processor input validation failed")
        return None

    # Read, validate and create all required config & session data
    batch_config = load_and_validate_required_config(batch_inputs)
    if not batch_config or batch_config is None:
        logging.error(f"Batch processor input validation failed")
        return None

    source_file_type = batch_config.data_pipeline_config[
        common_constants.BATCH_SPECIFIC_CONFIG_RAW_FILE_TYPE_KEY.format(source_system=batch_inputs.source_system)]
    if (not source_file_type or source_file_type is None or not isinstance(source_file_type, str)
            or source_file_type not in [common_constants.FILE_EXTENSION_CSV, common_constants.FILE_EXTENSION_JSON,
                                        common_constants.FILE_EXTENSION_PARQUET]):
        logging.error(f"Source file type {source_file_type} is not processable as per current system")
        return None

    load_file_and_process(source_file_type, batch_inputs, batch_config)
    return None


# Load configuration and set in config_model object
def load_and_validate_required_config(batch_inputs: BatchInput) -> BatchConfig | None:
    """
    This function initializes the configurations required for the batch processor execution
    :return: BatchConfig object with all required configuration objcets or None in case of failure
    """

    # Read and validate pipeline config data
    data_pipeline_config = config_reader_utils.read_config(common_constants.DATA_PIPELINE_CONFIG_FILE)
    if data_pipeline_config is None:
        logging.error(f"Data pipeline config read failed")
        return None

    is_data_pipeline_config_valid = config_validator.validate_data_pipeline_config(
        data_pipeline_config, batch_inputs)
    if not is_data_pipeline_config_valid:
        logging.error(f"Data pipeline config validation failed")
        return None

    batch_run_date_time_model = date_utils.construct_batch_run_datetime_model(
        batch_inputs.batch_run_date, batch_inputs.batch_run_time)
    if batch_run_date_time_model is None:
        logging.error(f"Batch processor input validation failed")
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
        minio_connection=minio_connection,
        batch_run_date_time=batch_run_date_time_model
    )
    return batch_config


# Load the data from file, invoke transformation if required and upload file in separate bucket
def load_file_and_process(source_file_type: str, batch_inputs: BatchInput,
                          batch_config: BatchConfig) -> None:
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

    sub_folder = common_utils.construct_sub_folder(batch_inputs, batch_config)
    data_frame_file_content = file_content_reader.read_file_and_convert_into_data_frame(
        batch_inputs,
        batch_config,
        file_name,
        sub_folder,
        source_file_type
    )

    if data_frame_file_content is None:
        logging.error(f"Reading file content from: {file_name} failed")
        return None

    target_file_type = fetch_target_file_type(batch_inputs, batch_config.data_pipeline_config)
    if target_file_type is None:
        logging.error(f"Target file type is {target_file_type} failed")
        return None

    target_file_name = (f'{batch_inputs.source_system}_{batch_inputs.processing_layer}_'
                        f'{batch_config.batch_run_date_time.year}{batch_config.batch_run_date_time.month}'
                        f'{batch_config.batch_run_date_time.day}')
    logging.info(f"Constructed target file name: {target_file_name}")

    match batch_inputs.processing_layer.lower():
        case common_constants.BRONZE_LAYER:
            # TODO: Load into raw table
            source_bucket_name = batch_config.minio_config.get(
                common_constants.MINIO_BUCKET_FILE_PATH_CONFIG_KEY.format(
                    processing_layer=batch_inputs.processing_layer))
            if source_bucket_name is None or not isinstance(source_bucket_name, str):
                logging.error(f"Source bucket name is {source_bucket_name} not valid")
                return None

            transfer_file.upload_file_content_to_target(
                data_frame_file_content,
                common_constants.SILVER_LAYER,  # Upload the file in Silver layer for further processing
                batch_config.minio_config,
                sub_folder,
                target_file_name,
                batch_config.minio_connection
            )
            logging.info(f"Transfer complete for file: {file_name} "
                         f"at layer: {batch_inputs.processing_layer} is complete")
            return None

        case common_constants.SILVER_LAYER:
            # Invoke bronze -> silver transformation
            return None
        case common_constants.GOLD_LAYER:
            # Invoke Silver -> Gold transformation
            return None
        case _:
            logging.warning(f'{source_file_type} file type is not supported as of now')
            return None


def fetch_target_file_type(batch_inputs: BatchInput, data_pipeline_config: dict) -> str | None:
    """
    This method fetches target file type from batch_inputs based on processing layer
    :param batch_inputs:
    :param data_pipeline_config:
    :return: Fetched target file type or None in case not configured or not supported processing layer
    """

    source_system = batch_inputs.source_system
    processing_layer = batch_inputs.processing_layer
    target_file_type = None

    # Fetch the target file type based on Processing layer and source system
    match processing_layer.strip().lower():
        case common_constants.BRONZE_LAYER:
            target_file_type = data_pipeline_config[common_constants.BATCH_SPECIFIC_CONFIG_RAW_FILE_TYPE_KEY.format(
                source_system=source_system)]

        case common_constants.SILVER_LAYER:
            target_file_type = data_pipeline_config[common_constants.BATCH_SPECIFIC_CONFIG_RAW_FILE_TYPE_KEY.format(
                source_system=source_system)]

        case common_constants.GOLD_LAYER:
            target_file_type = data_pipeline_config[common_constants.BATCH_SPECIFIC_CONFIG_RAW_FILE_TYPE_KEY.format(
                source_system=source_system)]

        case '_':
            logging.error(f'Source system {source_system} not supported, unable to fetch target file type')
            return None

    logging.info(f"Fetched target file type for {source_system} layer is: {target_file_type}")
    return target_file_type
