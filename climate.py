"""windhager myComfort climate device."""
import logging

import requests

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_COMFORT,
    PRESET_ECO,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, TEMP_CELSIUS

from . import (
    DOMAIN as MYCOMFORT_DOMAIN,
    MYCOMFORT_ERROR,
    MYCOMFORT_API,
    MYCOMFORT_NAME,
)

logger = logging.getLogger(__name__)


MYCOMFORT_MODE_STANDBY = "Stand-by"
MYCOMFORT_MODE_HEATING_1 = "Heating program 1"
MYCOMFORT_MODE_HEATING_2 = "Heating program 2"
MYCOMFORT_MODE_HEATING_3 = "Heating program 3"
MYCOMFORT_MODE_HEATING = "Heating mode"
MYCOMFORT_MODE_SETBACK = "Setback mode"
MYCOMFORT_MODE_DHW = "DHW operation"


MYCOMFORT_PROGRAM_ACTIVE = "active"
MYCOMFORT_PROGRAM_COMFORT = "comfort"
MYCOMFORT_PROGRAM_ECO = "eco"
MYCOMFORT_PROGRAM_EXTERNAL = "external"
MYCOMFORT_PROGRAM_HOLIDAY = "holiday"
MYCOMFORT_PROGRAM_NORMAL = "normal"
MYCOMFORT_PROGRAM_REDUCED = "reduced"
MYCOMFORT_PROGRAM_STANDBY = "standby"

MYCOMFORT_PROGRAM_STANDBY = "Stand-by"
MYCOMFORT_PROGRAM_HEATING = "Heating mode"
MYCOMFORT_PROGRAM_SETBACK = "Setback mode"
MYCOMFORT_PROGRAM_DHW = "DHW load"
MYCOMFORT_PROGRAM_ECO = "ECO / Party"
MYCOMFORT_PROGRAM_HOLIDAY = "Holiday program"
MYCOMFORT_PROGRAM_SCREED = "Screed"
MYCOMFORT_PROGRAM_FROST = "Frost protection"
MYCOMFORT_PROGRAM_HEATING_LIMIT = "Stand-by heating limit"
MYCOMFORT_PROGRAM_MANUAL = "Manual mode"
MYCOMFORT_PROGRAM_TEST = "Test"
MYCOMFORT_PROGRAM_SWEEP = "Chimney sweep mode"
MYCOMFORT_PROGRAM_BURNER_OFF = "Burner OFF"
MYCOMFORT_PROGRAM_BURNER_ON = "Burner ON"
MYCOMFORT_PROGRAM_AUTO = "Automatic boiler"
MYCOMFORT_PROGRAM_SOLID = "Solid fuel boiler"
MYCOMFORT_PROGRAM_BUFFER = "Buffer"


MYCOMFORT_HOLD_MODE_AWAY = "away"
MYCOMFORT_HOLD_MODE_HOME = "home"
MYCOMFORT_HOLD_MODE_OFF = "off"

MYCOMFORT_TEMP_HEATING_MIN = 6
MYCOMFORT_TEMP_HEATING_MAX = 30

SUPPORT_FLAGS_HEATING = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

MYCOMFORT_TO_HA_HVAC_HEATING = {
    MYCOMFORT_MODE_STANDBY: HVAC_MODE_OFF,
    MYCOMFORT_MODE_HEATING_1: HVAC_MODE_AUTO,
    MYCOMFORT_MODE_HEATING_2: HVAC_MODE_AUTO,
    MYCOMFORT_MODE_HEATING_3: HVAC_MODE_AUTO,
    MYCOMFORT_MODE_HEATING: HVAC_MODE_HEAT,
    MYCOMFORT_MODE_SETBACK: HVAC_MODE_OFF,
    MYCOMFORT_MODE_DHW: HVAC_MODE_OFF,
}

HA_TO_MYCOMFORT_HVAC_HEATING = {
    HVAC_MODE_HEAT: MYCOMFORT_MODE_HEATING,
    HVAC_MODE_OFF: MYCOMFORT_MODE_STANDBY,
    HVAC_MODE_AUTO: MYCOMFORT_MODE_HEATING_1,
}

MYCOMFORT_TO_HA_PRESET_HEATING = {
    MYCOMFORT_PROGRAM_COMFORT: PRESET_COMFORT,
    MYCOMFORT_PROGRAM_ECO: PRESET_ECO,
}

