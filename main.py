from src.constants import common_constants
from src.model.batch_inputs_model import BatchInput
from src.processor import batch_file_processor

import logging
from src.utils.logger_setup import setup_logging

# Initialize Logging level
setup_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.info('Starting batch processing')

    env = 'local'
    source_system = 'sales_ledger'
    batch_processing_category = 'finance_and_accounting'
    processing_layer = common_constants.BRONZE_LAYER
    #batch_run_date = datetime.today().strftime('%d-%m-%Y')  # Get today's date in DD-MM-YYYY format
    #batch_run_time = datetime.today().strftime("%H:%M")  # Get today's date in DD-MM-YYYY format
    batch_category = 'finance_and_accounting'

    batch_run_date = '01-06-2026'
    batch_run_time = '00:00'
    batch_inputs = BatchInput(
        environment=env,
        batch_category=batch_category,
        batch_processing_category=batch_processing_category,
        source_system=source_system,
        processing_layer=processing_layer,
        batch_run_date=batch_run_date,
        batch_run_time=batch_run_time
    )

    logger.info(f"Invoking processing for source system: {source_system}, processing layer: {processing_layer},"
                f"batch run date: {batch_run_date} for batch run time: {batch_run_time}")
    batch_file_processor.invoke_batch_processor(batch_inputs)
