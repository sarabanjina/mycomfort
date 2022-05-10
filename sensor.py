"""Windhager myComfort sensor device."""
import logging
from datetime import timedelta

import requests

from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_OF_MEASUREMENT,
    DEVICE_CLASS_TEMPERATURE,
    MASS_KILOGRAMS,
    PERCENTAGE,
    TEMP_CELSIUS,
    TIME_HOURS,
)
from homeassistant.helpers.entity import Entity

from . import (
    DOMAIN as MYCOMFORT_DOMAIN,
    MYCOMFORT_ERROR,
    MYCOMFORT_API,
    MYCOMFORT_NAME,
    SCAN_INTERVAL,
)

logger = logging.getLogger(MYCOMFORT_DOMAIN)

CONF_GETTER = "getter"

SENSOR_TYPE_TEMPERATURE = "temperature"

# boiler sensors
SENSOR_BOILER_TEMPERATURE = "boiler_temperature"
SENSOR_BOILER_SETPOINT_TEMPERATURE = "boiler_setpoint_temperature"
SENSOR_EXHAUST_TEMPERATURE = "exhaust_temperature"
SENSOR_BUFFER_TEMPERATURE = "buffer_temperature"
SENSOR_BURNER_MODULATION = "burner_modulation"
SENSOR_BURNER_STARTS = "burner_starts"
SENSOR_BURNER_HOURS = "burner_hours"
SENSOR_BOILER_CONSUMPTION_BULKFILL = "boiler_consumption_bulkfill"
SENSOR_BOILER_CONSUMPTION_TOTAL = "boiler_consumption_total"
SENSOR_BOILER_TIME_CLEANING = "boiler_time_cleaning"
SENSOR_BOILER_TIME_MAIN_CLEANING = "boiler_time_main_cleaning"
SENSOR_BOILER_TIME_MAINTENANCE = "boiler_time_maintenance"
SENSOR_BOILER_ALARM = "boiler_alarm"

# module sensors
SENSOR_OUTSIDE_TEMPERATURE = "outside_temperature"
SENSOR_FLOW_TEMPERATURE = "flow_temperature"
SENSOR_FLOW_SETPOINT_TEMPERATURE = "flow_setpoint_temperature"

# DHW sensors
SENSOR_DHW_TEMPERATURE = "dhw_temperature"
SENSOR_DHW_SETPOINT_TEMPERATURE = "dhw_setpoint_temperature"

