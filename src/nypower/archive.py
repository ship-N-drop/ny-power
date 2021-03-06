import os

from influxdb import InfluxDBClient

INFLUX_DB = "ny-power"


class Archiver(object):

    def __init__(self):
        INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST")
        self.client = InfluxDBClient(
            INFLUXDB_HOST, 8086, 'root', 'root', INFLUX_DB)
        dbs = [x['name'] for x in self.client.get_list_database()]
        if INFLUX_DB not in dbs:
            self.client.create_database(INFLUX_DB)

    def save_computed(self, field, ts, units, value):
        pkt = [
            {
                "measurement": "%s_computed" % field,
                "time": ts,
                "tags": {
                    "units": units,
                },
                "fields": {
                    "value": value,
                }
            }
        ]
        self.client.write_points(pkt)

    def save_upstream(self, field, kind, ts, units, value):
        pkt = [
            {
                "measurement": field,
                "tags": {
                    "type": kind,
                    "units": units,
                },
                "time": ts,
                "fields": {
                    "value": value
                }
            }
        ]
        self.client.write_points(pkt)

    def get_timeseries(self, measure, since):
        res = self.client.query(
            "select value, units from %s where time >= now() - %s" %
            (measure, since))
        data = []
        ts = []
        units = ""
        for r in res.get_points():
            ts.append(r["time"])
            units = r["units"]
            data.append(r["value"])
        return dict(units=units, ts=ts, values=data)
