import logging

from pyspark.sql import DataFrame

from constants import common_constants as constants
from model.batch_config_model import BatchConfig
from model.batch_inputs_model import BatchInput


# Load CSV files from configured minio bucket
def read_file_and_convert_into_data_frame(batch_input: BatchInput, batch_config: BatchConfig,
                                          file_name: str, file_extension: str) -> DataFrame | None:
    """
    This method is used to load csv files, run basic validation and store in Bronze raw table
    It uses the attached Batch Input model for connecting to minio and fetching the file
    :return: The csv file name along with data frame or None in case of failure
    """

    minio_config = batch_config.minio_config
    spark = batch_config.spark_session

    # Append bucket name with sub folder and validate configured bucket name is string
    bucket_name = minio_config.get(constants.MINIO_BUCKET_FILE_PATH.format(
        processing_layer=batch_input.processing_layer))
    if bucket_name is None or not bucket_name or not isinstance(bucket_name, str):
        logging.error(
            f'Bucket name: {bucket_name} is not in valid string format for {batch_input.processing_layer} layer')
        return None

    # Fetch batch run date & time, file path & sub folder based on processing layer & bucket
    batch_run_date = batch_input.batch_run_date
    batch_run_time = batch_input.batch_run_time
    bucket_with_subfolder = constants.BUCKET_NAME_WITH_SUBFOLDER_TEMPLATE.format(
        bucket_name=bucket_name,
        ingestion_date=batch_run_date,
        batch_run_time=batch_run_time
    )
    file_path = constants.MINIO_SERVER_FILE_PATH.format(bucket_name_with_subfolder=bucket_with_subfolder)
    if file_name is None or not file_name.endswith(file_extension):
        logging.error(f'File name: {file_name} is either not provided '
                      f'or not matching with the file extension: {file_extension}')
        return None

    # Load files into Spark data frame
    file_path_with_name = f'{file_path}/{file_name}'  # File absolute path
    df = None  # Initialize the data frame
    match file_extension:
        case constants.FILE_EXTENSION_CSV:
            df = (spark.read
                  .option("header", True)
                  .option("inferSchema", True)
                  .csv(file_path_with_name, header=True, inferSchema=True))
        case constants.FILE_EXTENSION_PARQUET:
            df = (spark.read
                  .option("header", True)
                  .option("inferSchema", True)
                  .parquet(file_path_with_name, header=True, inferSchema=True))
        case constants.FILE_EXTENSION_JSON:
            df = (spark.read
                  .option("header", True)
                  .option("inferSchema", True)
                  .json(file_path_with_name))
        case _:
            logging.warning(f'{file_extension} file type is not supported as of now')
            return None

    return df
