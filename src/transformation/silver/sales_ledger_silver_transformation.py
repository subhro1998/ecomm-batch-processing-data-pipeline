from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType, BooleanType
from pyspark.sql.window import Window

from src.constants import transformation_constants, common_constants, global_constants
from src.model.batch_inputs_model import BatchInput
from src.schema import financial_data_system_schemas
from src.transformation import transformation_utils


def process_sales_ledger_data_silver(batch_inputs: BatchInput, df: DataFrame) -> None:
    # Step 1: add some necessary columns in the raw data
    df = add_necessary_derived_columns(df)

    # Step 2: Deduplicate records based on sales ledger natural keys
    unique_df, duplicates_df = deduplicate_sales_ledger_data(df)

    # 2nd step: Separate data that failed & passed the Silver layer validation
    quarantined_df, valid_df = categorize_sales_ledger_data_validity(batch_inputs, unique_df)

    # Step 3: Combine duplicate data and validation failed data and quarantine them to analyze further
    # records_to_quarantine = duplicates_df.unionByName(quarantined_df, allowMissingColumns=True)
    # save_and_upload_bad_records(records_to_quarantine)

    # Step 4: Type case data types and date time format to make the data uniform
    # valid_df = type_cast_sales_ledger_data(valid_df)

    # Step 5: Enrich the cleansed valid records, fill None values as per pre-decided strategy
    enriched_and_cleansed_df = enrich_sales_ledger_data(valid_df)
    enriched_and_cleansed_df.show()

    return None


def add_necessary_derived_columns(raw_df: DataFrame) -> DataFrame:
    parsed_date = transformation_utils.parse_date_column_values("transaction_date")
    parsed_time = transformation_utils.parse_time_column_values("transaction_time")

    return raw_df \
        .withColumn("silver_processed_at", F.current_timestamp()) \
        .withColumn("_parsed_txn_date", parsed_date) \
        .withColumn("_parsed_txn_time", parsed_time)


