from pathlib import Path
import tzlocal
import logging
import colorlog
import logging.config
import datetime as dt
import json
from typing import Literal


def setup_logging(
    log_dir: Path,
    log_file: str,
    log_level: Literal[
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL
    ],
    flg_time_partitioned: bool = False,
    flg_replace_log_file: bool = False):

    # TODO: modify to be able to handle extra arguments to give meta information to jsonl entries (make groups of processes)
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            local_tz = tzlocal.get_localzone()
            log_record = {
                "timestamp": dt.datetime.fromtimestamp(record.created, tz=local_tz).strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
                "level": record.levelname,
                "filename": record.filename,
                "lineno": record.lineno,
                "message": record.getMessage()
            }
            return json.dumps(log_record)

    if flg_replace_log_file:
        handler_mode = 'w'
    else:
        handler_mode = 'a'

    # Ensure log directory exists
    if flg_time_partitioned:
        log_dir = log_dir / dt.datetime.now().strftime("%Y/%m/")
        log_file = f"{dt.datetime.now().strftime('%Y-%m-%d')}"
    else:
        log_dir = log_dir
        log_file = log_file.rstrip('.log') # .log is added in the handler

    log_dir.mkdir(parents=True, exist_ok=True)

    # Define the logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(levelname)8s]: %(message)s'
            },
            'verbose': {
                'format': '''%(asctime)s [%(levelname)8s]: %(message)s
                                 └─ %(funcName)s()
                                 └─ at %(filename)s:%(lineno)d'''
            },
           'console': {
                '()': colorlog.ColoredFormatter,
                'format': '%(log_color)s%(asctime)s [%(levelname)8s]: %(message)s%(reset)s',
                'log_colors': {
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            },
            'json': {
                    '()': JsonFormatter,
                    'datefmt': '%Y-%m-%d %H:%M:%S,%f'
                },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
            'console': {
                'level': log_level,
                'formatter': 'console',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'level': log_level,
                'formatter': 'default',
                'class': 'logging.FileHandler',
                'filename': log_dir / log_file,
                'mode': handler_mode,
            },
            'file_verbose': {
                'level': log_level,
                'formatter': 'verbose',
                'class': 'logging.FileHandler',
                'filename': log_dir / f"{log_file}_verbose.log",
                'mode': handler_mode,
            },
            'json': {
                'level': log_level,
                'formatter': 'json',
                'class': 'logging.FileHandler',
                'filename': log_dir / f'{log_file}.jsonl',
                'mode': handler_mode,
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default'],
                'level': 'WARNING',
                'propagate': True
            },
            'default': {
                'handlers': ['file', 'console'],
                'level': log_level,
                'propagate': False
            },
            'verbose': {
                'handlers': ['file', 'console', 'file_verbose', 'json'],
                'level': log_level,
                'propagate': False
            },
        }
    }

    # Apply the configuration
    logging.config.dictConfig(logging_config)

