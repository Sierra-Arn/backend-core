# app/modules/health/base_schemas.py
from enum import StrEnum
 
 
class ServiceStatus(StrEnum):
    """
    Enumeration of possible availability states for the application
    and its dependencies.
 
    Attributes
    ----------
    OK : str
        The service is reachable and operating normally.
    DEGRADED : str
        The application is running but one or more dependencies are
        unavailable. Requests that rely on the affected dependency will fail.
    UNAVAILABLE : str
        The service could not be reached or did not respond successfully.
    """
 
    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"