# Quarantine the validation failed records to analyze later (should upload as a file & save in DB -> both)
def categorize_sales_ledger_data_validity(batch_inputs: BatchInput, df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """
    This method tags the original sales ledger data based on pre-configured keys,
    figures out the validation failure reasons and columns that is not passing the check

    :param batch_inputs: Batch Input model
    :param df: Original sales ledger data frame
    :return: A tuple of the
             quarantined sales ledger data frame containing only the data that failed validations along with the reasons
             and the valid sales ledger records data frame
    """

    created_at_timestamp_col = F.trim(F.col("created_at").cast("string"))
    created_at_parse_expr = F.coalesce(
        *[F.try_to_timestamp(created_at_timestamp_col, F.lit(timestamp_format))
          for timestamp_format in global_constants.SPARK_TIMESTAMP_FORMATS]
    )

    validation_rules_list = [
        (
            F.col("source_system") != F.lit(batch_inputs.source_system),
            "INVALID_SOURCE_SYSTEM",
            ["source_system"]
        ),
        (
            F.col("transaction_date").isNull() | F.col("transaction_time").isNotNull(),
            "NULL_TXN_DATE_OR_TIME",
            ["transaction_date", "transaction_time"]
        ),
        (
            F.col("_parsed_txn_date").isNull() | F.col("_parsed_txn_time").isNull(),
            "NOT_PARSABLE_DATE_OR_TIME_FORMAT",
            ["transaction_date", "transaction_time"]
        ),
        (
            F.col("created_at").isNotNull()
            & (created_at_timestamp_col != "")
            & created_at_parse_expr.isNull(),
            "BAD_TIMESTAMP_OF_CREATED_AT_COLUMN",
            ["created_at"]
        ),
        (
            ~F.upper(F.col("currency")).isin(*global_constants.ALLOWED_CURRENCIES),
            "INVALID_CURRENCY",
            ["currency"]
        ),
        (
            (F.col("debit_amount") < 0) | F.col("debit_amount").isNull(),
            "NEGATIVE_DEBIT_AMOUNT",
            ["debit_amount"]
        ),
        (
            (F.col("credit_amount") < 0) | F.col("credit_amount").isNull(),
            "NEGATIVE_CREDIT_AMOUNT",
            ["credit_amount"]
        ),
        (
            (F.col("net_amount") < 0) | F.col("net_amount").isNull(),
            "NEGATIVE_NET_AMOUNT",
            ["net_amount"]
        ),
        (
            F.col("account_name").isNull() | (F.trim(F.col("account_name")) == ""),
            "ACCOUNT_NAME_NULL_OR_BLANK",
            ["account_name"]
        ),
        (
            F.col("account_code").isNull() | (F.trim(F.col("account_code")) == ""),
            "ACCOUNT_CODE_NULL_OR_BLANK",
            ["account_code"]
        ),
        (
            F.col("ledger_id").isNull() | (F.trim(F.col("ledger_id")) == ""),
            "LEDGER_ID_NULL",
            ["ledger_id"]
        ),
        (
            F.round(F.col("credit_amount") - F.col("debit_amount"), 2) != F.round(F.col("net_amount"), 2),
            "BALANCE_IS_BROKEN",
            ["credit_amount", "debit_amount", "net_amount"]
        ),
        (
            F.round(F.col("usd_equivalent"), 2) !=
            F.round(F.col("net_amount") * F.col("usd_exchange_rate"), 2),
            "USD_EQUIVALENCE_IS_NOT_MATCHING",
            ["usd_equivalent", "net_amount", "usd_exchange_rate"]
        ),
        (
            (F.col("entry_type").eqNullSafe(common_constants.ENTRY_TYPE_REVERSAL_PAYMENT))
            & F.col("reversal_reference").isNull(),
            "REVERSAL_PAYMENT_WITH_NO_REFERENCE",
            ["entry_type", "reversal_reference"]
        )
    ]

    failure_reason_exprs = []
    failed_columns_exprs = []
    for condition, reason, column_names in validation_rules_list:
        failure_reason_exprs.append(
            F.when(condition, F.lit(reason))
        )

        failed_columns_exprs.append(
            F.when(
                condition,
                F.array(*[F.lit(col_name) for col_name in column_names])
            ).otherwise(F.array())
        )

    failure_reason_col = F.array_compact(F.array(*failure_reason_exprs))
    failed_columns_col = F.array_distinct(F.flatten(F.array(*failed_columns_exprs)))

    # Tag the whole data frame based on validation checks
    tagged_df = df \
        .withColumn(transformation_constants.COLUMN_NAME_FAILURE_REASON, failure_reason_col) \
        .withColumn(transformation_constants.COLUMN_NAME_FAILED_COLUMNS, failed_columns_col) \
        .withColumn(transformation_constants.COLUMN_NAME_VALIDATION_RESULT,
                    F.when(
                        F.size(failed_columns_col) > 0,
                        F.lit(transformation_constants.VALIDATION_RESULT_FAILED)
                    )
                    .otherwise(F.lit(transformation_constants.VALIDATION_RESULT_SUCCESSFUL))
                    )

    # Quarantine the records that failed necessary validation
    quarantined_df = tagged_df \
        .filter((F.col(transformation_constants.COLUMN_NAME_VALIDATION_RESULT)
                 .eqNullSafe(transformation_constants.VALIDATION_RESULT_FAILED))
                & (F.size(F.col(transformation_constants.COLUMN_NAME_FAILURE_REASON)) > 0)
                & (F.size(F.col(transformation_constants.COLUMN_NAME_FAILED_COLUMNS)) > 0))

    # Separate the valid records and use this data frame further
    valid_df = tagged_df \
        .filter(F.col(transformation_constants.COLUMN_NAME_VALIDATION_RESULT)
                .eqNullSafe(transformation_constants.VALIDATION_RESULT_SUCCESSFUL)) \
        .drop(transformation_constants.COLUMN_NAME_FAILURE_REASON,
              transformation_constants.COLUMN_NAME_FAILED_COLUMNS)

    return quarantined_df, valid_df


def deduplicate_sales_ledger_data(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """
    First de-duplicate sales ledger data based on pre-configured keys
    and extract the duplicate records with reason for validation failure to quarantine for further analyze
    :param df: Original sales ledger data frame
    :return: Tuple of unique data and duplicated data
    """
    # Create the window function over Deduplication keys for Sales Ledger
    window_function = Window \
        .partitionBy(transformation_constants.SALES_LEDGER_DE_DUPLICATE_KEYS) \
        .orderBy(F.col("created_at").desc())

    # Ranked data frame with row_number for deduplication using natural keys for ales ledger
    ranked_df = df.withColumn("row_number", F.row_number().over(window_function))

    # Separate cleansed and duplicate data frames
    unique_df = ranked_df \
        .filter(F.col("row_number") == 1) \
        .drop("row_number") \
        .withColumn(transformation_constants.COLUMN_NAME_VALIDATION_RESULT,
                    F.lit(transformation_constants.VALIDATION_RESULT_SUCCESSFUL))

    duplicates_df = ranked_df \
        .filter(F.col("row_number") > 1) \
        .drop("row_number") \
        .withColumn(transformation_constants.COLUMN_NAME_VALIDATION_RESULT,
                    F.lit(transformation_constants.VALIDATION_RESULT_FAILED)) \
        .withColumn(transformation_constants.COLUMN_NAME_FAILURE_REASON,
                    F.lit(transformation_constants.VALIDATION_FAILURE_REASON_DUPLICATE))

    return unique_df, duplicates_df


def type_cast_sales_ledger_data(df: DataFrame) -> DataFrame:
    """
    Converts and imposes strict type checking for few columns in the DataFrame containing Sales ledger data

    :param df: DataFrame containing Sales ledger data
    :return: The same DataFrame but imposed strict type checking and processable format conversion
    """

    return df \
        .withColumn("created_at", F.to_timestamp("created_at", "yyyy-MM-dd'T'HH:mm:ss'Z'")) \
        .withColumn("debit_amount", F.col("debit_amount").cast(DecimalType(18, 2))) \
        .withColumn("credit_amount", F.col("credit_amount").cast(DecimalType(18, 2))) \
        .withColumn("net_amount", F.col("net_amount").cast(DecimalType(18, 2))) \
        .withColumn("usd_exchange_rate.", F.col("usd_exchange_rate.").cast(DecimalType(10, 6))) \
        .withColumn("usd_equivalent", F.col("usd_equivalent").cast(DecimalType(18, 2))) \
        .withColumn("tax_amount", F.col("tax_amount").cast(DecimalType(18, 2))) \
        .withColumn("discount_amount", F.col("discount_amount").cast(DecimalType(18, 2))) \
        .withColumn("gross_amount", F.col("gross_amount").cast(DecimalType(18, 2))) \
        .withColumn("cost_of_goods_usd", F.col("cost_of_goods_usd").cast(DecimalType(18, 2))) \
        .withColumn("is_reconciled", F.col("is_reconciled").cast(BooleanType()))


def enrich_sales_ledger_data(cleansed_df: DataFrame) -> DataFrame:
    """
    Cleanse and transform sales ledger data and store the final result for further analysis
    :param cleansed_df: Cleansed sales ledger data frame
    :return: The enriched sales ledger data frame
    """

    # Conditions where financial analyst needs to manually analyze
    condition_missing_fx = F.col("usd_exchange_rate").isNull()
    condition_zero_fx = F.col("usd_exchange_rate").eqNullSafe(F.lit(0.0))
    condition_missing_cog = F.col("cost_of_goods_usd").isNull()
    condition_cog_gt_usd = F.col("cost_of_goods_usd") > F.col("usd_equivalent")
    condition_discount_gt_gross = F.col("discount_amount") > F.col("gross_amount")
    condition_txn_created_gap_gt_15 = (
            F.abs(
                F.datediff(
                    F.to_date(F.col("_parsed_txn_date")),
                    F.to_date(F.col("created_at"))
                )
            ) > 15
    )

    # Derive the quarter of sale
    cleansed_and_enriched_df = \
        (cleansed_df
        # Fiscal period: Apr=1, May=2, ..., Mar=12
        .withColumn("fiscal_period", (((F.month("_parsed_txn_date") + 8) % 12) + 1))

        # Fiscal quarter: Q1=Apr-Jun, Q2=Jul-Sep, Q3=Oct-Dec, Q4=Jan-Mar
        .withColumn("fiscal_quarter_num", F.floor((F.col("fiscal_period") - 1) / 3) + 1)
        .withColumn("fiscal_quarter", F.concat(F.lit("Q"), F.col("fiscal_quarter_num")))

        # fiscal year label as end year, Example: 2025-04-01 -> FY2026, 2026-02-15 -> FY2026
        .withColumn("fiscal_year",
                    F.when(F.month("_parsed_txn_date") > 3, F.year("_parsed_txn_date") + 1)
                    .otherwise(F.year("_parsed_txn_date")))

        # Infer gross amount if it's not preset or null
        .withColumn("gross_amount",
                    F.round(
                        F.coalesce(
                            F.col("gross_amount"),
                            F.col("net_amount") + F.col("tax_amount") + F.col("discount_amount")),
                        2)
                    )

        # USD equivalent calculation if not present
        .withColumn("usd_equivalent",
                    F.round(
                        F.coalesce(
                            F.col("usd_equivalent"),
                            F.col("net_amount") * F.col("usd_exchange_rate") - F.col("tax_amount") - F.col(
                                "discount_amount")
                        ),
                        2)
                    )

        # Different amount and % calculations
        .withColumn("tax_amount", F.coalesce(F.col("tax_amount"), F.lit(0.00)))
        .withColumn("discount_amount", F.coalesce(F.col("discount_amount"), F.lit(0.00)))
        .withColumn("gross_margin_amt_usd", F.round(F.col("usd_equivalent") - F.col("cost_of_goods_usd"), 2))
        .withColumn("gross_margin_percentage",
                    F.round(((F.col("gross_margin_amt_usd") / F.col("usd_equivalent")) * 100), 4))
        .withColumn("effective_tax_rate", F.round(((F.col("tax_amount") / F.col("gross_amount")) * 100), 4))
        .withColumn("discount_rate", F.round(((F.col("discount_amount") / F.col("gross_amount")) * 100), 4))

        # Behavioral / classification columns
        .withColumn("is_cross_border",
                    (~F.upper(F.col("currency")).eqNullSafe(transformation_constants.CURRENCY_USD))
                    & (F.col("usd_exchange_rate") != 1.0))
        .withColumn("is_high_value",
                    F.col("usd_equivalent") >= transformation_constants.HIGH_VALUE_TXN_AMOUNT_THRESHOLD)
        .withColumn("is_forex_risk_transaction", (F.col("is_cross_border")) | (F.col("is_high_value")))
        .withColumn("transaction_direction",
                    F.when((F.upper(F.col("entry_type")).isin(transformation_constants.OUTFLOW_TRANSACTION_TYPES))
                           & (F.col("net_amount") < 0.0),
                           transformation_constants.TRANSACTION_OUTFLOW)
                    .otherwise(transformation_constants.TRANSACTION_INFLOW))
        .withColumn("amount_mismatch",
                    F.when(F.col("gross_amount")
                           - (F.col("net_amount") + F.col("tax_amount") + F.col("discount_amount")) <= 0.01,
                           False)
                    .otherwise(True)
                    )
        .withColumns(
            {
                "manual_analysis_required": condition_missing_fx | condition_zero_fx | condition_missing_cog
                                            | condition_cog_gt_usd | condition_discount_gt_gross
                                            | condition_txn_created_gap_gt_15,
                "deeper_analysis_area": F.concat_ws(
                    " | ",
                    F.when(condition_missing_fx, F.lit("usd_exchange_rate is null")),
                    F.when(condition_zero_fx, F.lit("usd_exchange_rate = 0")),
                    F.when(condition_missing_cog, F.lit("cost_of_goods_usd is null")),
                    F.when(condition_cog_gt_usd, F.lit("cost_of_goods_usd > usd_equivalent")),
                    F.when(condition_discount_gt_gross, F.lit("discount_amount > gross_amount")),
                    F.when(condition_txn_created_gap_gt_15, F.lit("txn_date - created_at > 15 days")))
            })
        )

    # Trim all values of the string data types
    for schema_field in financial_data_system_schemas.SILVER_SALES_LEDGER_SCHEMA.fields:
        if schema_field.dataType.simpleString().lower() in ["string", "str"]:
            cleansed_and_enriched_df = cleansed_and_enriched_df \
                .withColumn(schema_field.name, F.trim(F.col(schema_field.name)))

    return cleansed_and_enriched_df
