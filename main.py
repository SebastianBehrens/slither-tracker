import requests
import datetime as dt
import time
from bs4 import BeautifulSoup as soup
from pandas import DataFrame as dataframe
import sqlite3  # Import sqlite3 module
import logging
import os
from pathlib import Path

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

def validate_storage(logger:logging.Logger, flg_drop_db = False):
    logger.info("Validating storage...")

    if flg_drop_db:
        logger.warning("└─ Dropping database...")
        os.remove('slither.db')
        logger.warning("│    └─done.")

    logger.info("└─ Connecting to database...")
    conn = sqlite3.connect('slither.db')
    cursor = conn.cursor()
    
    # Check if the table exists before creating it
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='server_user_rank';")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        logger.info("└─ creating table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_user_rank (
                server_id TEXT,
                server_time TIMESTAMP WITH TIME ZONE NOT NULL,
                rank INTEGER,
                nick TEXT,
                score INTEGER,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (server_id, server_time, rank, nick)
            )
        ''')
        logger.info("│    └─done.")
    else:
        logger.info("└─ Table already exists.")
    conn.commit()
    conn.close()

def store_data(logger:logging.Logger, data, current_time: dt.datetime):
    logger.debug("│    └─ storing data...")
    conn = sqlite3.connect('slither.db')
    cursor = conn.cursor()
    
    df = dataframe(data['records'])
    df['server_id'] = data['server_id']
    df['server_time'] = data['server_time']
    df['created_at'] = current_time.isoformat()
    df = df[['server_id', 'server_time', 'rank', 'nick', 'score', 'created_at']]
    
    for index, row in df.iterrows():
        try:
            row_data = (row['server_id'], row['server_time'], row['rank'], row['nick'], row['score'], row['created_at'])
            conn.execute('''
                INSERT OR IGNORE INTO server_user_rank
                (server_id, server_time, rank, nick, score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                row_data)
        except Exception as e:
            logger.error(f"Error inserting row {index}: {e}")
    conn.commit()
    conn.close()

def fetch_table_size_in_rows(logger:logging.Logger):
    conn = sqlite3.connect('slither.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM server_user_rank')
    row_count = cursor.fetchone()[0]
    logger.info(f"└─ Number of rows in server_user_rank: {row_count}")
    conn.close()

def fetch_table_size_in_mb(logger:logging.Logger):
    conn = sqlite3.connect('slither.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            SUM(pgsize)/(1024.0*1024.0)
        FROM
            dbstat
        WHERE
            name = "server_user_rank";
    ''')
    table_info = cursor.fetchall()
    total_size = table_info[0][0]
    logger.info(f"└─ Table size in MB: {total_size}")
    conn.close()
    return total_size

if __name__ == "__main__":
    log_dir = Path.cwd() / 'logs'
    log_file = 'main.log'
    util_logging.setup_logging(log_dir, log_file, logging.INFO)
    logger = logging.getLogger('default')
    while True:
        logger.info("Starting load...")
        time_now = dt.datetime.now(dt.timezone.utc)
        logger.info(f"└─ {time_now.isoformat()}")
        validate_storage(flg_drop_db = False, logger = logger)
        url = "https://ntl-slither.com/ss/?lowts=0"
        content = fetch_webpage(url, logger, flg_dump_content = False)
        tables = extract_tables(content, logger)
        logger.info(f"│    └─ {len(tables)} tables found.")
        for table in tables:
            data = process_table(table, logger)
            if data:
                store_data(logger, data, time_now)
        logger.info("└─ sleeping for 2 minutes...")
        fetch_table_size_in_rows(logger)
        size = fetch_table_size_in_mb(logger)

        if size > 30000:
            logger.critical("└─ table size > 5000 MB, exiting...")
            exit()

        time.sleep(3)


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
