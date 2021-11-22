"""The Windhager myComfort integration."""
from datetime import timedelta
import enum
import logging

from .mycomfortclient.myComfortGateway import Gateway

import voluptuous as vol

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
#from homeassistant.helpers.storage import STORAGE_DIR

MYCOMFORT_PLATFORMS = ["sensor", "climate", "water_heater"]

DOMAIN = "mycomfort"
MYCOMFORT_ERROR = "error"
MYCOMFORT_API = "api"
MYCOMFORT_NAME = "name"

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)


DEFAULT_SCAN_INTERVAL = 60
SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_PORT): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    cv.time_period, lambda value: value.total_seconds()
                ),
                vol.Optional(CONF_NAME, default="myComfort"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Create the mycomfort component."""
    conf = config[DOMAIN]
    params = {}

    if conf.get(CONF_SCAN_INTERVAL):
        params["cacheDuration"] = conf.get(CONF_SCAN_INTERVAL) - 1

    params["logginglevel"] = logger.level

    try:
        mycomfort_api = Gateway(conf[CONF_HOST], conf[CONF_PORT], conf[CONF_USERNAME], conf[CONF_PASSWORD], **params)
    except AttributeError:
        logger.error(
            "Failed to create myComfort API client. Please check your credentials"
        )
        return False

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][MYCOMFORT_API] = mycomfort_api
    hass.data[DOMAIN][MYCOMFORT_NAME] = conf[CONF_NAME]

    for platform in MYCOMFORT_PLATFORMS:
        discovery.load_platform(hass, platform, DOMAIN, {}, config)

    return True
