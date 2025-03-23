import logging
from slither.frontend import Frontend
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    logger = logging.getLogger('test')
    app = Frontend(
        connection_string=os.environ['CONN_STRING_POSTGRES'],
        logger=logger
    )
    app.run()
