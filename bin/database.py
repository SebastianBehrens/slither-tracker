from contextlib import contextmanager
import datetime as dt
from pandas import DataFrame as dataframe
import time
import psycopg
import sqlite3
import logging
class SlitherDatabase():
    def __init__(self, connection_string: str, logger: logging.Logger):
        self.conn_string = connection_string
        self.logger = logger
        if 'sqlite' in connection_string:
            self.conn_string = self.conn_string.replace('sqlite:///', '')
            self.database_type = 'sqlite'
            self.logger.info("Using SQLite database")
        elif 'postgres' in connection_string:
            self.database_type = 'postgres'
            self.logger.info("Using Postgres database")
        else:
            raise ValueError("Invalid connection string: must contain 'sqlite' or 'postgres'")

    def query(self, query: str, fetch = 'all', flg_commit = False):
        if self.database_type == 'postgres':
            with psycopg.connect(self.conn_string) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query)
                        if flg_commit:
                            conn.commit()
                        if fetch == 'all':
                            return cursor.fetchall()
                        elif fetch == 'one':
                            return cursor.fetchone()
                        elif fetch == 'none':
                            return None
                        else: 
                            raise ValueError(f"Invalid fetch value: {fetch}")
        elif self.database_type == 'sqlite':
            with sqlite3.connect(self.conn_string) as conn:
                cursor = conn.cursor()  # SQLite cursor doesn't support context manager
                try:
                    cursor.execute(query)
                    if flg_commit:
                        conn.commit()
                    if fetch == 'all':
                        return cursor.fetchall()
                    elif fetch == 'one':
                        return cursor.fetchone()
                    elif fetch == 'none':
                        return None
                    else: 
                        raise ValueError(f"Invalid fetch value: {fetch}")
                finally:
                    cursor.close()  # Explicitly close the cursor
        else:
            raise ValueError(f"Invalid database type: {self.database_type}")

    def get_conn(self):
        if self.database_type == 'sqlite':
            return sqlite3.connect(self.conn_string)
        elif self.database_type == 'postgres':
            return psycopg.connect(self.conn_string)

    def validate_storage(self, flg_drop_table = False):
        self.logger.info("Validating storage...")

        if flg_drop_table:
            self.logger.warning("└─ Dropping table...")
            self.query(
                "DROP TABLE IF EXISTS server_user_rank;",
                flg_commit = True,
                fetch = 'none'
            )
            self.logger.warning("│    └─done.")

        self.logger.info("└─ Connecting to database...")
        # Check if the table exists before creating it
        table_exists = self.server_user_rank_exists()



        if not table_exists:
            self.logger.info("└─ creating table...")
            self.server_user_rank_create()
            self.logger.info("│    └─done.")
        else:
            self.logger.info("└─ Table already exists.")

    def server_user_rank_exists(self):
        if self.database_type == 'sqlite':
            query = (
                "SELECT name FROM sqlite_master WHERE type='table' AND name='server_user_rank';"
            )
            flg_exists = self.query(query, fetch = 'one', flg_commit = False)
            return flg_exists[0]
        elif self.database_type == 'postgres':
            query = (
                """
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'server_user_rank'
                );
                """
            )
            flg_exists = self.query(query, fetch = 'one', flg_commit = False)
            return flg_exists[0]
        else:
            raise ValueError(f"Invalid database type: {self.database_type}")
    def server_user_rank_create(self):
        if self.database_type == 'sqlite':
            query = (
                '''
                CREATE TABLE IF NOT EXISTS server_user_rank (
                server_id TEXT,
                server_time TIMESTAMP WITH TIME ZONE NOT NULL,
                flg_active NOT NULL DEFAULT TRUE,
                rank INTEGER,
                    nick TEXT,
                    score INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (server_id, server_time, rank, nick)
                )
            ''')
            self.query(query, flg_commit = True, fetch = 'none')
        elif self.database_type == 'postgres':
            query = (
                '''
                CREATE TABLE IF NOT EXISTS server_user_rank (
                server_id TEXT,
                server_time TIMESTAMP WITH TIME ZONE NOT NULL,
                flg_active BOOLEAN NOT NULL DEFAULT TRUE,
                rank INTEGER,
                    nick TEXT,
                    score INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (server_id, server_time, rank, nick)
                )
            ''')
            self.query(query, flg_commit = True, fetch = 'none')

    def server_user_rank_insert(self, data: dict):

        self.logger.debug("│    └─ storing data...")
        df = dataframe(data['records'])
        df['server_id'] = data['server_id']
        df['server_time'] = data['server_time']
        df['created_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
        df = df[['server_id', 'server_time', 'rank', 'nick', 'score', 'created_at']]

        conn = self.get_conn()
        cursor = conn.cursor()
        
        insertion_query_sqlite = '''
            INSERT OR IGNORE INTO server_user_rank
            (
                server_id,
                server_time,
                flg_active,
                rank,
                nick,
                score,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        insertion_query_postgres = '''
            INSERT INTO public.server_user_rank
            (
                server_id,
                server_time,
                flg_active,
                rank,
                nick,
                score,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (server_id, server_time, rank, nick) DO NOTHING
        '''


        for index, row in df.iterrows():
            print(index)
            try:
                row_data = (row['server_id'], row['server_time'], True, row['rank'], row['nick'], row['score'], row['created_at'])
                if self.database_type == 'sqlite':
                    cursor.execute(insertion_query_sqlite, row_data)
                else:
                    cursor.execute(insertion_query_postgres, row_data)
            except Exception as e:
                self.logger.error(f"Error inserting row {index}: {e}")
        self.logger.info(f"│    └─ inserted data for server {row['server_id']} at {row['server_time']}")
        print(df)

        conn.commit()
        conn.close()
        # elif database_type == 'postgres':
        #     conn = psycopg.connect(os.environ['POSTGRESS_CONN'])
        #     cursor = conn.cursor()
        #     df = dataframe(data['records'])
        #     df['server_id'] = data['server_id']
        #     df['server_time'] = data['server_time']
        #     df['created_at'] = current_time.isoformat()
        #     df = df[['server_id', 'server_time', 'rank', 'nick', 'score', 'created_at']]
            
        #     for index, row in df.head(3).iterrows():
        #         try:
        #             row_data = (
        #                 row['server_id'],
        #                 row['server_time'],
        #                 True,
        #                 row['rank'],
        #                 row['nick'],
        #                 row['score'],
        #                 row['created_at'])
        #             cursor.execute('''
        #                 INSERT INTO public.server_user_rank
        #                 (server_id, server_time, flg_active, rank, nick, score, created_at)
        #                 VALUES (%s, %s, %s, %s, %s, %s, %s)
        #                 ''',
        #                 row_data)
        #         except Exception as e:
        #             logger.error(f"Error inserting row {index}: {e}")

        #     conn.commit()
        #     conn.close()
        
    def fetch_table_size_in_rows(self):
        if self.database_type == 'sqlite':
            row_count = self.query(
                'SELECT COUNT(*) FROM server_user_rank',
                fetch = 'one',
                flg_commit = False
                )
            self.logger.info(f"└─ Number of rows in server_user_rank: {row_count}")
        elif self.database_type == 'postgres':
            row_count = self.query(
                'SELECT COUNT(*) FROM server_user_rank',
                fetch = 'one',
                flg_commit = False
                )
            self.logger.info(f"└─ Number of rows in server_user_rank: {row_count}")
        return row_count

    def fetch_table_size_in_mb(self):
        if self.database_type == 'sqlite':
            result = self.query(
                '''
                SELECT
                    SUM(pgsize)/(1024.0*1024.0)
                FROM
                dbstat
            WHERE
                name = "server_user_rank";
                ''',
                fetch = 'one',
                flg_commit = False
            )
            size_in_mb = result[0] if result else 0
            self.logger.info(f"└─ Table size in MB: {size_in_mb}")
        elif self.database_type == 'postgres':
            result = self.query(
                '''
                SELECT
                    pg_total_relation_size('server_user_rank')/(1024.0*1024.0) as size_mb
                ''',
                fetch = 'one',
                flg_commit = False
            )
            size_in_mb = result[0] if result else 0
            self.logger.info(f"└─ Table size in MB: {size_in_mb}")

        return size_in_mb
