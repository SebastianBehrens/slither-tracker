from pathlib import Path
from slither import backend
from slither.util import util_logging, database
import logging
from dotenv import load_dotenv
import os

if __name__ == "__main__":

    print('setting up logging...')
    log_dir = Path.cwd() / 'logs'
    log_file = 'main.log'
    util_logging.setup_logging(log_dir, log_file, logging.INFO)
    logger = logging.getLogger('default')
    print('loading environment variables...')
    load_dotenv()

    database = database.SlitherDatabase(
        connection_string=os.environ['CONN_STRING_POSTGRES'],
        # connection_string=os.environ['CONN_STRING_SQLITE'],
        logger = logger
    )

    # database.insert_test_cases()

    backend(
        logger,
        database = database
    )