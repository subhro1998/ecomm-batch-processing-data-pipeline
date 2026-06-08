import logging
from datetime import datetime

from constants import common_constants as constant
from model.batch_config_model import BatchRunInputDateTime


def construct_batch_run_datetime_model(batch_run_date: str, batch_run_time: str) -> BatchRunInputDateTime | None:
    """
    This function will construct batch run input datetime model
    :param batch_run_date:
    :param batch_run_time:
    :return: Constructed batch run input datetime model
    """

    try:
        yyyy_mm_dd_batch_run_date = convert_date_to_yyyy_mm_dd(batch_run_date)
        formatted_date = datetime.strptime(yyyy_mm_dd_batch_run_date, "%Y-%m-%d")
        formatted_time = datetime.strptime(batch_run_time, "%H:%M")

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


def convert_date_to_yyyy_mm_dd(date_str: str) -> str:
    """
    This function will try to parse the provided date using common date formats and return a datetime object
    :param date_str: Date string in any date format
    :return: The parsed datetime object
    """
    for formats in constant.SUPPORTED_DATE_FORMATS:
        try:
            datetime_obj = datetime.strptime(date_str.strip(), formats)
            return datetime_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {date_str}")