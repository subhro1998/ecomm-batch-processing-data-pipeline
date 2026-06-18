COLUMN_NAME_VALIDATION_RESULT = "validation_result"
COLUMN_NAME_FAILED_COLUMNS = "faild_columns"
COLUMN_NAME_FAILURE_REASON = "validation_failure_reason"

VALIDATION_RESULT_SUCCESSFUL = "SUCCESSFUL"
VALIDATION_RESULT_FAILED = "FAILED"
VALIDATION_FAILURE_REASON_DUPLICATE = "DUPLICATE record based on SALES Ledger Deduplicate key"

SALES_LEDGER_DE_DUPLICATE_KEYS = ["ledger_id", "batch_id", "source_system", "created_at", "source_file_name"]
SALES_LEDGER_ENUM_COLUMNS = ["entry_type", "currency", "payment_method", "channel", "region", "country_code"]
SALES_LEDGER_STRING_COLUMNS = ["entry_type", "currency", "payment_method", "channel", "region", "country_code"]
SALES_LEDGER_NOT_NULL_COLUMNS = ["ledger_id", "batch_id", "source_system", "created_at", "source_file_name"]

DATE_FORMAT_YYYY_MM_DD = "%Y-%m-%d"
SPARK_DATE_FORMAT_YYYY_MM_DD = "yyyy-MM-dd"
SPARK_TIME_FORMAT_HH_MM = "HH-MM"
TIME_FORMAT_HH_MM = "%H:%M"