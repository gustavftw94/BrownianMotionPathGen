import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS







query_api = client.query_api()

query = """from(bucket: "ontrack-fake-sensor-data")
# |> range(start: -10m)"""
tables = query_api.query(query, org="VestiTech Data")

for table in tables:
  for record in table.records:
    print(record)