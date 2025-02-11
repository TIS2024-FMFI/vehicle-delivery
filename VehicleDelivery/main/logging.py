import os
from VehicleDelivery.settings import BASE_DIR
from main.models import *

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "app.log"),
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters" : [],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "main": {  
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

    
def get_complaint_type(type):
    if type is ClaimModel:
        type_processed = "Claim"
    elif type is TransportModel:
        type_processed = "Transport"
    elif type is PreparationModel:
        type_processed = "Preparation"
    elif type is CommunicationModel:
        type_processed = "Communication"
    elif type is OtherModel:
        type_processed = "Other"
    elif type is Person:
        type_processed = "Person"
    elif type is Department:
        type_processed = "Department"
    else:
        type_processed = "_"

    return type_processed