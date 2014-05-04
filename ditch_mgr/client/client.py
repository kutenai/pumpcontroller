#!/usr/bin/env python

from json import loads

from celery import Celery,group,chain

app = Celery('mgr.tasks')
app.config_from_object('mgr.celeryconfig')

#app2 = Celery('gbmgr.tasks')
#app2.config_from_object('gbmgr.celeryconfig')

#@app2.task
#def onstatus(d):
#    """
#    Handler for status results..
#    :param d:
#    :return:
#    """
#    print("Status:%s" % loads(d))

@app.task
def status():
    pass


@app.task
def read_sensors():
    pass


@app.task
def pump_enable(bEnable):
    pass


@app.task
def south_enable(bEnable):
    pass


@app.task
def north_enable(bEnable):
    pass


@app.task
def add(x,y):
    return x + y


@app.task
def mul(x,y):
    return x * y


if __name__ == "__main__":

    #bigres = chain(pump_enable(True) | status | pump_enable(False))().get()
    #print("Bug Result:%s" + bigres)
    pump_enable.delay(False)

    g = chain(add.s(4) | mul.s(8))
    print("Check this out:%s" % g(4).get())

    print("Value is %s" % add.delay(2,2).get())
    result = group(add.s(i,i) for i in xrange(10))().get()
    print(result)

    print("Main dealio is done..")
