"""Constants for the Lease Contract integration."""

DOMAIN = "lease_contract"

PLATFORMS = ["sensor"]

# --- Config entry keys (set during the UI config flow) ---
CONF_ODOMETER_ENTITY = "odometer_entity"
CONF_MAX_KM = "max_km"
CONF_START_DATE = "start_date"
CONF_END_DATE = "end_date"
CONF_START_ODOMETER = "start_odometer"  # optional, manual baseline override

# --- Persistent per-entry storage keys ---
STORE_KEY_START_ODOMETER = "start_odometer"
STORE_KEY_MONTH_KEY = "month_key"
STORE_KEY_MONTH_START_ODOMETER = "month_start_odometer"

STORAGE_VERSION = 1
