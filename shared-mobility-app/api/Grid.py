from math import ceil, floor
import utils
from GridCell import GridCell
import iso8601
import pandas as pd
import createHalfNormal # for testing
from DataProcessor import DataProcessor # for testing


class Grid:
    """ Represents a grid of lat/long grid cells over a defined region
    """
    def __init__(self, min_lat, min_lng, max_lat, max_lng, distance, cdfs, ecdf, start_time):
        self.distance = distance
        self.cdfs = cdfs # from discretized half normal
        self.ecdf = ecdf # from event data
        # take lower left corner of entire lat/lng region and add buffer space
        self.lower_left = utils.add_distance(50, (min_lat, min_lng), "left-down")
        # approximate dimensions of lat/lng region based on distance
        lower_right = utils.add_distance(50, (min_lat, max_lng), "right-down") # add buffer
        upper_left = utils.add_distance(50, (max_lat, min_lng), "left-up") # add buffer
        dist_lng = utils.haversine(self.lower_left, lower_right)*1000 # in meters
        self.num_lng = ceil(dist_lng/self.distance)
        dist_lat = utils.haversine(upper_left, self.lower_left)*1000 # in meters
        self.num_lat = ceil(dist_lat/self.distance)
        print("num lat:", self.num_lat, "num lng:", self.num_lng)
        # create grid cells
        grid_cell_corner = self.lower_left
        self.cells = {}
        for i in range(self.num_lat):
            for j in range(self.num_lng):
                grid_cell = GridCell(grid_cell_corner, distance, cdfs, ecdf, start_time)
                self.cells[(j, i)] = grid_cell
                # move grid_cell_corner self.distance meters to right
                grid_cell_corner = utils.add_distance(self.distance, grid_cell_corner, "right")
            # move grid_cell_corner back to leftmost lng move up by self.distance meters
            grid_cell_corner = (grid_cell_corner[0], self.lower_left[1])
            grid_cell_corner = utils.add_distance(self.distance, grid_cell_corner, "up")

    def get_cells(self):
        return self.cells

    def get_date_from_string(self, time_stamp):
        """ Return the date part of a time stamp string
        """
        t = iso8601.parse_date(time_stamp)
        return str(t.date())

    def locate_point(self, coord):
        """ Determine the coordinate of the GridCell that an inputted lat/lng
            coord belongs in.
            Return None if coord lies outside of all the GridCells
        """
        lowest_lat = self.lower_left[0]
        leftmost_lng = self.lower_left[1]
        dist_lat =  utils.haversine((coord[0], leftmost_lng), self.lower_left)*1000 # in meters
        dist_lng =  utils.haversine((lowest_lat, coord[1]), self.lower_left)*1000 # in meters
        grid_coord = (floor(dist_lng/self.distance), floor(dist_lat/self.distance))
        if grid_coord in self.cells:
            return grid_coord
        return None

    def calculate_grid_coords(self, grid_coord, dimension):
        """ Given grid_coord and dimension, return list of unique valid neighbord grid coords
        """
        # add reverse dimension if applicable
        dimensions = list(set([dimension, dimension[::-1]]))
        # for each dimension, add coords in all four directions (up, down, left, right)
        coords = set()
        for dim in dimensions:
            coords.add(tuple([x+y for x,y in zip(grid_coord,(1*dim[0], -1*dim[1]))])) # up-left
            coords.add(tuple([x+y for x,y in zip(grid_coord,(1*dim[0], 1*dim[1]))])) # up-right
            coords.add(tuple([x+y for x,y in zip(grid_coord,(-1*dim[0], -1*dim[1]))])) # down-left
            coords.add(tuple([x+y for x,y in zip(grid_coord,(-1*dim[0], 1*dim[1]))])) # down-right
        # make sure coords has valid values
        return [x for x in coords if x in self.cells]

    def find_neighbors(self, grid_coord):
        """ Based on inputted grid_coord find all the neighboring cells.
            The output would be a dictionary where the key is the distance
            and the value would be a list of coords that is at that distance from grid_coord
        """
        neighbors_dict = {}
        # go through other distances and calculate what neighbors would be
        # go through cdfs, extract the triangle dimensions, and process
        # process dimensions by adding all possible combinations and directions
        # and seeing if the grid_coord is valid
        for dist in self.cdfs:
            dimension = self.cdfs[dist][1] # tuple
            neighbors = self.calculate_grid_coords(grid_coord, dimension)
            neighbors_dict[dist] = neighbors
        return neighbors_dict

    def process_data(self, df_data, df_result):
        """ Takes in df_data of locations and events data and iterates through each row.
            Depending on the time_type, we update the proprties of the GridCell objects accordingly.
            Need to write data to df_result whenever a whole day passes
        """
        current_date = self.get_date_from_string(min(df_data['time']))
        # iterate through df_data
        for index, row in df_data.iterrows():
            # if new day, then fill in df_result for previous date
            if current_date != self.get_date_from_string(row['time']):
                print(f"at least one day passed from {current_date}")
                for coord in self.cells:
                    # get dictionary of values from grid cell
                    cell_data = self.cells[coord].get_data()
                    df_result.loc[pd.IndexSlice[(current_date, str(coord))]] = pd.Series(cell_data)
                current_date = self.get_date_from_string(row['time'])
            # find out which grid cell event took place in
            grid_coord = self.locate_point((row['lat'], row['lng']))
            # get coords of neighborhood cells
            neighbors = self.find_neighbors(grid_coord)
            # do different processing depending on time_type
            time_type = row['time_type']
            time = row['time']
            if time_type == 'trip':
                self.cells[grid_coord].increment_num_trips()
                # a trip occurred at grid_coord, we need to estimate where the
                # demand originated from. For each neighbor, get the probability
                # a user would choose a scooter where the trip happened. Prob
                # would be 0 if there is a closer scooter (greedy perspective)
                probs = {}
                prob_sum = 0
                for dist in neighbors:
                    for coord in neighbors[dist]:
                        prob = self.cells[coord].get_trip_prob(dist)
                        prob_sum += prob
                        probs[coord] = prob
                # normalize probs
                if prob_sum > 0:
                    norm_probs = {k: v / prob_sum for k, v in probs.items()}
                    assert int(round(sum(norm_probs.values(), 0.0))) == 1
                else:
                    norm_probs = probs
                # updates self.demand_probs for each grid cell
                for coord in norm_probs:
                    self.cells[coord].add_to_demand_prob(norm_probs[coord])
            else: # if time_type is "start_time" or "end_time", then availability changed
                for dist in neighbors:
                    for coord in neighbors[dist]:
                        self.cells[coord].process_interval(time_type, time, dist)
        return df_result

if __name__ == '__main__':
    # create half normal distribution
    cdfs = createHalfNormal.create_distribution(0.7, 400, 1000)
    # create ecdf from df_events
    processor = DataProcessor()
    processor.set_events(pd.read_csv('../../../data_files/events.csv'))
    ecdf = processor.calculate_cdf()
    assert (ecdf(24*60)-ecdf(1*60)) == 1
    # find corners of entire lat/ lng region and compute grid cells
    min_lat = 41.82
    min_lng = -71.44
    max_lat = 41.83
    max_lng = -71.43
    START = "2018-11-01T06:00:00-04:00"
    grid = Grid(min_lat, min_lng, max_lat, max_lng, 400, cdfs, ecdf, START)
    # process data
    df_empty = processor.create_empty_df_result(grid)
    # df_empty.to_csv('../../../data_files/20210330_emptyResult.csv')
    df_data = pd.read_csv('../../../data_files/20210330_cleanedInputDataSubset.csv')
    df_result = grid.process_data(df_data, df_empty)
    df_result.to_csv('../../../data_files/20210330_demandLatLng.csv')
