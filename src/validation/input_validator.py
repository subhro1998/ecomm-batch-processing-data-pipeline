import logging
import re
from datetime import datetime

from constants import common_constants as constants
from model.batch_inputs_model import BatchInput

DATE_PATTERN_DD_MM_YYYY = re.compile(r"^\d{2}-\d{2}-\d{4}$")
TIME_PATTERN_HH_MM = re.compile(r"^\d{2}:\d{2}$")


def validate_batch_processor_inputs(batch_inputs: BatchInput) -> bool:
    """
    This function validates all the inputs of the batch processor
    :param batch_inputs Batch Input model
    :return: True if all inputs are valid, False otherwise
    """

    env = batch_inputs.environment
    # Validate if environment is within expected values
    if (not env or env is None
            or env.lower() not in ['local', 'dev', 'qa', 'uat', 'stage', 'prod']):
        logging.error(f"Environment variable: {env} does not fall under expected values")
        return False

    # Validate if the source_system is known or not
    source_system = batch_inputs.source_system
    if (not source_system or source_system is None
            or source_system.lower() not in [constants.SOURCE_SYSTEM_FINANCE_AND_ACCOUNTING,
                                             constants.SOURCE_SYSTEM_RETURN_AND_REFUND,
                                             constants.SOURCE_SYSTEM_SUPPLIER_FEEDS,
                                             constants.SOURCE_SYSTEM_SELLER_PERFORMANCE,
                                             constants.SOURCE_SYSTEM_CUSTOMER_UPDATES,
                                             constants.SOURCE_SYSTEM_INVENTORY_UPDATES]):

        logging.error(f"Invalid Source system: {source_system} provided, unable to process data")
        return False

    # Validate if batch run date is a Valid date in DD-MM-YYYY format
    batch_run_date = batch_inputs.batch_run_date
    if not batch_run_date or batch_run_date is None:
        logging.error("Batch run date is required, can't be empty or Null")
        return False
    elif not DATE_PATTERN_DD_MM_YYYY.fullmatch(batch_run_date):
        logging.error(f"Invalid date format: {batch_run_date}")
        return False
    else:
        try:
            datetime.strptime(batch_run_date, "%d-%m-%Y")
        except ValueError:
            logging.error(f"Invalid date format: {batch_run_date}")
            return False

    # Validate if batch run time is a Valid time of the day (24 hrs format) in HH:MM format
    batch_run_time = batch_inputs.batch_run_time
    if not batch_run_time or batch_run_time is None:
        return False
    elif not TIME_PATTERN_HH_MM.fullmatch(batch_run_time):
        logging.error(f"Invalid time format: {batch_run_time}")
        return False
    else:
        try:
            datetime.strptime(batch_run_time, "%H:%M")
        except ValueError:
            logging.error(f"Invalid time format: {batch_run_time}")
            return False

    # Validate if processing_layer is within expected values
    processing_layer = batch_inputs.processing_layer
    if (not processing_layer or processing_layer is None
            or processing_layer.lower() not in [constants.BRONZE_LAYER, constants.SILVER_LAYER, constants.GOLD_LAYER]):
        logging.error(f"Invalid processing layer provided: {processing_layer}")
        return False

    # Since all values are valid, returning true
    return True
