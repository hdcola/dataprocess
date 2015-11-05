#!/usr/bin/env python
# encoding: utf-8

import MySQLdb
import ConfigParser
import sys
import logging
import time

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='../../log/db_engine.log',
                    filemode='w+')

reload(sys)
sys.setdefaultencoding('utf8')


class DB_Engine(object):
    def __init__(self):
        self.host = ""
        self.port = 0
        self.user = ""
        self.passwd = ""
        self.output_path = ""

        self.initConfig()
        self.db_name = "mgboss"

    def initConfig(self):
        Conf = ConfigParser.ConfigParser()
        path = sys.path[0]
        Conf.read(path + "/../conf/service.conf")

        try:
            self.host = Conf.get("db", "db_host")
            self.port = Conf.getint("db", "db_port")
            self.user = Conf.get("db", "db_user")
            self.passwd = Conf.get("db", "db_passwd")
            self.output_path = Conf.get("meizi", "output_path")
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            logging.error("initConfig fail:%s" % str(e))
            sys.exit(-1)

    def select_from_table(self):
        _res = ()
        try:
            _conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db_name, charset="utf8")
        except MySQLdb.Error as e:
            logging.error("Mysql connect error:%s" % str(e))
            return _res

        _cursor = _conn.cursor()

        _sql = "SELECT source.sourceId, source.format, channel.activityId, channel.channelName, channel.channelId, source.cameraPosition, " \
               "source.terminal, time.timeId, time.startTime, time.endTime " \
               "from " \
               "asset_live_source as source, " \
               "asset_livesource_attribute as attribute, " \
               "asset_live_channels as channel, " \
               "asset_live_source_time as time " \
               "where source.channelId = channel.channelId " \
               "and source.cameraPosition = attribute.attrID " \
               "and time.sourceId = source.sourceId;"

        try:
            _cursor.execute(_sql)
            _res = _cursor.fetchall()
            _conn.commit()
        except MySQLdb.Error as e:
            logging.error("Mysql fetch error:%s" % str(e))
        finally:
            _cursor.close()
            _conn.close()

        return _res

if __name__ == '__main__':
    db_client = DB_Engine()
    res = db_client.select_from_table()
    if len(res) == 0:
        logging.error("The result Mysql fetch is 0!")
        sys.exit(-1)

    curtime = time.time()
    timedata = time.localtime(int(curtime))
    time_now = time.strftime("%Y%m%d%H", timedata)

    file = db_client.output_path + '/' + time_now + '_live.csv'
    try:
        ofp = open(file, 'a+')
    except IOError as e:
        logging.error("IOError:%s" % str(e))
        exit(-1)

    for record in res:
        output = ','.join([str(tmp) for tmp in record])
        ofp.write(output+'\n')

    ofp.close()
