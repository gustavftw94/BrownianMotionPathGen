from dataclasses import dataclass
from shapely import geometry
from datetime import datetime, timedelta
from typing import List
import csv
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from alive_progress import alive_bar

@dataclass
class Settings:
    boundary: geometry.Polygon
    timestep: timedelta
    n_steps: int
    migration_factor = 0.005
    start_time: datetime = datetime.now()

class InfluxConnection():
    def __init__(self):
        self.token = os.environ.get("INFLUXDB_TOKEN")
        self.org = "VestiTech Data"
        self.url = "https://eu-central-1-1.aws.cloud2.influxdata.com"
        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.bucket = "ontrack-fake-sensor-data"
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def clean_bucket(self, days_back):
        """
        Delete Time series data from InfluxDB.

        :param str, datetime.datetime start: start time
        :param str, datetime.datetime stop: stop time
        :param str predicate: predicate
        :param str bucket: bucket id or name from which data will be deleted
        :param str, Organization org: specifies the organization to delete data from.
                                      Take the ``ID``, ``Name`` or ``Organization``.
                                      If not specified the default value from ``InfluxDBClient.org`` is used.
        :return:
        """
        start = datetime.now() - timedelta(days=days_back)
        stop = datetime.now()
        self.client.delete_api().delete(start=start, stop=stop, bucket=self.bucket, org=self.org, predicate="")

    def write(self, point:Point):
        self.write_api.write(bucket=influx_connection.bucket, org=self.org, record=point)

    def get_historical_data(self, hours_back:int, device_id:str, measurement_type:str):
        query = f"""from(bucket: "ontrack-fake-sensor-data")
         |> range(start: -{hours_back}h)
         |> filter(fn:(r) => r.id == "{device_id}")
         |> filter(fn:(r) => r._measurement == "{measurement_type}")"""
        query_api = self.client.query_api()
        tables = query_api.query(query, org=self.org)
        for table in tables:
            for record in table.records:
                print(record)


influx_connection = InfluxConnection()


class Result:
    def __init__(self, settings: Settings):
        self.positions: List[geometry.Point] = []
        self.timestamps: List[datetime] = []
        self.settings = settings
        self._timedelta = self.settings.timestep
        self.end_time = self.settings.start_time - (
            self.settings.n_steps * self._timedelta
        )

    def to_csv(self, filename: str):
        ## save positions and timestamps to csv file
        result_dict = {
            "x": [p.x for p in self.positions],
            "y": [p.y for p in self.positions],
            "timestamp": self.timestamps,
        }
        _range = range(len(self.positions) - 1)

        cols = []
        datatypes = ["#datatype","double", "double", "dateTime"]
        cols.append(datatypes)
        cols.append(result_dict.keys())
        for i in _range:
            row = [
                result_dict["x"][i],
                result_dict["y"][i],
                result_dict["timestamp"][i],
            ]
            cols.append(row)

        with open(filename, "w") as f:
            w = csv.writer(f)
            w.writerows(cols)

    def write_result_to_influx(self,device_id: str):
        with alive_bar(len(self.positions)) as bar:
            for pos, time in zip(self.positions,self.timestamps):
                bar()
                coordinate_point = (
                    Point("coordinates")
                    .tag("id", device_id)
                    .field("latitude", pos.x)
                    .field("longitude", pos.y)
                    .field("sent_at", time.timestamp())
                )
                influx_connection.write(coordinate_point)

    def __str__(self):
        try:
            total_time = self.settings.start_time - self.end_time
            res = ""
            for i in range(len(self.positions) - 1):
                res += (
                    str(self.positions[i].x)
                    + "   "
                    + str(self.positions[i].y)
                    + "   "
                    + str(self.timestamps[i])
                    + "\n"
                )
            res += f" {self.settings.n_steps} steps Time interval {total_time} from {self.end_time} to {self.settings.start_time}\n"
        except Exception as e:
            res = "Error: " + str(e)
        return res

if __name__ == "__main__":
    #fake time series data bucket
    influx_connection.clean_bucket(100)
    #influx_connection.get_historical_data(hours_back=500, device_id="R010T1F2236B72F0", measurement_type="coordinates")