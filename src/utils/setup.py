import sys

from pyspark.sql import SparkSession
from constants import common_constants as constants
from src.utils import config_reader_utils as config_reader
from src.validation import config_validator as config_validator


# Initialize Spark session based on env and loaded minio config
def initialize_spark_session(env, minio_config: dict) -> SparkSession:
    # Initialize spark session with config
    spark = (SparkSession.builder
             # Spark App Name
             .appName(constants.SPARK_APP_NAME)
             # Minio Host
             .config(constants.MINIO_HOST_CONFIG_KEY,
                     minio_config.get(constants.MINIO_HOST_CONFIG_PATH.format(env=env)))
             # Minio Username
             .config(constants.MINIO_USER_CONFIG_KEY,
                     minio_config.get(constants.MINIO_USERNAME_CONFIG_PATH.format(env=env)))
             # Minio user password
             .config(constants.MINIO_PASSWORD_CONFIG_KEY,
                     minio_config.get(constants.MINIO_USER_PASSWORD_CONFIG_PATH.format(env=env)))
             # Minio file system -> S3A File System for now
             .config(constants.MINIO_FILE_SYSTEM_CONFIG_KEY,
                     constants.MINIO_CONFIG_VALUE_FILE_SYSTEM_S3AFILE_SYSTEM)
             # File accessible -> True always
             .config(constants.MINIO_FILE_ACCESSIBLE_CONFIG_KEY,
                     minio_config.get(constants.MINIO_FILE_ACCESSIBLE_CONFIG_PATH.format(env=env)))
             # SSL enablement config -> Boolean
             # Will be True for Https, should be False for Local
             .config(constants.MINIO_SSL_ENABLE_CONFIG_KEY,
                     minio_config.get(constants.MINIO_SSL_CONFIG_PATH.format(env=env)))

             .getOrCreate()  # Get or create Spark Session
             )

    return spark


# Load minio config
def load_and_validate_minio_config(env: str) -> dict:
    minio_config = config_reader.read_config(constants.MINIO_CONFIG_FILE)
    config_validator.validate_minio_config(minio_config, env)
    return minio_config
