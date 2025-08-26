import os
from logging.config import dictConfig
import logging

BASE_DIR = os.getcwd()
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s - %(lineno)d - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'doc_extractor': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': os.path.join(LOG_DIR, 'doc_extractor.log')
        }
    },
    'loggers': {
        'doc_extractor': {
            'handlers': ['doc_extractor', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}
dictConfig(LOGGING)
logger = logging.getLogger('doc_extractor')
