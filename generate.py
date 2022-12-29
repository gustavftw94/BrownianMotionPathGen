from settings import Settings, Result
from numpy.random import normal
from shapely import geometry
from datetime import timedelta
from matplotlib import pyplot as plt
import numpy as np


class Brownian(object):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.result = Result(settings)
        self.current_time = self.settings.start_time

    def find_random_point_in_polygon(self):
        minx, miny, maxx, maxy = self.settings.boundary.bounds
        x = np.random.uniform(minx, maxx)
        y = np.random.uniform(miny, maxy)
        start_pos = geometry.Point(x, y)
        return start_pos

    def make_start_pos(self):
        start_pos = self.find_random_point_in_polygon()
        while not self.settings.boundary.contains(start_pos):
            start_pos = self.find_random_point_in_polygon()
        self.result.positions.append(start_pos)
        self.result.timestamps.append(self.settings.start_time)

    def determine_suitable_normal_params(self):
        poly = self.settings.boundary
        box = poly.minimum_rotated_rectangle
        x, y = box.exterior.coords.xy
        edge_length = (
            geometry.Point(x[0], y[0]).distance(geometry.Point(x[1], y[1])),
            geometry.Point(x[1], y[1]).distance(geometry.Point(x[2], y[2])),
        )
        length = max(edge_length)
        width = min(edge_length)
        self.length_modifier = max(length, width) * 0.01

    def line_intersects(self, old_pos, new_pos):
        line = geometry.LineString([old_pos, new_pos])
        boundary_exterior = self.settings.boundary.exterior
        does_intersect_with_boundary = not boundary_exterior.intersection(line).is_empty
        return does_intersect_with_boundary

    def generate_new_pos(self, old_pos: geometry.Point):
        change_grazing_zone = np.random.randint(0, 10000) / 10000
        if change_grazing_zone < self.settings.migration_factor:
            new_pos = self.find_random_point_in_polygon()
            while (not self.settings.boundary.contains(new_pos)) or (
                self.line_intersects(old_pos, new_pos)
            ):
                new_pos = self.find_random_point_in_polygon()

        else:
            delta_x = normal(0, 1) * self.length_modifier
            delta_y = normal(0, 1) * self.length_modifier
            x = old_pos.x + delta_x
            y = old_pos.y + delta_y

            new_pos = geometry.Point(x, y)
            if not self.settings.boundary.contains(new_pos):
                x = old_pos.x - delta_x
                y = old_pos.y - delta_y
                new_pos = geometry.Point(x, y)
                if not self.settings.boundary.contains(new_pos):
                    x = old_pos.x + delta_x
                    y = old_pos.y - delta_y
                    new_pos = geometry.Point(x, y)
                if not self.settings.boundary.contains(new_pos):
                    x = old_pos.x - delta_x
                    y = old_pos.y + delta_y
                    new_pos = geometry.Point(x, y)
                if not self.settings.boundary.contains(new_pos):
                    return False
        self.result.positions.append(new_pos)
        self.step_in_time()
        return True

    def step_in_time(self):
        self.current_time += self.settings.timestep
        self.result.timestamps.append(self.current_time)

    def run(self):
        self.make_start_pos()
        self.determine_suitable_normal_params()

        for i in range(self.settings.n_steps):
            found = False
            while not found:
                found = self.generate_new_pos(self.result.positions[-1])

    def display_results(self):
        print(self.result)

    def plot_result_path(self):
        x = [p.x for p in self.result.positions]
        y = [p.y for p in self.result.positions]
        plt.plot(x, y)
        x, y = self.settings.boundary.exterior.xy
        plt.plot(x, y)
        plt.show()

    def __str__(self):
        res = ""
        res += f"start_pos: {self.result.positions[0]}\n"
        return res


if __name__ == "__main__":
    polygon = [
        [17.995366850522515, 59.33057931698136],
        [17.995928949604263, 59.335739843849126],
        [18.006868244097205, 59.341264196549076],
        [18.02709688175287, 59.3386224723839],
        [18.046658391763145, 59.33444978561704],
        [18.056776175241623, 59.327353589628416],
        [18.04159950002463, 59.325848145401864],
        [18.029514369759312, 59.3282854978724],
        [18.025720200955107, 59.32613490182459],
        [18.029233320219163, 59.323123838704674],
        [18.03597850920434, 59.322908752559414],
        [18.039210578925463, 59.3214748101403],
        [18.03864847984366, 59.32061441565148],
        [18.028671221136022, 59.31910867289071],
        [18.02445547802074, 59.31989740360763],
        [18.016586090872067, 59.31982570157129],
        [18.014337694543713, 59.32061441565148],
        [18.016305041330554, 59.32154650869816],
        [18.01700766518306, 59.32204839436724],
        [18.01925606151144, 59.322621968915],
        [18.024174428479228, 59.32176160346384],
        [18.024596002791583, 59.32276536103984],
        [18.028390171595845, 59.32348231258868],
        [18.025017577102545, 59.325919834734236],
        [18.024174428479228, 59.32455771155588],
        [18.0223476064632, 59.32462940361063],
        [18.020942358758106, 59.32505955276281],
        [18.011386674361404, 59.325202934603595],
        [17.995366850522515, 59.33057931698136],
    ]

    settings = Settings(
        boundary=geometry.Polygon(polygon),
        timestep=timedelta(hours = 1),
        n_steps=500,
    )
    for i in range(10):
        b = Brownian(settings=settings)
        b.run()
        b.display_results()
        b.result.to_csv(f"faketimeseriesdata{i}.csv")
        #b.plot_result_path()
