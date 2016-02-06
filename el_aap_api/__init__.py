__author__ = 'schlitzer'
# stdlib
import argparse
import configparser
import signal
import sys
import time
from logging.handlers import TimedRotatingFileHandler

# 3rd party
from bottle import run
from pep3143daemon import DaemonContext, PidFile
import pymongo
from requestlogger import WSGILogger, ApacheFormatter

# Project
from el_aap_api.app import app, app_logger
from el_aap_api.controllers import *
from el_aap_api.models import *
from el_aap_api.errors import error_catcher


def main():
    parser = argparse.ArgumentParser(description="ElasticSearch Authentication and Authorization Proxy API")

    parser.add_argument("--cfg", dest="cfg", action="store",
                        default="/etc/el_aap/el_aap_api.ini",
                        help="Full path to configuration")

    parser.add_argument("--pid", dest="pid", action="store",
                        default="/var/run/el_aap/el_aap_api.pid",
                        help="Full path to PID file")

    parser.add_argument("--nodaemon", dest="nodaemon", action="store_true",
                        help="Do not daemonize, run in foreground")

    subparsers = parser.add_subparsers(help='commands', dest='method')
    subparsers.required = True

    quit_parser = subparsers.add_parser('quit', help='Stop ElasticSearch Authentication and Authorization Proxy API')
    quit_parser.set_defaults(method='quit')

    start_parser = subparsers.add_parser('start', help='Start ElasticSearch Authentication and Authorization Proxy API')
    start_parser.set_defaults(method='start')

    devel_parser = subparsers.add_parser('devel', help='Start ElasticSearch Authentication and Authorization Proxy API in developement mode')
    devel_parser.set_defaults(method='devel')

    indicies_parser = subparsers.add_parser('indices', help='create indices and exit')
    indicies_parser.set_defaults(method='indices')

    admin_parser = subparsers.add_parser('create_admin', help='create default admin user')
    admin_parser.set_defaults(method='create_admin')

    parsed_args = parser.parse_args()

    if parsed_args.method == 'quit':
        el_aapapi = ElasticSearchAAPAPI(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aapapi.quit()

    elif parsed_args.method == 'start':
        el_aapapi = ElasticSearchAAPAPI(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aapapi.start()

    elif parsed_args.method == 'devel':
        el_aapapi = ElasticSearchAAPAPI(
                cfg=parsed_args.cfg,
                pid=parsed_args.pid,
                nodaemon=parsed_args.nodaemon
        )
        el_aapapi.start(devel=True)

    elif parsed_args.method == 'indices':
        el_aapapi = ElasticSearchAAPAPI(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aapapi.manage_indices()

    elif parsed_args.method == 'create_admin':
        el_aapapi = ElasticSearchAAPAPI(
            cfg=parsed_args.cfg,
            pid=parsed_args.pid,
            nodaemon=parsed_args.nodaemon
        )
        el_aapapi.create_admin()


class ElasticSearchAAPAPI(object):
    def __init__(self, cfg, pid, nodaemon):
        self._config_file = cfg
        self._config = configparser.ConfigParser()
        self._mongo_pools = dict()
        self._mongo_colls = dict()
        self._pid = pid
        self._nodaemon = nodaemon

    def _app(self, devel=False):
        self._setup_pools()
        self._setup_colls()

        permissions = Permissions(self._mongo_colls['permissions'])
        roles = Roles(self._mongo_colls['roles'])
        session = Sessions(self._mongo_colls['sessions'])
        users = Users(self._mongo_colls['users'])

        app.install(MetaPlugin(permissions, 'm_permissions'))
        app.install(MetaPlugin(roles, 'm_roles'))
        app.install(MetaPlugin(session, 'm_sessions'))
        app.install(MetaPlugin(users, 'm_users'))
        app.install(error_catcher)

        # access log logger
        acc_handlers = []

        try:
            access_log = self.config.get('file:logging', 'acc_log')
            access_retention = self.config.getint('file:logging', 'acc_retention')
            acc_handlers.append(TimedRotatingFileHandler(access_log, 'd', access_retention))
        except (configparser.NoOptionError, configparser.NoSectionError):
            pass

        logapp = WSGILogger(app, acc_handlers, ApacheFormatter())

        # application logger
        app_handlers = []

        try:
            access_log = self.config.get('file:logging', 'app_log')
            app_retention = self.config.getint('file:logging', 'app_retention')
            app_handlers.append(TimedRotatingFileHandler(access_log, 'd', app_retention))
        except (configparser.NoOptionError, configparser.NoSectionError):
            pass

        for handler in app_handlers:
            app_logger.addHandler(handler)

        run(app=logapp, host='0.0.0.0', port=self.config.getint('main', 'port'), debug=devel, reloader=devel, server='waitress')

    def _setup_pools(self):
        for section in self.config.sections():
            if section.endswith(':mongopool'):
                sectionname = section.rsplit(':', 1)[0]
                pool = pymongo.MongoClient(
                    host=self.config.get(section, 'host'),
                    port=self.config.getint(section, 'port'),
                    serverSelectionTimeoutMS=10
                )
                db = pool.get_database(self.config.get(section, 'db'))
                try:
                    user = self.config.get(section, 'user')
                    password = self.config.get(section, 'pass')
                    db.authenticate(user, password)
                except configparser.NoOptionError:
                    pass
                self._mongo_pools[sectionname] = db

    def _setup_colls(self):
        for section in self.config.sections():
            if section.endswith(':mongocoll'):
                sectionname = section.rsplit(':', 1)[0]
                pool = self._mongo_pools[self.config.get(section, 'pool')]
                coll = pool.get_collection(self.config.get(section, 'coll'))
                self._mongo_colls[sectionname] = coll

    @property
    def config(self):
        return self._config

    @property
    def pid(self):
        return self._pid

    @property
    def nodaemon(self):
        return self._nodaemon

    def create_admin(self):
        self.config.read_file(open(self._config_file))
        self._setup_pools()
        self._setup_colls()

        admin = {
            "_id": "default_admin",
            "admin": True,
            "email": "admin@example.com",
            "name": "Default Admin User",
            "password": "password"
        }

        users = Users(self._mongo_colls['users'])
        users.create(admin)

    def manage_indices(self):
        self.config.read_file(open(self._config_file))
        self._setup_pools()
        self._setup_colls()

        sessions = self._mongo_colls['sessions']
        sessions.create_index([('lastused', pymongo.ASCENDING)], expireAfterSeconds=3600)

    def quit(self):
        try:
            pid = open(self.pid).readline()
        except IOError:
            print("Daemon already gone, or pidfile was deleted manually")
            sys.exit(1)
        print("terminating Daemon with Pid: {0}".format(pid))
        os.kill(int(pid), signal.SIGTERM)
        sys.stdout.write("Waiting...")
        while os.path.isfile(self.pid):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(0.5)
        print("Gone")

    def start(self, devel=False):
        self.config.read_file(open(self._config_file))
        if devel:
            self._app(devel=True)
            return
        daemon = DaemonContext(pidfile=PidFile(self.pid))
        if self.nodaemon:
            daemon.detach_process = False
        dlog = open(self.config.get('main', 'dlog'), 'w')
        daemon.stderr = dlog
        daemon.stdout = dlog
        daemon.open()

        self._app()

