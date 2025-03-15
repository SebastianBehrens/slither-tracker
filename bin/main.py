import requests
import datetime as dt
import time
from bs4 import BeautifulSoup as soup
from pandas import DataFrame as dataframe
import sqlite3  # Import sqlite3 module
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from database import SlitherDatabase
import util_logging

def fetch_webpage(url, logger:logging.Logger, flg_dump_content = False):
    logger.info("Fetching webpage...")
    response = requests.get(url)
    if flg_dump_content:
        logger.info("└─ Dumping content...")
        with open('ntl_page_dump.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
    if response.status_code != 200:
        logger.warning(f"Bad response: {response.status_code}")
    logger.info("└─done.")
    return soup(response.text, 'html.parser')

def extract_tables(soup, logger:logging.Logger):
    logger.info("Extracting tables...")
    tables = soup.find_all('table')
    extracted_tables = []
    for table in tables:
        extracted_tables.append(table.prettify())
    return extracted_tables

def process_table(table, logger:logging.Logger):
    logger.debug(f"│    └─ extracting table...")
    parsed = soup(table, 'html.parser')
    
    first_tr = parsed.find('tr')
    server_id = None  # Initialize server_id to None
    server_ip = None  # Initialize server_ip to None

    if first_tr:
        th = first_tr.find('th')
        if th:
            server_id = th.find('span').text.strip()
            logger.debug(f"│    └─ Processing server {server_id}...")
            server_ip = th.find('span', style='user-select: all').text.strip()

    third_tr = parsed.find_all('tr')[2]
    if third_tr:
        server_time = third_tr.text.strip().split('Server time: ')[-1]
    
    all_tds = parsed.find_all('td')
    filtered_tds = [td for td in all_tds if td.get('class') in [['tdrank'], ['tdnick'], ['tdscore']]]
    
    rank_idx = 1
    records = []
    for i in range(0, len(filtered_tds), 3):
        triplet = filtered_tds[i:i+3]
        if len(triplet) == 3:  # Ensure we have a complete triplet
            rank = rank_idx
            nick = triplet[1]
            score = triplet[2]
            aux_record = {
                "rank": rank_idx,
                "nick": nick.text.strip(),
                "score": score.text.strip()
            }
            rank_idx += 1
            records.append(aux_record)
    
    # Check if server_id is defined before returning
    if server_id:  # Check if server_id is not None
        out = {
            'server_id': server_id,
            'server_ip': server_ip,
            'server_time': server_time,
            'records': records
        }
        return out
    return None



def test_database(logger: logging.Logger):

    first_user_data = {
        'server_id': 'test_server_1',
        'server_ip': '127.0.0.1',
        'server_time': dt.datetime.now(dt.timezone.utc).isoformat(),
        'flg_active': True,
        'records': [
            {"rank": 1, "nick": "UserA", "score": 100}
        ]
    }
    database.server_user_rank_insert(first_user_data)

    time.sleep(2)
    
    second_user_data = {
        'server_id': 'test_server_1',
        'server_ip': '127.0.0.1',
        'server_time': dt.datetime.now(dt.timezone.utc).isoformat(),
        'records': [
            {"rank": 1, "nick": "UserB", "score": 150}
        ]
    }



def main(
    logger: logging.Logger,
    database: SlitherDatabase
    ):

    while True:
        logger.info("Starting load...")
        time_now = dt.datetime.now(dt.timezone.utc)
        logger.info(f"└─ {time_now.isoformat()}")

        database.validate_storage(
            flg_drop_table = False
        )

        url = "https://ntl-slither.com/ss/?lowts=0"

        content = fetch_webpage(url, logger, flg_dump_content = False)
        tables = extract_tables(content, logger)
        logger.info(f"│    └─ {len(tables)} tables found.")

        for idx, table in enumerate(tables):
            data = process_table(table, logger)
            if data:
                database.server_user_rank_insert(data)
        logger.info("└─ sleeping for 2 minutes...")
        size_rows = database.fetch_table_size_in_rows()
        size_mb = database.fetch_table_size_in_mb()

        if size_mb > 5000:
            logger.critical("└─ table size > 5000 MB, exiting...")
            exit()

        time.sleep(3)

if __name__ == "__main__":

    print('setting up logging...')
    log_dir = Path.cwd() / 'logs'
    log_file = 'main.log'
    util_logging.setup_logging(log_dir, log_file, logging.INFO)
    logger = logging.getLogger('default')
    print('loading environment variables...')
    load_dotenv()

    # # # main(logger)
    main(
        logger,
        database = SlitherDatabase(
            # connection_string=os.environ['CONN_STRING_POSTGRES'],
            connection_string=os.environ['CONN_STRING_SQLITE'],
            logger = logger
        )
    )
    # # # test_database(logger)


# build dashboard with 
# 10 longest living players
# 10 highest scores
# 10 shortest top 1 times per loss size (out of top 10


# data check
# 8270 0.6875
# 8800 0.73046875 MB
# 9320 0.7734375 MB

# delta 1: 530 rows - 0.04296875 MB
# delta 2: 520 rows - 0.04296875 MB
# 520 - 0.043mb
# => 2gb used by 46511 cycles
# => 17280 cycles per day
# => fire
