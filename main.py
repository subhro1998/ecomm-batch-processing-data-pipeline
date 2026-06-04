from datetime import datetime

from constants import common_constants as constant
from model.batch_inputs_model import BatchInput
from src.processor import batch_file_processor

import logging
from src.utils.logger_setup import setup_logging

# Initialize Logging level
setup_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.info('Starting batch processing')

    env = 'local'
    processing_layer = constant.BRONZE_LAYER
    #batch_run_date = datetime.today().strftime('%d-%m-%Y')  # Get today's date in DD-MM-YYYY format
    #batch_run_time = datetime.today().strftime("%H:%M")  # Get today's date in DD-MM-YYYY format
    source_system = 'finance_and_accounting'

    batch_run_date = '01-06-2026'
    batch_run_time = '00:00'
    batch_inputs = BatchInput(
        environment=env,
        batch_name=f'{processing_layer.upper()}_{source_system.upper()}',
        source_system=source_system,
        processing_layer=processing_layer,
        batch_run_date=batch_run_date,
        batch_run_time=batch_run_time
    )

    logger.info(f"Invoking processing for source system: {source_system}, processing layer: {processing_layer},"
                f"batch run date: {batch_run_date} for batch run time: {batch_run_time}")
    batch_file_processor.invoke_batch_processor(batch_inputs)
