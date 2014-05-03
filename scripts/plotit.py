
import argparse

from Ditch.DBConnection import DBConnection
from Ditch.DBDitch import DBDitch
from Ditch.DitchLogger import DitchLogger
import plotly


def main():
    parser = argparse.ArgumentParser(description="plotit")

    args = parser.parse_args()

    conn = DBConnection()
    dbTable = DBDitch(conn)

    py = plotly.plotly(username='kutenai',key='xhhbxk2swl')

    readings = dbTable.queryLastNReadings(1000)

    print("Done. Retrieved %d records" % len(readings))

    x = [r['timestamp'].strftime("%Y %m %d %H:%M") for r in readings]
    y = [r['ditch_inches'] for r in readings]

    py.plot(x,y)

    print("Plotted results")


if __name__ == "__main__":

    main()
