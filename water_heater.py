"""Windhager myComfort water_heater device."""
import logging

import requests

from homeassistant.components.water_heater import (
    SUPPORT_TARGET_TEMPERATURE,
    WaterHeaterEntity,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, TEMP_CELSIUS

from . import (
    DOMAIN as MYCOMFORT_DOMAIN,
    MYCOMFORT_ERROR,
    MYCOMFORT_API,
    MYCOMFORT_NAME,
)

logger = logging.getLogger(__name__)

MYCOMFORT_MODE_DHW = "dhw"
MYCOMFORT_MODE_DHWANDHEATING = "dhwAndHeating"
MYCOMFORT_MODE_FORCEDREDUCED = "forcedReduced"
MYCOMFORT_MODE_FORCEDNORMAL = "forcedNormal"
MYCOMFORT_MODE_OFF = "standby"

MYCOMFORT_MODE_STANDBY = "Stand-by"
MYCOMFORT_MODE_HEATING_1 = "Heating program 1"
MYCOMFORT_MODE_HEATING_2 = "Heating program 2"
MYCOMFORT_MODE_HEATING_3 = "Heating program 3"
MYCOMFORT_MODE_HEATING = "Heating mode"
MYCOMFORT_MODE_SETBACK = "Setback mode"
MYCOMFORT_MODE_DHW = "DHW operation"

MYCOMFORT_TEMP_WATER_MIN = 10
MYCOMFORT_TEMP_WATER_MAX = 60

OPERATION_MODE_ON = "on"
OPERATION_MODE_OFF = "off"

SUPPORT_FLAGS_HEATER = SUPPORT_TARGET_TEMPERATURE

MYCOMFORT_TO_HA_HVAC_DHW = {
    MYCOMFORT_MODE_STANDBY: OPERATION_MODE_OFF,
    MYCOMFORT_MODE_HEATING_1: OPERATION_MODE_OFF,
    MYCOMFORT_MODE_HEATING_2: OPERATION_MODE_OFF,
    MYCOMFORT_MODE_HEATING_3: OPERATION_MODE_OFF,
    MYCOMFORT_MODE_HEATING: OPERATION_MODE_OFF,
    MYCOMFORT_MODE_SETBACK: OPERATION_MODE_OFF,
    MYCOMFORT_MODE_DHW: OPERATION_MODE_ON,
}
HA_TO_MYCOMFORT_HVAC_DHW = {
    OPERATION_MODE_OFF: MYCOMFORT_MODE_STANDBY,
    OPERATION_MODE_ON: MYCOMFORT_MODE_DHW,
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Create the Windhager myComfort water_heater devices."""
    if discovery_info is None:
        return
    mycomfort_api = hass.data[MYCOMFORT_DOMAIN][MYCOMFORT_API]

    for module in mycomfort_api.modules():
        if module.isDHWCircuit():
            add_entities(
                [
                    myComfortWater(
                        f"{hass.data[MYCOMFORT_DOMAIN][MYCOMFORT_NAME]} Water",
                        module,
                    )
                ]
            )


class myComfortWater(WaterHeaterEntity):
    """Representation of the Windhager myComfort domestic hot water device."""

    def __init__(self, name, api):
        """Initialize the DHW water_heater device."""
        self._name = name
        self._state = None
        self._api = api
        self._attributes = {}
        self._target_temperature = None
        self._current_temperature = None
        self._current_mode = None

    def update(self):
        try:
            current_temperature = float(self._api.getDHWTemperature())
            if current_temperature != MYCOMFORT_ERROR:
                self._current_temperature = current_temperature
            else:
                self._current_temperature = None

            self._target_temperature = (
                float(self._api.getDHWSetpointTemperature())
            )

            self._current_mode = self._api.getOperationMode()
        except requests.exceptions.ConnectionError:
            logger.error("Unable to retrieve data from myComfort gateway")
        except ValueError:
            logger.error("Unable to decode data from myComfort gateway")

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS_HEATER

    @property
    def name(self):
        """Return the name of the water_heater device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            #self._api.setDomesticHotWaterTemperature(temp)
            self._target_temperature = temp

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return MYCOMFORT_TEMP_WATER_MIN

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return MYCOMFORT_TEMP_WATER_MAX

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS

    @property
    def current_operation(self):
        """Return current operation ie. heat, cool, idle."""
        return MYCOMFORT_TO_HA_HVAC_DHW.get(self._current_mode)

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return list(HA_TO_MYCOMFORT_HVAC_DHW)
