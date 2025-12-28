class LocationNotFoundError(Exception):
    """Raised when a location cannot be found via geocoding."""

    pass


class ExternalServiceError(Exception):
    """Raised when an external API call fails."""

    pass


class DataParseError(Exception):
    """Raised when response data cannot be parsed as expected."""

    pass
