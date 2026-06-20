# Processable ISO currencies
ALLOWED_CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY", "CHF", "YUN"]

# Python supported common date and time formats
SPARK_SUPPORTED_DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%m/%d/%Y"
]
SPARK_SUPPORTED_TIME_FORMATS = [
    "%H:%M",  # → 14:30 (24-hour format without seconds)
    "%H:%M:%S",  # → 14:30:59
    "%I:%M %p",  # → 02:30 PM
    "%Y-%m-%d %H:%M:%S",  # → 2026-06-16 14:30:59
    "%Y-%m-%dT%H:%M:%S",  # → ISO-like timestamp
    "%Y-%m-%dT%H:%M:%S.%f",  # → with microseconds
    "%Y-%m-%d %H:%M:%S%z"  # → with UTC offset
]

# Spark supported date and time formats
SPARK_SUPPORTED_DATE_FORMATS = [
    "yyyy-MM-dd",
    "dd-MM-yyyy",
    "MM-dd-yyyy",
    "yyyy/MM/dd",
    "dd/MM/yyyy",
    "MM/dd/yyyy"
]
SPARK_SUPPORTED_TIME_FORMATS = [
    "HH:mm",                 # 14:30
    "HH:mm:ss",              # 14:30:59
    "hh:mm a",               # 02:30 PM
    "yyyy-MM-dd HH:mm:ss",   # 2026-06-16 14:30:59
    "yyyy-MM-dd'T'HH:mm:ss", # ISO-like timestamp
    "yyyy-MM-dd'T'HH:mm:ss.SSSSSS",  # with microseconds
    "yyyy-MM-dd HH:mm:ssXXX" # with UTC offset
]

SPARK_TIMESTAMP_FORMATS = [
    "yyyy-MM-dd HH:mm:ss",
    "yyyy-MM-dd HH:mm",
    "yyyy-MM-dd'T'HH:mm:ss",
    "yyyy-MM-dd'T'HH:mm:ss.SSSSSS",
    "yyyy-MM-dd",
    "dd-MM-yyyy HH:mm:ss",
    "dd-MM-yyyy",
    "MM/dd/yyyy HH:mm:ss",
    "MM/dd/yyyy"
]