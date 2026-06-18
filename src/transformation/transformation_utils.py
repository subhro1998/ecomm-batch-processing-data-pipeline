import pyspark.sql.functions as F
from pyspark.sql import Column

from src.constants import transformation_constants, common_constants

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

    parsed_date = F.coalesce(
        *[
            F.to_date(F.trim(F.col(column_name)), date_format)
            for date_format in common_constants.SUPPORTED_DATE_FORMATS
        ]
    )
    return F.date_format(parsed_date, transformation_constants.SPARK_DATE_FORMAT_YYYY_MM_DD)


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
    parsed_date_time = F.coalesce(*[
        F.to_timestamp(
            F.concat(F.lit(SPARK_TIME_PARSER_DEFAULT_DATE),
                     F.trim(F.col(column_name))),
            f"{transformation_constants.SPARK_DATE_FORMAT_YYYY_MM_DD} {time_format}"
        )
        for time_format in common_constants.SUPPORTED_TIME_FORMATS
    ])

    return F.date_format(parsed_date_time, transformation_constants.SPARK_TIME_FORMAT_HH_MM)
