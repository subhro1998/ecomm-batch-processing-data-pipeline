from src.constants import common_constants

COLUMN_NAME_VALIDATION_RESULT = "validation_result"
COLUMN_NAME_FAILED_COLUMNS = "failed_columns"
COLUMN_NAME_FAILURE_REASON = "validation_failure_reason"

VALIDATION_RESULT_SUCCESSFUL = "SUCCESSFUL"
VALIDATION_RESULT_FAILED = "FAILED"
VALIDATION_FAILURE_REASON_DUPLICATE = "DUPLICATE record based on SALES Ledger Deduplicate key"

SALES_LEDGER_DE_DUPLICATE_KEYS = ["ledger_id", "batch_id", "source_system", "source_file_name"]
SALES_LEDGER_ENUM_COLUMNS = ["entry_type", "currency", "payment_method", "channel", "region", "country_code"]
SALES_LEDGER_STRING_COLUMNS = ["entry_type", "currency", "payment_method", "channel", "region", "country_code"]
SALES_LEDGER_NOT_NULL_COLUMNS = ["ledger_id", "batch_id", "source_system", "created_at", "source_file_name"]

PYTHON_DATE_FORMAT_YYYY_MM_DD = "%Y-%m-%d"
PYTHON_TIME_FORMAT_HH_MM = "%H:%M"
SPARK_DATE_FORMAT_YYYY_MM_DD = "yyyy-MM-dd"
SPARK_TIME_FORMAT_HH_MM = "HH:mm"

CURRENCY_USD = "USD"
TRANSACTION_INFLOW = "INFLOW"
TRANSACTION_OUTFLOW = "OUTFLOW"
HIGH_VALUE_TXN_AMOUNT_THRESHOLD = 1000.0
OUTFLOW_TRANSACTION_TYPES = [
    common_constants.ENTRY_TYPE_REVERSAL_PAYMENT,
    "VENDOR_PAYABLE",
    "GOVT_TAX",
    "CAMPAIGN_PAYABLE"
]