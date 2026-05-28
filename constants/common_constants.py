# Spark config Key
SPARK_APP_NAME = 'batch-processing-data-pipeline'
MINIO_HOST_CONFIG_KEY = 'spark.hadoop.fs.s3a.endpoint'
MINIO_USER_CONFIG_KEY = 'spark.hadoop.fs.s3a.access.key'
MINIO_PASSWORD_CONFIG_KEY = 'spark.hadoop.fs.s3a.secret.key'
MINIO_FILE_ACCESSIBLE_CONFIG_KEY = 'spark.hadoop.fs.s3a.path.style.access'
MINIO_FILE_SYSTEM_CONFIG_KEY = 'spark.hadoop.fs.s3a.impl'
MINIO_SSL_ENABLE_CONFIG_KEY = 'spark.hadoop.fs.s3a.connection.ssl.enabled' # Config value will be true for Https
MINIO_CONFIG_VALUE_FILE_SYSTEM_S3AFILE_SYSTEM = 'S3AFileSystem'

# Config file path
MINIO_CONFIG_FILE = 'config/minio-config.yml'
POSTGRES_CONFIG_FILE = 'config/postgres-config.yml'

# Environment specific minio config
MINIO_HOST_CONFIG_PATH = 'minio.config.environment-specific.{env}.host'
MINIO_USERNAME_CONFIG_PATH = 'minio.config.environment-specific.{env}.username'
MINIO_USER_PASSWORD_CONFIG_PATH = 'minio.config.environment-specific.{env}.password'
MINIO_FILE_ACCESSIBLE_CONFIG_PATH = 'minio.config.environment-specific.{env}.accessible'
MINIO_SSL_CONFIG_PATH = 'minio.config.environment-specific.{env}.ssl'

# Minio Bucket
MINIO_BUCKET_BRONZE_FILE_PATH = 'minio.config.bucket.bronze.name'
MINIO_BUCKET_COMPLETED_FILE_PATH = 'minio.config.bucket.completed.name'
MINIO_SERVER_FILE_PATH = 's3a://{bucket_name}/data/{csv_file_name}'