#!/usr/bin/env python
# -*- coding: utf-8 -*-
from synapse.persistence import read_schema
from synapse.federation import ReplicationHandler

from synapse.server import HomeServer

from synapse.util import DbPool

from twisted.internet import reactor
from twisted.enterprise import adbapi
from twisted.python.log import PythonLoggingObserver

import argparse
import logging
import sqlite3


logger = logging.getLogger(__name__)


class HomeServerReplicationHandler(ReplicationHandler):
    def __init__(self, hs):
        hs.get_federation().set_handler(self)

    def on_receive_pdu(self, pdu):
        pdu_type = pdu.pdu_type
        print "#%s (receive) *** %s" % (pdu.context, pdu_type)


def setup_db(db_name):
    """ Set up all the dbs. Since all the *.sql have IF NOT EXISTS, so we don't
    have to worry about overwriting existing content.

    Args:
        db_name : The path to the database.
    """
    logging.info("Preparing database: %s...", db_name)
    pool = adbapi.ConnectionPool(
        'sqlite3', db_name, check_same_thread=False,
        cp_min=1, cp_max=1)

    # set the dbpool global so other layers can access it
    DbPool.set(pool)

    schemas = [
            "transactions",
            "pdu",
            "users",
            "im"
    ]

    for sql_loc in schemas:
        sql_script = read_schema(sql_loc)

        with sqlite3.connect(db_name) as db_conn:
            c = db_conn.cursor()
            c.executescript(sql_script)
            c.close()
            db_conn.commit()


def setup_logging(verbosity=0, filename=None, config_path=None):
    """ Sets up logging with verbosity levels.

    Args:
        verbosity: The verbosity level.
        filename: Log to the given file rather than to the console.
        config_path: Path to a python logging config file.
    """

    if config_path is None:
        if verbosity == 0:
            level = logging.WARNING
        elif verbosity == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG

        logging.basicConfig(level=level, filename=filename)
    else:
        logging.config.fileConfig(config_path)

    observer = PythonLoggingObserver()
    observer.start()


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", type=int, default=8080,
                        help="The port to listen on.")
    parser.add_argument("-d", "--database", dest="db", default="homeserver.db",
                        help="The database name.")
    parser.add_argument("-H", "--host", dest="host", default="localhost",
                        help="The hostname of the server.")
    parser.add_argument('-v', '--verbose', dest="verbose", action='count',
                        help="The verbosity level.")
    args = parser.parse_args()

    setup_logging(args.verbose)

    # setup and run with defaults if not specified
    setup_db(args.db)

    logger.info("Server hostname: %s", args.host)

    hs = HomeServer(args.host)

    # This object doesn't need to be saved because it's set as the handler for
    # the replication layer
    HomeServerReplicationHandler(hs)

    # TODO(paul): Should this always be done by the construction process itself?
    hs.get_rest_servlet_factory().register_servlets(hs.get_http_server())

    hs.get_http_server().start_listening(args.port)

    reactor.run()


if __name__ == '__main__':
    run()
