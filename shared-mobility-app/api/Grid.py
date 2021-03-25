from math import ceil, floor
import utils
from GridCell import GridCell

class Grid:
    """ Represents a grid of lat/long grid cells over a defined region
    """
    def __init__(self, min_lat, min_lng, max_lat, max_lng, distance, cdfs, ecdf):
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
                grid_cell = GridCell(grid_cell_corner, distance, cdfs.keys())
                self.cells[(j, i)] = grid_cell
                # move grid_cell_corner self.distance meters to right
                grid_cell_corner = utils.add_distance(self.distance, grid_cell_corner, "right")
            # move grid_cell_corner back to leftmost lng move up by self.distance meters
            grid_cell_corner = (grid_cell_corner[0], self.lower_left[1])
            grid_cell_corner = utils.add_distance(self.distance, grid_cell_corner, "up")

    def get_cells(self):
        return self.cells

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

    def find_neighbors(self, grid_coord):
        """ Based on inputted grid_coord find all the neighboring cells.
            The output would be a dictionary where the key is the distance
            and the value would be a list of coords that is at that distance from grid_coord
        """
        neighbors = {0: [grid_coord]}
        # go through other distances and calculate what neighbors would be
        # go through cdfs, extract the triangle dimensions, and process
        # process dimensions by adding all possible combinations and directions
        # and seeing if the grid_coord is valid



    def process_data(self, df_data, df_result):
        """ Takes in df_data of locations and events data and iterates through each row.
            Depending on the time_type, we update the proprties of the GridCell objects accordingly.
            Need to write data to df_result whenever a whole day passes
        """
        # iterate through df_data
        for index, row in df_data.iterrows():
            # find out which grid cell event took place in
            grid_coord = self.locate_point((row['lat'], row['lng']))
            # get coords of neighborhood cells

            # do differeent processing depending on whether
        return None