SENSOR_TYPES = {
    SENSOR_EXHAUST_TEMPERATURE: {
        CONF_NAME: "Exhaust Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getExhaustTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    SENSOR_BUFFER_TEMPERATURE: {
        CONF_NAME: "Buffer Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getBufferTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    SENSOR_BOILER_TEMPERATURE: {
        CONF_NAME: "Boiler Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getBoilerTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    SENSOR_BOILER_SETPOINT_TEMPERATURE: {
        CONF_NAME: "Boiler Setpoint Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getBoilerSetpointTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    SENSOR_BURNER_MODULATION: {
        CONF_NAME: "Burner modulation",
        CONF_ICON: "mdi:percent",
        CONF_UNIT_OF_MEASUREMENT: PERCENTAGE,
        CONF_GETTER: lambda api: api.getBurnerModulation(),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_BOILER_CONSUMPTION_BULKFILL: {
        CONF_NAME: "Pellet consumption since bulk fill",
        CONF_ICON: "mdi:power",
        CONF_UNIT_OF_MEASUREMENT: MASS_KILOGRAMS,
        CONF_GETTER: lambda api: int(float(api.getBoilerConsumptionBulkfill()) * 1000),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_BOILER_CONSUMPTION_TOTAL: {
        CONF_NAME: "Pellet consumption total",
        CONF_ICON: "mdi:power",
        CONF_UNIT_OF_MEASUREMENT: MASS_KILOGRAMS,
        CONF_GETTER: lambda api: int(float(api.getBoilerConsumptionTotal()) * 1000),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_BOILER_TIME_CLEANING: {
        CONF_NAME: "Boiler Operating Time Cleaning",
        CONF_ICON: "mdi:counter",
        CONF_UNIT_OF_MEASUREMENT: TIME_HOURS,
        CONF_GETTER: lambda api: api.getOperatingTimeCleaning(),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_BOILER_TIME_MAIN_CLEANING: {
        CONF_NAME: "Boiler Operating Time Main Cleaning",
        CONF_ICON: "mdi:counter",
        CONF_UNIT_OF_MEASUREMENT: TIME_HOURS,
        CONF_GETTER: lambda api: api.getOperatingTimeMainCleaning(),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_BOILER_TIME_MAINTENANCE: {
        CONF_NAME: "Boiler Operating Time Maintenance",
        CONF_ICON: "mdi:counter",
        CONF_UNIT_OF_MEASUREMENT: TIME_HOURS,
        CONF_GETTER: lambda api: api.getOperatingTimeMaintenance(),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_BURNER_STARTS: {
        CONF_NAME: "Burner Starts",
        CONF_ICON: "mdi:counter",
        CONF_UNIT_OF_MEASUREMENT: None,
        CONF_GETTER: lambda api: api.getBurnerStarts(),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_BURNER_HOURS: {
        CONF_NAME: "Burner Hours",
        CONF_ICON: "mdi:counter",
        CONF_UNIT_OF_MEASUREMENT: TIME_HOURS,
        CONF_GETTER: lambda api: api.getBurnerHours(),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_BOILER_ALARM: {
        CONF_NAME: "Boiler Alarm",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: None,
        CONF_GETTER: lambda api: api.getAlarmText(),
        CONF_DEVICE_CLASS: None,
    },
    SENSOR_OUTSIDE_TEMPERATURE: {
        CONF_NAME: "Outside Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getOutsideTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    SENSOR_FLOW_TEMPERATURE: {
        CONF_NAME: "Flow Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getFlowTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    SENSOR_FLOW_SETPOINT_TEMPERATURE: {
        CONF_NAME: "Flow Setpoint Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getFlowSetpointTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    SENSOR_DHW_TEMPERATURE: {
        CONF_NAME: "DHW Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getDHWTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    SENSOR_DHW_SETPOINT_TEMPERATURE: {
        CONF_NAME: "DHW Setpoint Temperature",
        CONF_ICON: None,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        CONF_GETTER: lambda api: api.getDHWSetpointTemperature(),
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
}

SENSORS_BOILER = [SENSOR_BOILER_TEMPERATURE, SENSOR_BOILER_SETPOINT_TEMPERATURE, SENSOR_BURNER_MODULATION, SENSOR_BURNER_STARTS, SENSOR_BURNER_HOURS, SENSOR_EXHAUST_TEMPERATURE, SENSOR_BUFFER_TEMPERATURE, SENSOR_BOILER_CONSUMPTION_BULKFILL, SENSOR_BOILER_CONSUMPTION_TOTAL, SENSOR_BOILER_TIME_CLEANING, SENSOR_BOILER_TIME_MAIN_CLEANING, SENSOR_BOILER_TIME_MAINTENANCE, SENSOR_BOILER_ALARM]
SENSORS_MODULE = [SENSOR_OUTSIDE_TEMPERATURE, SENSOR_FLOW_TEMPERATURE, SENSOR_FLOW_SETPOINT_TEMPERATURE]
SENSORS_DHW = [SENSOR_DHW_TEMPERATURE, SENSOR_DHW_SETPOINT_TEMPERATURE]

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Create the mycomfort sensor devices."""
    if discovery_info is None:
        return

    mycomfort_api = hass.data[MYCOMFORT_DOMAIN][MYCOMFORT_API]

    sensors = SENSORS_BOILER.copy()

    for boiler in mycomfort_api.boilers():
        add_entities(
            [
                myComfortSensor(hass.data[MYCOMFORT_DOMAIN][MYCOMFORT_NAME] + " " + boiler.name, boiler, sensor)
                for sensor in sensors
            ]

        )

    sensors = SENSORS_MODULE.copy()

    for module in mycomfort_api.modules():
        add_entities(
            [
                myComfortSensor(hass.data[MYCOMFORT_DOMAIN][MYCOMFORT_NAME] + " " + module.name, module, sensor)
                for sensor in sensors
            ]
        )

        if module.isDHWCircuit():
            logger.debug("Module " + module.name + " is a DHW circuit!")
            sensors_dhw = SENSORS_DHW.copy()
            add_entities(
                [
                    myComfortSensor(hass.data[MYCOMFORT_DOMAIN][MYCOMFORT_NAME] + " " + module.name, module, sensor)
                    for sensor in sensors_dhw
                ]
            )



class myComfortSensor(Entity):
    """Representation of a myComfort sensor."""

    def __init__(self, name, api, sensor_type):
        """Initialize the sensor."""
        self._sensor = SENSOR_TYPES[sensor_type]
        self._name = f"{name} {self._sensor[CONF_NAME]}"
        self._api = api
        self._sensor_type = sensor_type
        self._state = None

    @property
    def available(self):
        """Return True if entity is available."""
        return self._state is not None and self._state != MYCOMFORT_ERROR

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._api.serial_no}-{self._sensor_type}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._sensor[CONF_ICON]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor[CONF_UNIT_OF_MEASUREMENT]

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._sensor[CONF_DEVICE_CLASS]

    def update(self):
        """Update state of sensor."""
        try:
            self._state = self._sensor[CONF_GETTER](self._api)
        except requests.exceptions.ConnectionError:
            logger.error("Unable to retrieve data from myComfort gateway")
        except ValueError:
            logger.error("Unable to decode data from myComfort gateway")
