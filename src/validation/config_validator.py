import logging

from constants import common_constants as constant
from model.batch_inputs_model import BatchInput


# Validate Minio config
def validate_minio_config(minio_config, env: str) -> bool:
    """
    This function validates the minio config read from the config files

    :param minio_config: Minio configs as Dictionary read from the config files
    :param env: Environment name
    """

    # Check if config not found
    if not minio_config or minio_config is None:
        logging.error("Minio config not found")
        return False

    # Converted config is not dictionary
    if not isinstance(minio_config, dict):
        logging.error("Minio config is not dictionary after conversion")
        return False

    # Validate specific configs #
    # Validate host
    host = minio_config.get(constant.MINIO_HOST_CONFIG_PATH.format(env=env))
    if not host or host is None or not isinstance(host, str):
        logging.error("Either host not found or is not a string")
        return False

    # Validate Minio Username
    username = minio_config.get(constant.MINIO_USERNAME_CONFIG_PATH.format(env=env))
    if not username or username is None or not isinstance(username, str):
        logging.error("Either username not found or is not a string")
        return False

    # Validate Minio user password
    minio_password = minio_config.get(constant.MINIO_USER_PASSWORD_CONFIG_PATH.format(env=env))
    if not minio_password or minio_password is None or not isinstance(minio_password, str):
        logging.error("Either minio password not found or is not a string")
        return False

    # Validate File accessible -> True always
    file_accessible = minio_config.get(constant.MINIO_FILE_ACCESSIBLE_CONFIG_PATH.format(env=env))
    if not isinstance(file_accessible, bool):
        logging.error("File accessible is not a boolean")
        return False

    # Validate SSL enablement config
    ssl_enabled = bool(minio_config.get(constant.MINIO_SSL_CONFIG_PATH.format(env=env)))
    if not isinstance(ssl_enabled, bool):
        logging.error("SSL Enabled config is not a boolean")
        return False

    # Validate if sub folder config is present
    sub_folder_template = minio_config.get(constant.MINIO_SUB_FOLDER_TEMPLATE_KEY)
    if not sub_folder_template or sub_folder_template is None or not isinstance(sub_folder_template, str) :
        logging.error(f"Sub folder template key {sub_folder_template} is not valid")
        return False

    logging.info("Minio config validated successfully")
    return True


def validate_data_pipeline_config(data_pipeline_config: dict,
                                  batch_input: BatchInput) -> bool:
    """
    This function validates the data pipeline config read from the config file
    :param data_pipeline_config: Data pipeline config as Dictionary read from the config file
    :param batch_input: Provided batch input
    :return: True if the configuration is valid, False otherwise
    """
    if (not data_pipeline_config or data_pipeline_config is None
            or not isinstance(data_pipeline_config, dict)):
        logging.error(f"Batch processor config file: {constant.DATA_PIPELINE_CONFIG_FILE} read failed, "
                      f"Stoping to process further")
        return False

    # Validate if the source system is configured
    configured_source_systems = data_pipeline_config[constant.CONFIGURED_SOURCE_SYSTEMS_KEY]
    if (not isinstance(configured_source_systems, list) or len(configured_source_systems) == 0
            or batch_input.source_system not in configured_source_systems):
        logging.error(f"Source system {batch_input.source_system} is not in configured yet")
        return False

    # Validate if batch name and incoming file for upstream system is configured for processing
    configured_batch_upstream_category = data_pipeline_config[constant.ALL_CONFIGURED_SOURCE_CATEGORIES_KEY]
    if (not isinstance(configured_batch_upstream_category, list) or len(configured_batch_upstream_category) == 0
            or batch_input.batch_category not in configured_batch_upstream_category):
        logging.error(f"Batch name {batch_input.batch_category} is not in configured yet")
        return False

    # Validate if required batch specific config is present
    # 1. Validate parent_source_directory
    # 2. Validate processing_category
    # 3. Validate batch_run_time
    # 4. Validate raw_file_type
    parent_source_directory = data_pipeline_config[
        constant.FILE_SOURCE_PARENT_DIRECTORY_KEY.format(source_system=batch_input.source_system)]
    if parent_source_directory is None or not isinstance(parent_source_directory, str):
        logging.error(f"Sub directory {parent_source_directory} is not configured properly")
        return False

    processing_category = data_pipeline_config[
        constant.BATCH_SPECIFIC_CONFIG_PROCESSING_CATEGORY_KEY.format(source_system=batch_input.source_system)]
    if processing_category is None or not isinstance(processing_category, str):
        logging.error(f"Processing category {processing_category} is not configured properly")
        return False

    configured_batch_run_times = data_pipeline_config[
        constant.BATCH_SPECIFIC_CONFIG_BATCH_RUN_TIME_KEY.format(source_system=batch_input.source_system)]
    if (configured_batch_run_times is None or not isinstance(configured_batch_run_times, list)
            or len(configured_batch_run_times) == 0):
        logging.error(f"Batch run times {configured_batch_run_times} is not configured properly")
        return False

    raw_file_type = data_pipeline_config[
        constant.BATCH_SPECIFIC_CONFIG_RAW_FILE_TYPE_KEY.format(source_system=batch_input.source_system)]
    if raw_file_type is None or not isinstance(raw_file_type, str):
        logging.error(f"Source raw file type {raw_file_type} is not configured properly")
        return False

    return True