HA_TO_MYCOMFORT_PRESET_HEATING = {
    PRESET_COMFORT: MYCOMFORT_PROGRAM_COMFORT,
    PRESET_ECO: MYCOMFORT_PROGRAM_ECO,
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Create the myComfort climate devices."""
    if discovery_info is None:
        return
    mycomfort_api = hass.data[MYCOMFORT_DOMAIN][MYCOMFORT_API]

    for module in mycomfort_api.modules():
        add_entities(
            [
                myComfortClimate(
                    f"{hass.data[MYCOMFORT_DOMAIN][MYCOMFORT_NAME]} " + module.name,
                    module,
                )
            ]
        )


class myComfortClimate(ClimateEntity):
    """Representation of the myComfort heating climate device."""

    def __init__(self, name, api):
        """Initialize the climate device."""
        self._name = name
        self._state = None
        self._api = api
        self._attributes = {}
        self._target_temperature = None
        self._current_mode = None
        self._current_temperature = None
        self._current_program = None
        self._current_action = None

    def update(self):
        try:
            self._current_temperature = float(self._api.getFlowTemperature())

            self._current_program = self._api.getActiveProgram()

            self._target_temperature = float(self._api.getRoomTemperatureSetpoint())

            self._current_mode = self._api.getOperationMode()
            logger.debug(self._name + " current mode : " + self._current_mode)
            # Update the generic device attributes
            self._attributes = {}
#            self._attributes["room_temperature"] = _room_temperature
            self._attributes["active_mycomfort_program"] = self._current_program
            self._attributes["active_mycomfort_mode"] = self._current_mode
#            self._attributes["month_since_last_service"] = self._api.getMonthSinceLastService()
#            self._attributes["date_last_service"] = self._api.getLastServiceDate()
#            self._attributes["error_history"] = self._api.getErrorHistory()
#            self._attributes["active_error"] = self._api.getActiveError()

            # Update the specific device attributes
            self._current_action = self._api.getBurnerActive()

        except requests.exceptions.ConnectionError:
            logger.error("Unable to retrieve data from myComfort server")
        except ValueError:
            logger.error("Unable to decode data from myComfort server")

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS_HEATING

    @property
    def name(self):
        """Return the name of the climate device."""
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

    @property
    def hvac_mode(self):
        """Return current hvac mode."""
        return MYCOMFORT_TO_HA_HVAC_HEATING.get(self._current_mode)

    def set_hvac_mode(self, hvac_mode):
        """Set a new hvac mode on the ViCare API."""
        mycomfort_mode = HA_TO_MYCOMFORT_HVAC_HEATING.get(hvac_mode)
        if mycomfort_mode is None:
            logger.error(
                "Cannot set invalid mycomfort mode: %s / %s", hvac_mode, mycomfort_mode
            )
            return

        logger.debug("Setting hvac mode to %s / %s", hvac_mode, mycomfort_mode)
        self._api.setMode(mycomfort_mode)

    @property
    def hvac_modes(self):
        """Return the list of available hvac modes."""
        return list(HA_TO_MYCOMFORT_HVAC_HEATING)

    @property
    def hvac_action(self):
        """Return the current hvac action."""
        if self._current_action:
            return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return MYCOMFORT_TEMP_HEATING_MIN

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return MYCOMFORT_TEMP_HEATING_MAX

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            self._api.setRoomTemperatureSetpoint(temp)
            self._api.setDuration(60)
#            self._api.setProgramTemperature(self._current_program, temp)
            self._target_temperature = temp

    @property
    def preset_mode(self):
        """Return the current preset mode, e.g., home, away, temp."""
        return MYCOMFORT_TO_HA_PRESET_HEATING.get(self._current_program)

    @property
    def preset_modes(self):
        """Return the available preset mode."""
        return list(MYCOMFORT_TO_HA_PRESET_HEATING)

    def set_preset_mode(self, preset_mode):
        """Set new preset mode and deactivate any existing programs."""
        mycomfort_program = HA_TO_MYCOMFORT_PRESET_HEATING.get(preset_mode)
        if mycomfort_program is None:
            loger.error(
                "Cannot set invalid mycomfort program: %s / %s",
                preset_mode,
                mycomfort_program,
            )
            return

#        logger.debug("Setting preset to %s / %s", preset_mode, mycomfort_program)
#        self._api.deactivateProgram(self._current_program)
#        self._api.activateProgram(mycomfort_program)

    @property
    def extra_state_attributes(self):
        """Show Device Attributes."""
        return self._attributes
