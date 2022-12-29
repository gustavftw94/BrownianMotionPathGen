from dataclasses import dataclass
from shapely import geometry
from datetime import datetime, timedelta
from typing import List
import csv

@dataclass
class Settings:
    boundary: geometry.Polygon
    timestep: timedelta
    n_steps: int
    migration_factor = 0.005
    start_time: datetime = datetime.now()

class Result:
    def __init__(self, settings: Settings):
        self.positions: List[geometry.Point] = []
        self.timestamps: List[datetime] = []
        self.settings = settings
        self._timedelta = self.settings.timestep
        self.end_time = self.settings.start_time - (self.settings.n_steps * self._timedelta)

    def to_csv(self, filename:str):
        ## save positions and timestamps to csv file
        result_dict = {"x": [p.x for p in self.positions],
                        "y": [p.y for p in self.positions],
                        "timestamp": self.timestamps}
        _range = range(len(self.positions)-1)

        cols = []
        for i in _range:
            row = [result_dict["x"][i], result_dict["y"][i], result_dict["timestamp"][i]]
            cols.append(row)

        with open(filename, 'w') as f:
            w = csv.writer(f)
            w.writerow(result_dict.keys())
            w.writerows(cols)

    def __str__(self):
        try:
            total_time = self.settings.start_time - self.end_time
            res = ""
            for i in range(len(self.positions)-1):
                res += str(self.positions[i].x) +"   "+ str(self.positions[i].y) +"   "+ str(self.timestamps[i]) + "\n"
            res += f" {self.settings.n_steps} steps Time interval {total_time} from {self.end_time} to {self.settings.start_time}"
        except Exception as e:
            res = "Error: " + str(e)
        return res


