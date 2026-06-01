import sys

from constants import common_constants as constants


# Validate Minio config
def validate_minio_config(minio_config, env: str):
    """
    This function validates the minio config read from the config files

    :param minio_config: Minio configs as Dictionary read from the config files
    :param env: Environment name
    """

    # Check if config not found
    if not minio_config or minio_config is None:
        print("Minio config not found")
        sys.exit(1)

    # Converted config is not dictionary
    if not isinstance(minio_config, dict):
        print("Minio config is not dictionary after conversion")
        sys.exit(1)

    # Validate specific configs #
    # Validate host
    host = minio_config.get(constants.MINIO_HOST_CONFIG_PATH.format(env=env))
    if not host or host is None or not isinstance(host, str):
        print("Either host not found or is not a string")
        sys.exit(1)

    # Validate Minio Username
    username = minio_config.get(constants.MINIO_USERNAME_CONFIG_PATH.format(env=env))
    if not username or username is None or not isinstance(username, str):
        print("Either username not found or is not a string")
        sys.exit(1)

    # Validate Minio user password
    minio_password = minio_config.get(constants.MINIO_USER_PASSWORD_CONFIG_PATH.format(env=env))
    if not minio_password or minio_password is None or not isinstance(minio_password, str):
        print("Either minio password not found or is not a string")
        sys.exit(1)

    # Validate File accessible -> True always
    file_accessible = minio_config.get(constants.MINIO_FILE_ACCESSIBLE_CONFIG_PATH.format(env=env))
    if not isinstance(file_accessible, bool):
        print("File accessible is not a boolean")
        sys.exit(1)

    # Validate SSL enabelment config
    ssl_enabled = bool(minio_config.get(constants.MINIO_SSL_CONFIG_PATH.format(env=env)))
    if not isinstance(ssl_enabled, bool):
        print("SSL Enabled config is not a boolean")
        sys.exit(1)

    print("Minio config validated successfully")
