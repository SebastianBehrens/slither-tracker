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

    def query(self, query: str, fetch = 'all', flg_commit = False, flg_print_query = False):
        if flg_print_query:
            print(query)
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
        
    def compute_rank_runs(self, timestamp=None):
        """
        Compute user rank runs for records at a specific timestamp.
        
        Args:
            timestamp: datetime object for the timestamp to process records for.
                      If None, processes all records.
        """
        timestamp_str = timestamp.isoformat() if timestamp else None
        self.logger.info(f"Computing rank runs for timestamp: {timestamp_str}")
        
        # First, ensure we have a table to store the runs
        self.create_user_run_table()
        
        # Open new runs for users who appear for the first time
        self.open_new_runs(timestamp_str)
        
        # Close runs for users who are no longer visible
        self.close_inactive_runs(timestamp_str)
        
        self.logger.info("Rank runs computation completed.")
    
    def open_new_runs(self, timestamp_str=None):
        """
        Open new runs for users who appear for the first time in the leaderboard.
        
        Args:
            timestamp_str: ISO format string of the timestamp to process.
                          If None, processes all records.
        """
        self.logger.info(f"Opening new runs for timestamp: {timestamp_str}")
        if self.database_type == 'sqlite':
            query = f'''
                WITH current_records AS (
                    SELECT 
                        server_id,
                        nick,
                        created_at,
                        score,
                        rank
                    FROM server_user_rank
                    WHERE created_at = '{timestamp_str}'
                ),
                previous_timestamp AS (
                    SELECT MAX(created_at) as prev_time
                    FROM server_user_rank
                    WHERE created_at < '{timestamp_str}'
                ),
                previous_records AS (
                    SELECT 
                        server_id,
                        nick
                    FROM server_user_rank
                    WHERE created_at = (SELECT prev_time FROM previous_timestamp)
                ),
                existing_open_runs AS (
                    SELECT 
                        server_id,
                        nick
                    FROM user_run
                    WHERE end_time IS NULL
                )
                INSERT OR IGNORE INTO user_run (server_id, nick, start_time, max_score, min_rank, created_at)
                SELECT 
                    cur.server_id,
                    cur.nick,
                    cur.server_time,
                    cur.score,
                    cur.rank,
                    '{timestamp_str}' AS created_at
                FROM current_records cur
                WHERE NOT EXISTS (
                    SELECT 1 FROM existing_open_runs r
                    WHERE r.server_id = cur.server_id
                    AND r.nick = cur.nick
                    AND r.end_time IS NULL
                )
                AND NOT EXISTS (
                    SELECT 1 FROM previous_records prev
                    WHERE prev.server_id = cur.server_id
                    AND prev.nick = cur.nick
                )
            '''
        elif self.database_type == 'postgres':
            query = f'''
                WITH current_records AS (
                    SELECT 
                        server_id,
                        nick,
                        created_at,
                        score,
                        rank
                    FROM server_user_rank
                    WHERE created_at = '{timestamp_str}'
                ),
                previous_timestamp AS (
                    SELECT MAX(created_at) as prev_time
                    FROM server_user_rank
                    WHERE created_at < '{timestamp_str}'
                ),
                previous_records AS (
                    SELECT 
                        server_id,
                        nick
                    FROM server_user_rank
                    WHERE created_at = (SELECT prev_time FROM previous_timestamp)
                ),
                open_runs AS (
                    SELECT 
                        server_id,
                        start_time,
                        end_time,
                        nick
                    FROM user_run
                    WHERE end_time IS NULL
                )
                INSERT INTO user_run (server_id, nick, start_time, max_score, min_rank, created_at)
                SELECT 
                    cur.server_id,
                    cur.nick,
                    cur.created_at,
                    cur.score,
                    cur.rank,
                    '{timestamp_str}' AS created_at
                FROM current_records cur
                WHERE NOT EXISTS (
                    SELECT 1 FROM open_runs
                    WHERE open_runs.server_id = cur.server_id
                    AND open_runs.nick = cur.nick
                    AND open_runs.end_time IS NULL
                )
                AND NOT EXISTS (
                    SELECT 1 FROM previous_records prev
                    WHERE prev.server_id = cur.server_id
                    AND prev.nick = cur.nick
                )
                ON CONFLICT (server_id, nick, start_time) DO NOTHING
            '''
        
        self.query(query, fetch='none', flg_commit=True, flg_print_query=False)
    
    def close_inactive_runs(self, timestamp_str=None):
        """
        Close runs for users who are no longer visible in the latest data.
        
        Args:
            timestamp_str: ISO format string of the timestamp to process.
                          If None, processes all records.
        """
        self.logger.info(f"Closing inactive runs for timestamp: {timestamp_str}")
        if self.database_type == 'sqlite':
            query = f'''
                WITH previous_timestamp AS (
                    SELECT MAX(created_at) as max_time
                    FROM server_user_rank
                    WHERE created_at < '{timestamp_str}'
                ),
                current_users AS (
                    SELECT DISTINCT
                        server_id,
                        nick
                    FROM server_user_rank
                    WHERE created_at = '{timestamp_str}'
                ),
                open_runs_to_close AS (
                    SELECT
                        r.server_id,
                        r.nick,
                        r.start_time
                    FROM user_run r
                    WHERE r.end_time IS NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM current_users cu
                        WHERE cu.server_id = r.server_id
                        AND cu.nick = r.nick
                    )
                )
                UPDATE user_run
                SET 
                    end_time = (SELECT max_time FROM previous_timestamp),
                    duration_seconds = CAST(
                        (JULIANDAY((SELECT max_time FROM previous_timestamp)) - JULIANDAY(start_time)) * 86400 AS INTEGER
                    )
                WHERE (server_id, nick, start_time) IN (
                    SELECT server_id, nick, start_time FROM open_runs_to_close
                )
            '''
        elif self.database_type == 'postgres':
            query = f'''
                WITH previous_timestamp AS (
                    SELECT MAX(created_at) as max_time
                    FROM server_user_rank
                    WHERE created_at < '{timestamp_str}'
                ),
                current_users AS (
                    SELECT DISTINCT
                        server_id,
                        nick
                    FROM server_user_rank
                    WHERE created_at = '{timestamp_str}'
                ),
                open_runs_to_close AS (
                    SELECT
                        r.server_id,
                        r.nick,
                        r.start_time
                    FROM user_run r
                    WHERE r.end_time IS NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM current_users cu
                        WHERE cu.server_id = r.server_id
                        AND cu.nick = r.nick
                    )
                )
                UPDATE user_run
                SET 
                    end_time = (SELECT max_time FROM previous_timestamp),
                    duration_seconds = EXTRACT(EPOCH FROM (
                        (SELECT max_time FROM previous_timestamp) - start_time
                    ))::INTEGER
                WHERE (server_id, nick, start_time) IN (
                    SELECT server_id, nick, start_time FROM open_runs_to_close
                )
            '''
        
        self.query(query, fetch='none', flg_commit=True, flg_print_query=False)

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

    def inspect_server_user_rank(self, timestamp: dt.datetime):
        query = f'''
            SELECT * FROM server_user_rank
            WHERE created_at = '{timestamp}';
        '''
        records = self.query(query, fetch='all', flg_commit=False)
        print("\n\n server_user_rank: ================================")
        print(dataframe(records))
        print("====================================================\n\n")
    
    def inspect_user_run(self, timestamp: dt.datetime):
        query = f'''
            SELECT * FROM user_run
        '''
        records = self.query(query, fetch='all', flg_commit=False)
        print("\n\n user_run: ================================")
        print(dataframe(records))
        print("====================================================\n\n")
            

    def insert_test_cases(self):

        if click.confirm("Do you want to truncate the server_user_rank table and continue to insert test cases?", default=False):
            self.truncate_server_user_rank()
            self.truncate_user_run()
        else:
            print("Operation cancelled.")
            return

        datetime1 = dt.datetime.now(dt.timezone.utc)
        datetime2 = datetime1 + dt.timedelta(seconds=10)
        datetime3 = datetime2 + dt.timedelta(seconds=10)
        datetime4 = datetime3 + dt.timedelta(seconds=10)
        datetime5 = datetime4 + dt.timedelta(seconds=10)
        

        # Users:
        data_timestamp1 = {
                'server_id': 'test_server_1',
                'server_ip': '127.0.0.1',
                'server_time': datetime1.isoformat(),
                'created_at': datetime1.isoformat(),
                'records': [
                    {"rank": 8, "nick": "UserA", "score": 100},
                    {"rank": 5, "nick": "UserC", "score": 100}
                ]
            }

        data_timestamp2 = {
                'server_id': 'test_server_1',
                'server_ip': '127.0.0.1',
                'server_time': datetime2.isoformat(),
                'created_at': datetime2.isoformat(),
                'records': [
                {"rank": 5, "nick": "UserA", "score": 100}
            ]
        }

        data_timestamp3 = {
                'server_id': 'test_server_1',
                'server_ip': '127.0.0.1',
                'server_time': datetime3.isoformat(),
                'created_at': datetime3.isoformat(),
                'records': [
                    {"rank": 1, "nick": "UserB", "score": 150}
                ]
            }

        data_timestamp4 = {
                'server_id': 'test_server_1',
                'server_ip': '127.0.0.1',
                'server_time': datetime4.isoformat(),
                'created_at': datetime4.isoformat(),
                'records': [
                    {"rank": 1, "nick": "UserB", "score": 150}
                ]
            }
        self.server_user_rank_insert(
            data_timestamp1,
            created_at = datetime1
            )
        self.compute_rank_runs(timestamp = datetime1)
        
        self.inspect_server_user_rank(datetime1)
        self.inspect_user_run(datetime1)
        if click.confirm("Do you want to continue to insert test cases?", default=False):
            pass
        else:
            return

        self.server_user_rank_insert(
            data_timestamp2,
            created_at = datetime2
            )
        self.compute_rank_runs(timestamp = datetime2)
        
        self.inspect_server_user_rank(datetime2)
        self.inspect_user_run(datetime2)
        if click.confirm("Do you want to continue to insert test cases?", default=False):
            pass
        else:
            return

        self.server_user_rank_insert(
            data_timestamp3,
            created_at = datetime3
        )
        self.compute_rank_runs(timestamp = datetime3)
        
        self.inspect_server_user_rank(datetime3)
        self.inspect_user_run(datetime3)
        if click.confirm("Do you want to continue to insert test cases?", default=False):
            pass
        else:
            return

        self.server_user_rank_insert(
            data_timestamp4,
            created_at = datetime4
        )
        self.compute_rank_runs(timestamp = datetime4)

        self.inspect_server_user_rank(datetime4)
        self.inspect_user_run(datetime4)
        
    def user_run_table_exists(self):
        if self.database_type == 'sqlite':
            query = '''
                SELECT name FROM sqlite_master WHERE type='table' AND name='user_run';
            '''
        elif self.database_type == 'postgres':
            query = '''
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='user_run'
                );
            '''
        return self.query(query, fetch='one', flg_commit=False)

    def create_user_run_table(self):
        """Create the table to store user runs if it doesn't exist."""
        if self.database_type == 'sqlite':
            query = '''
                CREATE TABLE IF NOT EXISTS user_run (
                    server_id TEXT,
                    nick TEXT,
                    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    end_time TIMESTAMP WITH TIME ZONE,
                    duration_seconds INTEGER,
                    max_score INTEGER,
                    min_rank INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (server_id, nick, start_time)
                )
            '''
        elif self.database_type == 'postgres':
            query = '''
                CREATE TABLE IF NOT EXISTS user_run (
                    server_id TEXT,
                    nick TEXT,
                    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    end_time TIMESTAMP WITH TIME ZONE,
                    duration_seconds INTEGER,
                    max_score INTEGER,
                    min_rank INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (server_id, nick, start_time)
                )
            '''
        self.query(query, fetch='none', flg_commit=True)


