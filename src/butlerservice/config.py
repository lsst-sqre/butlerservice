"""Configuration definition."""

__all__ = ["Configuration"]

import os
from dataclasses import dataclass


@dataclass
class Configuration:
    """Configuration for butlerservice."""

    # List a default value for this required parameter to make mypi happy.
    # It probably better than using Optional[str] for a required parameter.
    butler_uri: str = os.getenv("BUTLER_URI", "")
    """URI for a butler registry. Required.

    Set with the ```BUTLER_URI``` environment variable.
    """

    name: str = os.getenv("SAFIR_NAME", "butlerservice")
    """The application's name, which doubles as the root HTTP endpoint path.

    Set with the ``SAFIR_NAME`` environment variable.
    """

    profile: str = os.getenv("SAFIR_PROFILE", "development")
    """Application run profile: "development" or "production".

    Set with the ``SAFIR_PROFILE`` environment variable.
    """

    logger_name: str = os.getenv("SAFIR_LOGGER", "butlerservice")
    """The root name of the application's logger.

    Set with the ``SAFIR_LOGGER`` environment variable.
    """

    log_level: str = os.getenv("SAFIR_LOG_LEVEL", "INFO")
    """The log level of the application's logger.

    Set with the ``SAFIR_LOG_LEVEL`` environment variable.
    """
