from minio import Minio
from minio.error import S3Error

from constants import common_constants as constant
from src.validation import bronze_validator


def validate_bucket_and_get_file_name(env: str, minio_config: dict,
                                      bucket_name: str, sub_folder: str,
                                      file_extension: str) -> str | None:
    """
    This method fetches the required files and content from the minio bucket.
    And if the files is in required format then returns the content of the files else returns None.

    :param env: Environment name
    :param minio_config: Minio config dictionary
    :param bucket_name: Minio bucket name
    :param sub_folder: Sub folder path
    :param file_extension: Expected files extension
    :return: None if validation is not successful and files content if files successfully passes the validation
    """

    response = None
    try:
        # Set up minio connection
        minio_conn = Minio(
            endpoint=minio_config[constant.MINIO_HOST_CONFIG_PATH.format(env=env)],
            access_key=minio_config[constant.MINIO_USERNAME_CONFIG_PATH.format(env=env)],
            secret_key=minio_config[constant.MINIO_USER_PASSWORD_CONFIG_PATH.format(env=env)],
            secure=minio_config[constant.MINIO_SSL_CONFIG_PATH.format(env=env)]
        )

        if not minio_conn.bucket_exists(bucket_name):
            raise Exception(f"The bucket {bucket_name} does not exist")

        if sub_folder is None or not sub_folder:
            raise Exception(f"The sub folder path {sub_folder} does not exist")

        all_files_and_objects = minio_conn.list_objects(bucket_name=bucket_name,
                                                        prefix=sub_folder,
                                                        recursive=True)
        for file_object in all_files_and_objects:
            if file_object.is_dir:
                continue

            if not file_object.object_name.endswith(file_extension):
                continue
            else:
                file_name = file_object.object_name
                if file_name.startswith(f"{sub_folder}/"):
                    print('Removing file sub folder details from minio object name')
                    file_name = file_name[len(sub_folder) + 1:]

                file_size = file_object.size
                #response = minio_conn.get_object(bucket_name, file_name)

                # Run necessary validation
                is_valid = bronze_validator.validate_bronze_file(file_name, file_size,
                                                                 file_extension)
                if is_valid:
                    print(f'File {file_name} is valid, processing it')
                    return file_name

        # Unable to find files with provided details satisfying conditions
        print(f'No matching {file_extension} file found in path {bucket_name}/{sub_folder}')
        return None

    #except S3Error as e:
    #    print(f"Error: {e}")
    #    return None

    finally:
        if response is not None:
            response.close()
            response.release_conn()
