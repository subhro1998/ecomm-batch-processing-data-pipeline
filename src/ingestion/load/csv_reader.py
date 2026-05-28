from constants import common_constants as constants
from src.utils import setup as config_setup


class BronzeIngestionCSV:

    # Initialize required parameters
    def __init__(self, env: str) -> None:
        # Load minio config
        minio_config = config_setup.load_and_validate_minio_config(constants.MINIO_CONFIG_FILE)
        self.minio_config = minio_config

        # Initialize spark session with config
        spark = config_setup.initialize_spark_session(env, self.minio_config)
        self.spark = spark

    # Load CSV file from Minion bronze bucket
    def load_csv(self):
        csv_file_path_with_name = (constants.MINIO_SERVER_FILE_PATH
                         .format(bucket_name=self.minio_config.get(constants.MINIO_BUCKET_BRONZE_FILE_PATH)))

        if not isinstance(csv_file_path_with_name, str):
            raise TypeError(
                f"{constants.MINIO_BUCKET_BRONZE_FILE_PATH} must be a string, got {type(csv_file_path_with_name).__name__}"
            )

        df = self.spark.read.csv(csv_file_path_with_name, header=True, inferSchema=True)
        df.show()
