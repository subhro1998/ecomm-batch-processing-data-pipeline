import sys
from pyspark.sql import SparkSession

from constants import common_constants as constants
from src.utils import config_reader_utils as config_reader
from src.validation import config_validator as config_validator


# Initialize Spark session based on env and loaded minio config
def initialize_spark_session(env, minio_config: dict) -> SparkSession:
    # Initialize spark session with config
    # If rerunning inside the same interpreter, make sure no old Spark session survives
    try:
        if SparkSession.getActiveSession() is not None:
            SparkSession.getActiveSession().stop()
    except Exception:
        pass

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
             # Minio files system -> S3A File System for now
             .config(constants.MINIO_FILE_SYSTEM_CONFIG_KEY,
                     constants.MINIO_CONFIG_VALUE_FILE_SYSTEM_S3AFILE_SYSTEM)
             # File accessible -> True always
             .config(constants.MINIO_FILE_ACCESSIBLE_CONFIG_KEY,
                     minio_config.get(constants.MINIO_FILE_ACCESSIBLE_CONFIG_PATH.format(env=env)))
             # SSL enablement config -> Boolean
             # Will be True for Https, should be False for Local
             .config(constants.MINIO_SSL_ENABLE_CONFIG_KEY,
                     minio_config.get(constants.MINIO_SSL_CONFIG_PATH.format(env=env)))
             # Extra JVM Executor options to read from Minio bucket
             .config(constants.JAVA_DRIVER_OPTIONS_KEY, constants.JAVA_DRIVER_OPTIONS_VALUE)
             .config(constants.JAVA_EXECUTOR_OPTIONS_KEY, constants.JAVA_EXECUTOR_OPTIONS_VALUE)
             # AWS / Minio Credentials and Packages for loading required packages and classes
             .config(constants.MINIO_AWS_CREDENTIALS_PROVIDER_KEY,
                    minio_config.get(constants.MINIO_AWS_CREDENTIALS_PROVIDER_CONFIG_VALUE))
             .config(constants.MINIO_AWS_SPARK_JAR_PACKAGES_KEY,
                     minio_config.get(constants.MINIO_AWS_SPARK_PACKAGES_CONFIG_VALUE))
             .getOrCreate()  # Get or create Spark Session
             )

    return spark


# Load minio config
def load_and_validate_minio_config(env: str) -> dict:
    minio_config = config_reader.read_config(constants.MINIO_CONFIG_FILE)
    config_validator.validate_minio_config(minio_config, env)
    if minio_config is None:
        print(f'{constants.MINIO_CONFIG_FILE} location does not have Minio config or unable to load config')
        sys.exit(1)

    return minio_config
