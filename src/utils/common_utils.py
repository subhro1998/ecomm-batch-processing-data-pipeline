import logging

from constants import common_constants as constant
from model.batch_config_model import BatchConfig
from model.batch_inputs_model import BatchInput


def construct_sub_folder(batch_input: BatchInput, batch_config: BatchConfig) -> str:
    """
    This utility method reads the sub folder template from minio config and converts into sub folder path
    :param batch_input: BatchInput object
    :param batch_config: BatchConfig object
    :return: The converted sub folder path
    """
    batch_run_datetime = batch_config.batch_run_date_time

    sub_folder_template = batch_config.minio_config[constant.MINIO_SUB_FOLDER_TEMPLATE_KEY]
    parent_source_directory = batch_config.data_pipeline_config[
        constant.FILE_SOURCE_PARENT_DIRECTORY_KEY.format(source_system=batch_input.source_system)]

    sub_folder_path = sub_folder_template.format(
        parent_source_directory=parent_source_directory,
        yyyy=batch_run_datetime.year,
        mm=batch_run_datetime.month,
        dd=batch_run_datetime.day,
        hhmm=f'{batch_run_datetime.hour}{batch_run_datetime.minute}'
    )

    logging.info(f'Converted subfolder template: {sub_folder_template} into sub folder path is {sub_folder_path}')
    return sub_folder_path
