import logging

from minio import Minio
from pyspark.sql import SparkSession

from src.constants import common_constants
from src.utils import config_reader_utils as config_reader
from src.validation import config_validator as config_validator


# Initialize Spark session based on env and loaded minio config
def initialize_spark_session(env, minio_config: dict) -> SparkSession:
    """
    This function initializes the spark session
    :param env: Environment
    :param minio_config: Minio config dictionary
    :return: Initialized SparkSession
    """

    # Initialize spark session with config
    spark = (SparkSession.builder
             # Spark App Name
             .appName(common_constants.SPARK_APP_NAME)
             # Minio Host
             .config(common_constants.MINIO_HOST_CONFIG_KEY,
                     minio_config.get(common_constants.MINIO_HOST_CONFIG_PATH.format(env=env)))
             # Minio Username
             .config(common_constants.MINIO_USER_CONFIG_KEY,
                     minio_config.get(common_constants.MINIO_USERNAME_CONFIG_PATH.format(env=env)))
             # Minio user password
             .config(common_constants.MINIO_PASSWORD_CONFIG_KEY,
                     minio_config.get(common_constants.MINIO_USER_PASSWORD_CONFIG_PATH.format(env=env)))
             # Minio filesystem system -> S3A File System for now
             .config(common_constants.MINIO_FILE_SYSTEM_CONFIG_KEY,
                     common_constants.MINIO_CONFIG_VALUE_FILE_SYSTEM_S3AFILE_SYSTEM)
             # File accessible -> True always
             .config(common_constants.MINIO_FILE_ACCESSIBLE_CONFIG_KEY,
                     minio_config.get(common_constants.MINIO_FILE_ACCESSIBLE_CONFIG_PATH.format(env=env)))
             # SSL enablement config -> Boolean
             # Will be True for Https, should be False for Local
             .config(common_constants.MINIO_SSL_ENABLE_CONFIG_KEY,
                     minio_config.get(common_constants.MINIO_SSL_CONFIG_PATH.format(env=env)))
             # Extra JVM Executor options to read from Minio bucket
             .config(common_constants.JAVA_DRIVER_OPTIONS_KEY, common_constants.JAVA_DRIVER_OPTIONS_VALUE)
             .config(common_constants.JAVA_EXECUTOR_OPTIONS_KEY, common_constants.JAVA_EXECUTOR_OPTIONS_VALUE)
             # AWS / Minio Credentials and Packages for loading required packages and classes
             .config(common_constants.MINIO_AWS_CREDENTIALS_PROVIDER_KEY,
                     minio_config.get(common_constants.MINIO_AWS_CREDENTIALS_PROVIDER_CONFIG_VALUE))
             .config(common_constants.MINIO_AWS_SPARK_JAR_PACKAGES_KEY,
                     minio_config.get(common_constants.MINIO_AWS_SPARK_PACKAGES_CONFIG_VALUE))
             .getOrCreate()  # Get or create Spark Session
             )

    return spark


# Load minio client
def setup_minio_connection(env: str, minio_config: dict) -> Minio:
    """
    This function initializes the minio client
    :param env: Environment
    :param minio_config: Minio config dictionary
    :return: Minio connection
    """

    # Set up minio connection
    minio_connection = Minio(
        endpoint=minio_config[common_constants.MINIO_HOST_CONFIG_PATH.format(env=env)],
        access_key=minio_config[common_constants.MINIO_USERNAME_CONFIG_PATH.format(env=env)],
        secret_key=minio_config[common_constants.MINIO_USER_PASSWORD_CONFIG_PATH.format(env=env)],
        secure=minio_config[common_constants.MINIO_SSL_CONFIG_PATH.format(env=env)]
    )
    return minio_connection


# Load minio config
def load_and_validate_minio_config(env: str) -> dict | None:
    minio_config = config_reader.read_config(common_constants.MINIO_CONFIG_FILE)
    is_minio_config_valid = config_validator.validate_minio_config(minio_config, env)
    if minio_config is None or not is_minio_config_valid:
        logging.error(f'{common_constants.MINIO_CONFIG_FILE} location does not have Minio config or unable to load config')
        return None

    return minio_config
