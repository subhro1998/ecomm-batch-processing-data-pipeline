import logging

from constants import common_constants as constant


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

    logging.info("Minio config validated successfully")
    return True


def validate_data_pipeline_config(data_pipeline_config: dict,
                                  source_system: str) -> bool:
    """
    This function validates the data pipeline config read from the config file
    :param data_pipeline_config: Data pipeline config as Dictionary read from the config file
    :param source_system: Source system name from input
    :return: True if the configuration is valid, False otherwise
    """
    if not data_pipeline_config or data_pipeline_config is None or not isinstance(data_pipeline_config, dict):
        logging.error(f"Batch processor config file: {constant.DATA_PIPELINE_CONFIG_FILE} read failed, "
                      f"Stoping to process further")
        return False

    source_system_config_key = constant.CONFIG_KEY_SOURCE_SYSTEM + '.' + source_system
    source_system_config_exists = False
    for key in data_pipeline_config.keys():
        if key.startswith(source_system_config_key):
            source_system_config_exists = True
            break

    # Validate that the source system is configured
    if not source_system_config_exists:
        logging.error(f"Source system {source_system} is not in config file")
        return False

    return True
