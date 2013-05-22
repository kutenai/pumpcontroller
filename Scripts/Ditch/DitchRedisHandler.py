
import os.path
import os
import socket
import redis
from redis.exceptions import (
    ConnectionError,
    )

from time import time

class DitchRedisHandler(object):

    def __init__(self,host,port,db):
        self.host= host
        self.port = port
        self.db = db
        self.redis = None
        self.isConnected = False
        self.myid = "None"

    def redisConnect(self):

        self.myid = 'server:' + socket.gethostname() + ":%d" % os.getpid()
        self.lprint("Connect to Redis on %s:%s DB=%s" % (self.host,self.port,self.db))
        self.redis = redis.StrictRedis(host=self.host, port=self.port, db=self.db)

        try:
            self.redis.ping()
            self.lprint("Done..")
            self.isConnected = True
        except ConnectionError:
            # Failed to connect to redist..
            self.lprint("Redis connect failed..")
            self.redis = None
            self.isConnected = False
            return False
        except Exception as e:
            self.lprint("General exception thrown connecting to redis.")

        return True

    def redisDisconnect(self):
        # We are ending now.. deregister with redis
        self.hdel(self.myid)
        self.srem('servers',self.myid)
        self.lprint("Deregistered from redis server.")

    def hset(self,hash,key,value):

        try:
            self.redis.hset(hash,key,value)
        except:
            # Failed.. perhaps redis is down?
            self.isConnected = False
            return False
        return True

    def hget(self,hash,key):

        try:
            return self.redis.hget(hash,key)
        except:
            # Failed.. perhaps redis is down?
            self.isConnected = False
            return None

    def hdel(self,key):

        try:
            self.redis.hdel(key)
        except:
            self.isConnected = False

    def sadd(self,setname,value):

        try:
            self.redis.sadd(setname,value)
        except:
            self.isConnected = False

    def srem(self,setname,value):

        try:
            self.redis.srem(setname,value)
        except:
            # Failed.. perhaps redis is down?
            self.isConnected = False
            return False
        return True

    def lpush(self,listname,value):

        try:
            self.redis.lpush(listname,value)
        except:
            self.isConnected = False

    def rpop(self,listname):

        try:
            return self.redis.rpop(listname)
        except:
            self.isConnected = False
        return None

    def brpop(self,listname,timeout):

        try:
            return self.redis.brpop(listname,timeout)
        except:
            self.isConnected = False
            return None

    def exists(self,key):

        try:
            return self.redis.exists(key)
        except:
            self.isConnected = False
            return False

