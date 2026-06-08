from dataclasses import dataclass
from typing import Any

from minio import Minio
from pyspark.sql import SparkSession


@dataclass
class BatchRunInputDateTime:
    """
    This model class gives broken-up date format structures
    """
    year: str
    month: str
    day: str
    hour: str
    minute: str


@dataclass
class BatchConfig:
    """
    This model class gives structure to store all required configurations
    for successful batch processing completion
    """
    # All required configurations
    minio_config: dict[str, Any]
    data_pipeline_config: dict[str, Any]
    postgres_config: dict[str, Any] | None  # TODO: For now, it is nullable

    spark_session: SparkSession
    minio_connection: Minio

    batch_run_date_time: BatchRunInputDateTime
