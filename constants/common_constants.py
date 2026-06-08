# Spark config Key
SPARK_APP_NAME = 'batch-processing-data-pipeline'

# Minio config
MINIO_HOST_CONFIG_KEY = 'spark.hadoop.fs.s3a.endpoint'
MINIO_USER_CONFIG_KEY = 'spark.hadoop.fs.s3a.access.key'
MINIO_PASSWORD_CONFIG_KEY = 'spark.hadoop.fs.s3a.secret.key'
MINIO_FILE_ACCESSIBLE_CONFIG_KEY = 'spark.hadoop.fs.s3a.path.style.access'
MINIO_FILE_SYSTEM_CONFIG_KEY = 'spark.hadoop.fs.s3a.impl'
MINIO_SSL_ENABLE_CONFIG_KEY = 'spark.hadoop.fs.s3a.connection.ssl.enabled'  # Config value will be true for Https
MINIO_CONFIG_VALUE_FILE_SYSTEM_S3AFILE_SYSTEM = 'org.apache.hadoop.fs.s3a.S3AFileSystem'
MINIO_AWS_CREDENTIALS_PROVIDER_CONFIG_VALUE = 'minio.config.aws-minio-credential-provider'
MINIO_AWS_SPARK_PACKAGES_CONFIG_VALUE = 'minio.config.aws-minio-packages'

# Config files path
MINIO_CONFIG_FILE = 'config/minio_config.yml'
POSTGRES_CONFIG_FILE = 'config/postgres_config.yml'
DATA_PIPELINE_CONFIG_FILE = 'config/data_pipeline_config.yml'
LOGGING_CONFIG_FILE = 'config/logging_config.json'

# Environment specific minio config
MINIO_HOST_CONFIG_PATH = 'minio.config.environment-specific.{env}.host'
MINIO_USERNAME_CONFIG_PATH = 'minio.config.environment-specific.{env}.username'
MINIO_USER_PASSWORD_CONFIG_PATH = 'minio.config.environment-specific.{env}.password'
MINIO_FILE_ACCESSIBLE_CONFIG_PATH = 'minio.config.environment-specific.{env}.accessible'
MINIO_SSL_CONFIG_PATH = 'minio.config.environment-specific.{env}.ssl-enabled'
MINIO_SUB_FOLDER_TEMPLATE_KEY = 'minio.config.datetime_sub_folder_template'

# Minio Bucket related configs
MINIO_BUCKET_FILE_PATH_CONFIG_KEY = 'minio.config.bucket.{processing_layer}.name'
MINIO_SERVER_FILE_PATH = 's3a://{bucket_name_with_subfolder}'
BUCKET_NAME_WITH_SUBFOLDER_TEMPLATE = '{bucket_name}/{sub_directory}'
FULL_FILE_PATH_WITHOUT_BUCKET = '{sub_directory}/{file_name_with_extension}'

# Pipeline config
CONFIGURED_SOURCE_SYSTEMS_KEY = 'source_system.configured_source_systems'  # Value will be a List
ALL_CONFIGURED_SOURCE_CATEGORIES_KEY = 'source_system.source_categories'  # Value will be a List
FILE_SOURCE_PARENT_DIRECTORY_KEY = 'source_system.batch_specific_config.{source_system}.parent_source_directory'
BATCH_SPECIFIC_CONFIG_FILE_TYPE_KEY = 'source_system.batch_specific_config.{source_system}.raw_file_type'
BATCH_SPECIFIC_CONFIG_PROCESSING_CATEGORY_KEY = 'source_system.batch_specific_config.{source_system}.processing_category'
BATCH_SPECIFIC_CONFIG_BATCH_RUN_TIME_KEY = 'source_system.batch_specific_config.{source_system}.batch_run_time'

# Valid source systems
VALID_SOURCE_SYSTEMS = ['customer-data', 'inventory-updates', 'sales', 'notify-customer']

# File Extensions
FILE_EXTENSION_CSV = '.csv'
FILE_EXTENSION_JSON = '.json'
FILE_EXTENSION_PARQUET = '.parquet'

# Extra executor config for reading file from Minio bucket using Spark Hadoop
MINIO_AWS_CREDENTIALS_PROVIDER_KEY = 'spark.hadoop.fs.s3a.aws.credentials.provider'
MINIO_AWS_SPARK_JAR_PACKAGES_KEY = 'spark.jars.packages'
JAVA_DRIVER_OPTIONS_KEY = 'spark.driver.extraJavaOptions'
JAVA_DRIVER_OPTIONS_VALUE = '-Djava.security.manager=allow'
JAVA_EXECUTOR_OPTIONS_KEY = 'spark.executor.extraJavaOptions'
JAVA_EXECUTOR_OPTIONS_VALUE = '-Djava.security.manager=allow'

# Medallion Layers
BRONZE_LAYER = 'bronze'
SILVER_LAYER = 'silver'
GOLD_LAYER = 'gold'

# Source Systems
SOURCE_SYSTEM_FINANCE_AND_ACCOUNTING = 'finance_and_accounting'
SOURCE_SYSTEM_RETURN_AND_REFUND = 'returns_and_refund'
SOURCE_SYSTEM_SUPPLIER_FEEDS = 'supplier_feeds'
SOURCE_SYSTEM_SELLER_PERFORMANCE = 'seller_performance'
SOURCE_SYSTEM_CUSTOMER_UPDATES = 'customer_updates'
SOURCE_SYSTEM_INVENTORY_UPDATES = 'inventory_updates'

# Common date formats
SUPPORTED_DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
]
