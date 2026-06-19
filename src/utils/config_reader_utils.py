import logging

import yaml


def read_config(config_file_path: str) -> dict | None:
    """
    Method to read the config filesystem
    If filesystem not found or config is empty then stop the execution further

    :param config_file_path: Path to config filesystem
    :return: Config tree read from config filesystem
    """

    try:
        with open(config_file_path, 'r') as configFileContent:
            config = yaml.safe_load(configFileContent)
            if config is not None and isinstance(config, dict):
                flattened_config = flatten_dict(config)

                if flattened_config is not None:
                    return flattened_config
                else:
                    logging.error("Config tree is empty")
                    return None

    except FileNotFoundError:
        logging.error(f"Config filesystem not found in path: {config_file_path}")
        return None


def flatten_dict(dict_to_flatten, parent_key='', separator='.') -> dict:
    """
    Flatten dictionary until config tree's leaf level reached

    :raise NoConfigFoundException: if flattened dictionary is empty
    :param dict_to_flatten: Dictionary to flatten
    :param parent_key: Key till previous config tree level
    :param separator: Separator till config tree level

    :return: flattened dictionary
    """

    flattened_dict = {}
    for key, value in dict_to_flatten.items():
        updated_key = f'{parent_key}{separator}{key}' if parent_key else key

        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, updated_key, separator))
        else:
            flattened_dict[updated_key] = value

    if flattened_dict is None or not flattened_dict:
        raise Exception("Config tree is empty")

    return flattened_dict
