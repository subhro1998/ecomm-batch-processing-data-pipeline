import logging

from minio import Minio
from pyspark.sql import SparkSession

from constants import common_constants as constant
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
             .appName(constant.SPARK_APP_NAME)
             # Minio Host
             .config(constant.MINIO_HOST_CONFIG_KEY,
                     minio_config.get(constant.MINIO_HOST_CONFIG_PATH.format(env=env)))
             # Minio Username
             .config(constant.MINIO_USER_CONFIG_KEY,
                     minio_config.get(constant.MINIO_USERNAME_CONFIG_PATH.format(env=env)))
             # Minio user password
             .config(constant.MINIO_PASSWORD_CONFIG_KEY,
                     minio_config.get(constant.MINIO_USER_PASSWORD_CONFIG_PATH.format(env=env)))
             # Minio files system -> S3A File System for now
             .config(constant.MINIO_FILE_SYSTEM_CONFIG_KEY,
                     constant.MINIO_CONFIG_VALUE_FILE_SYSTEM_S3AFILE_SYSTEM)
             # File accessible -> True always
             .config(constant.MINIO_FILE_ACCESSIBLE_CONFIG_KEY,
                     minio_config.get(constant.MINIO_FILE_ACCESSIBLE_CONFIG_PATH.format(env=env)))
             # SSL enablement config -> Boolean
             # Will be True for Https, should be False for Local
             .config(constant.MINIO_SSL_ENABLE_CONFIG_KEY,
                     minio_config.get(constant.MINIO_SSL_CONFIG_PATH.format(env=env)))
             # Extra JVM Executor options to read from Minio bucket
             .config(constant.JAVA_DRIVER_OPTIONS_KEY, constant.JAVA_DRIVER_OPTIONS_VALUE)
             .config(constant.JAVA_EXECUTOR_OPTIONS_KEY, constant.JAVA_EXECUTOR_OPTIONS_VALUE)
             # AWS / Minio Credentials and Packages for loading required packages and classes
             .config(constant.MINIO_AWS_CREDENTIALS_PROVIDER_KEY,
                     minio_config.get(constant.MINIO_AWS_CREDENTIALS_PROVIDER_CONFIG_VALUE))
             .config(constant.MINIO_AWS_SPARK_JAR_PACKAGES_KEY,
                     minio_config.get(constant.MINIO_AWS_SPARK_PACKAGES_CONFIG_VALUE))
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
        endpoint=minio_config[constant.MINIO_HOST_CONFIG_PATH.format(env=env)],
        access_key=minio_config[constant.MINIO_USERNAME_CONFIG_PATH.format(env=env)],
        secret_key=minio_config[constant.MINIO_USER_PASSWORD_CONFIG_PATH.format(env=env)],
        secure=minio_config[constant.MINIO_SSL_CONFIG_PATH.format(env=env)]
    )
    return minio_connection


# Load minio config
def load_and_validate_minio_config(env: str) -> dict | None:
    minio_config = config_reader.read_config(constant.MINIO_CONFIG_FILE)
    is_minio_config_valid = config_validator.validate_minio_config(minio_config, env)
    if minio_config is None or not is_minio_config_valid:
        logging.error(f'{constant.MINIO_CONFIG_FILE} location does not have Minio config or unable to load config')
        return None

    return minio_config
