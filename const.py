"""Constants for Cycle Tracker integration."""

DOMAIN = "cycle_tracker"
VERSION = "1.0.0"

# Config keys
CONF_USER_NAME         = "user_name"
CONF_CYCLE_START       = "cycle_start_date"
CONF_CYCLE_LENGTH      = "cycle_length"
CONF_PERIOD_LENGTH     = "period_length"
CONF_NOTIFY_DEVICE     = "notify_device"
CONF_DAILY_SUMMARY     = "daily_summary"
CONF_NOTIFY_PERIOD     = "notify_period_soon"
CONF_NOTIFY_OVULATION  = "notify_ovulation"

# Defaults
DEFAULT_CYCLE_LENGTH  = 28
DEFAULT_PERIOD_LENGTH = 5

# Phase identifiers
PHASE_MENSTRUATION = "menstruatie"
PHASE_FOLLICULAR   = "foliculara"
PHASE_OVULATION    = "ovulatie"
PHASE_LUTEAL       = "luteala"

PHASE_LABELS = {
    PHASE_MENSTRUATION: "Menstruație",
    PHASE_FOLLICULAR:   "Foliculară",
    PHASE_OVULATION:    "Ovulație",
    PHASE_LUTEAL:       "Luteală",
}

PHASE_ICONS = {
    PHASE_MENSTRUATION: "mdi:water",
    PHASE_FOLLICULAR:   "mdi:flower-outline",
    PHASE_OVULATION:    "mdi:egg-outline",
    PHASE_LUTEAL:       "mdi:moon-waning-crescent",
}

# Fertility levels
FERTILITY_MAXIMUM    = "maxim"
FERTILITY_VERY_HIGH  = "foarte_inalt"
FERTILITY_HIGH       = "inalt"
FERTILITY_MODERATE   = "moderat"
FERTILITY_LOW        = "scazut"

FERTILITY_LABELS = {
    FERTILITY_MAXIMUM:   "Maxim",
    FERTILITY_VERY_HIGH: "Foarte înalt",
    FERTILITY_HIGH:      "Înalt",
    FERTILITY_MODERATE:  "Moderat",
    FERTILITY_LOW:       "Scăzut",
}

# Sensor entity names
SENSOR_CYCLE_DAY         = "cycle_day"
SENSOR_CYCLE_PHASE       = "cycle_phase"
SENSOR_FERTILITY_LEVEL   = "fertility_level"
SENSOR_DAYS_UNTIL_PERIOD = "days_until_period"
SENSOR_NEXT_PERIOD_DATE  = "next_period_date"
SENSOR_OVULATION_DATE    = "ovulation_date"
SENSOR_CYCLE_PROGRESS    = "cycle_progress"
