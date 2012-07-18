__author__ = 'kutenai'

import os
import json
import re
import MySQLdb

class DBCursor(object):

    def __init__(self,conn,database):
        self.curs = None
        if conn:
            try:
                self.curs = conn.cursor()
                self.curs.execute('use ' + database)
            except MySQLdb.Error as e:
                print "Failed to get cursor. MySQLdb error: %d:%s" % (e.args[0], e.args[1])

            self.conn = conn

        if not self.curs:
            raise "Could not create a DB Cursor.."

    def __del__(self):
        pass

    def cursor(self):
        return self.curs

    def execute(self,sql):
        if self.curs:
            self.curs.execute(sql)

    def fetchone(self):
        if self.curs is None: raise "Cursor invalid"
        return self.curs.fetchone()

    def fetchoneDict(self):
        """
        Return a row from the cursor formatted as a dictionary.

        This function was taken from this site:
          http://www.halfcooked.com/mt/archives/000969.html


        Give credit, where credit due!
        """
        if self.curs is None: raise "Cursor invalid."

        row = self.curs.fetchone()
        if row is None: return None
        cols = [ d[0] for d in self.curs.description ]
        return dict(zip(cols, row))

    def fetchallDict(self):
        """
        Fetch all rows as an array of dictionaries.
        """

        rows = []
        row = self.fetchoneDict()
        while row:
            rows.append(row)
            row = self.fetchoneDict()

        return rows

    def fetchallObj(self):
        """
        Fetch all rows as an array of objects.
        """

        class DBRow:
            def __init__(self,row):
                self.row = row
            def __getattr__(self,item):
                if self.row.has_key(item):
                    return self.row[item]
                raise Exception("Item %s does not exist." % item)
            def __repr__(self):
                s = "DBRow "
                s = s + ";".join([key + ":" + str(self.row[key]) for key in self.row.keys()])
                return s

        rows = []
        row = self.fetchoneDict()
        while row:
            rows.append(DBRow(row))
            row = self.fetchoneDict()

        return rows

    def updateRow(self, table, **data):
        """
        Return a row from the cursor formatted as a dictionary.

        This function was taken from this site:
          http://www.halfcooked.com/mt/archives/000969.html


        Give credit, where credit due!
        """

        if self.curs is None: raise "Cursor invalid."

        idName = table + "_id"
        id = data[idName]
        del data[idName]
        sets = []
        for key in data.keys():
            sets.append("%s = %%s" % key)
            set = ', '.join(sets)
            qq = "UPDATE %s SET %s WHERE %s = %%s" % (table, set, idName,)
            self.curs.execute(qq, tuple(data.values()+[id]))

    def insertRow(self, table, **data):
        """
        Return a row from the cursor formatted as a dictionary.

        This function was taken from this site:
          http://www.halfcooked.com/mt/archives/000969.html


        Give credit, where credit due!
        """

        if self.curs is None: raise "Cursor invalid."

        keys = ', '.join(data.keys())
        vals = ', '.join(["%s"] * len(data.values()))
        qq = "INSERT INTO %s (%s) VALUES (%s)" % (table, keys, vals)
        self.curs.execute(qq, tuple(data.values()))
        return self.curs.lastrowid

    def insert_id(self):
        """
        Retrieve the last insert Id from the connection.
        """
        return self.conn.insert_id()

class DBConnection(object):

    dests = ['local']

    def __init__(self,dest="local",db=None):

        # Use passed in value if set
        if db:
            self.db = db

        if dest == 'local':
            self.hosts = [
                {
                    'host':'bondinorth.deepbondi.net',
                    'port':3306
                },
            ]
            self.port = 3306
            self.user = 'ditchuser'
            self.pw = '11dKk21!'
            if not db:
                self.db = 'ditch_db'
        else:
            raise "Invalid DB Destination"


        self.conn = None
        self.curs = None

    @classmethod
    def validDestinations(cls):
        return cls.dests

    def __del__(self):
        if self.conn:
            MySQLdb.connection.close(self.conn)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def getConnection(self):
        """
        Return the current connect. Open one if none exists.

        Note that an SSH tunnel is required to  make this work..
        That tunnel must be setup on the local host before executing the script
        The hostname is eeweb.com, and the tunnel must forward local 3316 to
        the remote 3306

        P.S. - I changed the local forward port to 3316.
        """

        if self.conn == None:
            try:
                conn = None
                for hostval in self.hosts:
                    host = hostval['host']
                    port = hostval['port']
                    try:
                        print "Trying DB connection to %s at %d" % (host,port)
                        conn = MySQLdb.connect(host=host,
                                               port=port,
                                               user=self.user,
                                               passwd=self.pw)
                    except MySQLdb.Error as e:
                        conn = None
                        pass

                    if conn:
                        break


                if not conn:
                    raise Exception("Failed to open Database connection.","-1001")
                else:
                    self.conn = conn

            except MySQLdb.Error as e:
                print "Failed to open connection. MySQLdb error: %d:%s" % (e.args[0], e.args[1])
            except:
                return None
        return self.conn

    def getCursor(self):
        """
        Return a cursor and use the proper database.
        """

        conn = self.getConnection()

        if not conn:
            raise Exception("Could not establish Database connection.",'-1000')

        return DBCursor(conn,self.db)

    def insertId(self):

        return self.conn.insert_id()

class DBConnUser(object):

    def __init__(self,connection):
        self.conn = connection

    def getCursor(self):
        return self.conn.getCursor()

    def insertId(self):
        return self.conn.insertId()


def main():

    # Left over.. could put some test code here.
    pass


if __name__ == '__main__':
    main()
