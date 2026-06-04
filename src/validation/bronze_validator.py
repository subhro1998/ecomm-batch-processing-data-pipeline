import logging

# Run basic validation for Bronze layer processor files
def validate_bronze_file(file_name, file_size, expected_file_extension: str) -> bool:
    if not file_name.endswith(expected_file_extension):
        logging.warning(f'File extension is not same with expected file extension: {expected_file_extension}')
        return False

    if file_size is None or file_size <= 0:
        logging.warning(f'File size is not same with expected file size: {file_size}')
        return False

    return True
