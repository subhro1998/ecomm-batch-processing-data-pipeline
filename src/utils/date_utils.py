import logging
from datetime import datetime

from src.constants import transformation_constants, global_constants
from src.model.batch_config_model import BatchRunInputDateTime


def construct_batch_run_datetime_model(batch_run_date: str, batch_run_time: str) -> BatchRunInputDateTime | None:
    """
    This function will construct batch run input datetime model
    :param batch_run_date:
    :param batch_run_time:
    :return: Constructed batch run input datetime model
    """

    try:
        yyyy_mm_dd_batch_run_date = convert_date_to_python_yyyy_mm_dd(batch_run_date)
        hh_mm_time = convert_time_to_python_hh_mm(batch_run_time)
        formatted_date = datetime.strptime(yyyy_mm_dd_batch_run_date, "%Y-%m-%d")
        formatted_time = datetime.strptime(hh_mm_time, "%H:%M")

        year = formatted_date.strftime("%Y")
        month = formatted_date.strftime("%m")
        day_of_month = formatted_date.strftime("%d")
        hour = formatted_time.strftime("%H")
        minute = formatted_time.strftime("%M")

        batch_run_time_details = BatchRunInputDateTime(
            year=year,
            month=month,
            day=day_of_month,
            hour=hour,
            minute=minute
        )
        return batch_run_time_details

    except ValueError as value_error:
        logging.error(f"Invalid date format: {batch_run_date} or invalid time format: {batch_run_time}\n"
                      f"Error details is: {value_error}")
        return None


def convert_date_to_python_yyyy_mm_dd(date_str: str) -> str:
    """
    This function will try to parse the provided date using common date formats and return a datetime object
    :param date_str: Date string in any date format
    :return: The parsed datetime object or else throws ValueError if date string is not parseable
    """

    if not date_str or date_str is None:
        raise ValueError(f"Provided date for conversion cannot be null or empty")

    for date_format in global_constants.SUPPORTED_PYTHON_DATE_FORMATS:
        try:
            datetime_obj = datetime.strptime(date_str.strip(), date_format)
            return datetime_obj.strftime(transformation_constants.PYTHON_DATE_FORMAT_YYYY_MM_DD)
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {date_str}")


def convert_time_to_python_hh_mm(time_str: str) -> str:
    """
    This function will try to parse the provided time using common time formats and return a time object
    :param time_str: Time string in any time format
    :return: The parsed time object or else throws ValueError if time string is not parseable
    """

    if not time_str or time_str is None:
        raise ValueError(f"Provided time cannot be null or empty")

    for time_format in global_constants.SUPPORTED_PYTHON_TIME_FORMATS:
        try:
            formatted_time = datetime.strptime(time_str.strip(), time_format)
            return formatted_time.strftime(transformation_constants.PYTHON_TIME_FORMAT_HH_MM)
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {time_str}")
