__author__ = 'kutenai'

import os
import json
import re
import MySQLdb
from time import strftime

from DBConnection import *

class DBDitch(DBConnUser):

    def __init__(self,connection):
        super(DBDitch,self).__init__(connection)

        self.setTableNames()

    def setTableNames(self):

        self.ditchLog = "ditch_log"

    def clearLog(self):
        """
        Just delete all from the current tables.
        """
        curs = self.getCursor()
        curs.execute("delete from %s" % self.ditchLog)
        curs.execute("alter table %s AUTO_INCREMENT=1" % self.compTable)

    def insertLogEntry(self,ditchlvl,sumplvl,pumpOn):

        ctime = strftime('%Y-%m-%d %H:%M:%S')

        sql = """
            insert into %s
            (
                logtime,
                ditch_level,
                sump_level,
                pump_status
            ) values (
                "%s", %d, %d, %d
            )

            """ % (self.ditchLog,
                   ctime,
                   ditchlvl, sumplvl, pumpOn
                )

        curs = self.getCursor()
        curs.execute(sql)

def main():

    # Left over.. could put some test code here.
    pass


if __name__ == '__main__':
    main()
