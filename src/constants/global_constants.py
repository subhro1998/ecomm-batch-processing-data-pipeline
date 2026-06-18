# Processable ISO currencies
ALLOWED_CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY", "CHF", "YUN"]

# Common date formats
SUPPORTED_DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
]
SUPPORTED_TIME_FORMATS = [
    "%H:%M",  # → 14:30 (24-hour format without seconds)
    "%H:%M:%S",  # → 14:30:59
    "%I:%M %p",  # → 02:30 PM
    "%Y-%m-%d %H:%M:%S",  # → 2026-06-16 14:30:59
    "%Y-%m-%dT%H:%M:%S",  # → ISO-like timestamp
    "%Y-%m-%dT%H:%M:%S.%f",  # → with microseconds
    "%Y-%m-%d %H:%M:%S%z",  # → with UTC offset
]