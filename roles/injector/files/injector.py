#!/usr/bin/env python

"""
Injector - batch ingestion of data after some cleaning

Usage: injector.py [-w WORKERS] -d datasource
"""

import argparse
import psycopg2
import psycopg2.extras
import threading
import csv
import os
import os.pathi
import time

from functools import partial
from concurrent import futures
from tabulate import tabulate


class InjectorService:

    def __init__(self, datasource, workers, logger):
        self.running = True
        self.csv = [{{ injector_csvs }}]
        self.start = False
        self.session = False
        self.datasource = datasource
        self.workers = workers
        self.logger = logger

        self.pg_conn()


    def pg_conn(self):
        try:
            self.logger.debug('connecting postgresql')
            conn = psycopg2.connect(dbname="{{ postgresql_db_name }}",
                                    user="{{ postgresql_user_name }}",
                                    password="{{ postgresql_user_password }}",
                                    port="{{ postgresql_port }}")
        except:
            self.logger.error('Could not connect to postgresql')
            sys.exit(1)
        self.conn = conn


    def is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False


    def worker(chunk, self, datasource):
        SQL_INS = ""
        if datasource.split('_')[2] == '3':
            SQL_INS = """
            INSERT INTO sessions(sessionid,
                                 device,
                                 duration)
                VALUES (%s, %s, %s) 
            """
        elif datasource.split('_')[2] == '2':
            SQL_INS = """
            INSERT INTO clicks(sessionid,
                               pageviewid,
                               total_clicks,
                               resp_clicks,
                               unresp_clicks)
                VALUES (%s, %s, %s, %s, %s)
            """
        else:
            SQL_INS = """
            INSERT INTO mouse_moves(sessionid,
                                    pageviewid,
                                    mouse_distance,
                                    duration_moves,
                                    no_moves)
                VALUES (%s, %s, %s, %s, %s)
            """

        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        self.logger.debug('starting parallel worker...')
        for rec in chunk:
            entry = ()
            for att in rec:
                if is_int(att):
                    entry += (att,)
                else:
                    entry += (None,)
            try:
                cur.execute(INSERT_SQL, entry)
            except psycopg2.DataError:
                self.logger.warn('Record %s not inserted!' % entry)

        self.conn.commit()
        cur.close()


    def injector(self, datasource):
        self.logger.info(('Thread injector for source '
                          '%s started') % datasource)

        while self.running:
            if not self.start:
                self.logger.info('no new data for %s, sleeping.' %
                                 datasource)
                time.sleep(5)
                continue
            path = os.path.join(self.datasource, datasource)
            if os.path.isfile(path):
                if not self.session or \
                  datasource.split('_')[2] != '3':
                    self.logger.info('no new data for %s, sleeping.' %
                            datasource)
                    time.sleep(5)
                    continue
                task = partial(self.worker, datasource)
                with futures.ThreadPoolExecutor(max_workers=self.workers) \
                     as executor:
                    futures_instances = []
                    with open(path) as csvfile:
                        reader = csv.reader(csvfile)
                        chunks = [reader[i:i + 100] \
                                  for i in xrange(0, len(reader), 100)]
                        for c in chunks:
                            futures_instances.append(executor.submit(task, rec))
                        futures.wait(futures_instances)

                        if datasource.split('_')[2] == '3':
                            self.session = True
                        ren = os.path.join(self.datasource,
                                           os.path.splitext(datasource)[0] + \
                                                            ".done")
                        os.rename(path, ren)
            else:
                self.logger.info('no new data for %s, sleeping.' % datasource)
                time.sleep(5)
                continue

    def coordinator(self):
        self.logger.info('Thread coordinator is started')

        while self.running:
            for f in self.csv:
                path = os.path.join(self.datasource, f)


    def start(self):
        self.running = True
        self.threads = []

        self.logger.info('Starting coordinator workers...')
        c = threading.Thread(target=self.coordinator)
        c.setDaemon(True)
        c.start()
        self.threads.append(c)

        self.logger.info('Starting injector workers...')

        for f in self.csv:
            t = threading.Thread(target=self.injector, args=(f,))
            t.setDaemon(True)
            t.start()
            self.threads.append(t)

        self.logger.info('Ready to inject...')

        while self.running:
            time.sleep(1000)
            for t in self.threads:
                if not t.is_alive():
                    self.logger.error('A thread crashed unexpectedly!!')
                    self.running = False

        for t in self.threads:
            t.join()

        print 'All injectors threads are going down!'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--datasource', help='where data is placed',
                        required=True, nargs='+')
    parser.add_argument('-w', '--workers', help='number of parallel workers',
                        default=3, type=int)

    args = parser.parse_args()
    datasource = args.datasource
    workers = args.workers

    if datasource is None:
        print >> sys.stderr, '-d option is mandatory'
        sys.exit(1)

    logger = set_loggers()

    i = InjectorService(datasource=datasource, workers=workers, logger=logger)
    i.start()


def set_loggers(destination):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.{{ injector_log_level }})
    handler = logging.FileHandler("{{ injector_log_destination }}")
    handler.setLevel(logging.{{ injector_log_level }})
    formatter = logging.Formatter('%(asctime)s - %(name)s \
                                  - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

if __name__ == '__main__':
    sys.exit(main())
