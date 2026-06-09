from pyspark.sql.types import (
    StructType, StructField, StringType, DateType,
    DecimalType, BooleanType, TimestampType
)

# Columns Silver must have before saving — non-negotiable
SALES_LEDGER_NOT_NULL_COLUMNS = [
    "ledger_id", "transaction_date", "transaction_time", "order_id",
    "customer_id", "debit_amount", "credit_amount", "net_amount", "currency",
    "exchange_rate", "source_system", "gross_amount", "batch_id", "created_at",
]

SILVER_SALES_LEDGER_SCHEMA = StructType([
    StructField("ledger_id", StringType(), False),
    StructField("transaction_date", DateType(), False),
    StructField("transaction_time", StringType(), False),
    StructField("fiscal_period", StringType(), True),
    StructField("entry_type", StringType(), True),
    StructField("order_id", StringType(), False),
    StructField("order_line_id", StringType(), True),
    StructField("customer_id", StringType(), False),
    StructField("product_id", StringType(), True),
    StructField("product_category", StringType(), True),
    StructField("account_code", StringType(), True),
    StructField("account_name", StringType(), True),
    StructField("debit_amount", DecimalType(20, 2), False),
    StructField("credit_amount", DecimalType(20, 2), False),
    StructField("net_amount", DecimalType(22, 2), False),
    StructField("currency", StringType(), False),
    StructField("exchange_rate", DecimalType(10, 6), False),
    StructField("usd_equivalent", DecimalType(18, 2), True),
    StructField("payment_method", StringType(), True),
    StructField("payment_reference", StringType(), True),
    StructField("channel", StringType(), True),
    StructField("region", StringType(), True),
    StructField("country_code", StringType(), True),
    StructField("country_name", StringType(), True),
    StructField("state_province", StringType(), True),
    StructField("tax_amount", DecimalType(18, 2), True),
    StructField("discount_amount", DecimalType(18, 2), True),
    StructField("gross_amount", DecimalType(22, 2), False),
    StructField("cost_of_goods", DecimalType(22, 2), True),
    StructField("campaign_id", StringType(), True),
    StructField("is_reconciled", BooleanType(), True),
    StructField("reconciliation_id", StringType(), True),
    StructField("reversal_reference", StringType(), True),
    StructField("posted_by", StringType(), True),
    StructField("created_at", TimestampType(), False),
    StructField("source_system", StringType(), False),
    StructField("batch_id", StringType(), False),
])
