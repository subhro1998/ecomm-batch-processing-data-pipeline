import pyspark.sql.functions as F
from pyspark.sql import Column

from src.constants import transformation_constants, global_constants

SPARK_TIME_PARSER_DEFAULT_DATE = "2000-01-01 "


def parse_date_column_values(column_name: str) -> Column:
    """
    This util function iterates through a provided column name
    and tries to convert the value into a supported date format

    :param column_name: Provided column name
    :return: Converted column date value
    """

    if not column_name or column_name is None:
        raise ValueError("Column name is required for date parsing")

    parse_attempts = [F.try_to_date(F.col(column_name), date_format)
                      for date_format in global_constants.SPARK_SUPPORTED_DATE_FORMATS]
    parse_attempts.append(F.try_to_date(F.col(column_name)))

    return F.coalesce(*parse_attempts)


def parse_time_column_values(column_name: str) -> Column:
    """
    This util function iterates through a provided column name
    and tries to convert the value into a supported time format

    :param column_name: Provided column name
    :return: Converted column time value
    """

    if not column_name or column_name is None:
        raise ValueError("Column name is required for time parsing")

    # Spark has no standalone TimeType, so parse onto a dummy date.
    parse_attempts = [F.try_to_timestamp(F.col(column_name), F.lit(time_format))
                      for time_format in global_constants.SPARK_SUPPORTED_TIME_FORMATS]
    parse_attempts.append(F.try_to_timestamp(F.col(column_name)))

    return F.coalesce(*parse_attempts)
