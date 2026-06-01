import sys
from datetime import datetime

from constants import common_constants as constants
from files import minio_client
from src.utils import setup as config_setup


class BronzeIngestionCSV:
    """
    Class to load csv files, run basic validation and store in Bronze raw table
    """

    # Initialize required parameters
    def __init__(self, env: str):
        # Load minio config
        minio_config = config_setup.load_and_validate_minio_config(env)

        self.minio_config = minio_config

        # Initialize spark session with config
        spark = config_setup.initialize_spark_session(env, self.minio_config)
        self.spark = spark

    # Load CSV files from Minion bronze bucket
    def load_csv(self, env: str, batch_run_time: str):
        """
        This method is used to load csv files, run basic validation and store in Bronze raw table
        :param batch_run_time: Run time of the batch
        """

        today_str = datetime.today().strftime('%d-%m-%Y')  # Get today's date in DD-MM-YYYY format

        # Append bucket name with sub folder
        bucket_name = self.minio_config.get(constants.MINIO_BUCKET_BRONZE_FILE_PATH)
        bucket_with_subfolder = constants.BUCKER_NAME_WITH_SUBFOLDER_TEMPLATE.format(
            bucket_name=bucket_name,
            ingestion_date=today_str,
            batch_run_time=batch_run_time
        )

        file_path = (constants.MINIO_SERVER_FILE_PATH
                     .format(bucket_name_with_subfolder=bucket_with_subfolder))
        sub_folder = today_str + '/' + batch_run_time

        csv_file_name = minio_client.validate_bucket_and_get_file_name(
            env,
            self.minio_config,
            bucket_name,
            sub_folder,
            constants.FILE_EXTENSION_CSV
        )

        if csv_file_name is None:
            print(f'{file_path} location does not have files uploaded yet or files have some issues '
                  f'or could not pass basic quality check')
            sys.exit(1)

        # Load files into Spark data frame
        csv_file_path_with_name = file_path + '/' + csv_file_name # File absolute path
        df = (self.spark.read
              .option("header", True)
              .option("inferSchema", True)
              .csv(csv_file_path_with_name, header=True, inferSchema=True))

        df.show()
