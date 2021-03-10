from math import ceil, floor
import utils
from GridCell import GridCell

class Grid:
    """ Represents a grid of lat/long grid cells over a defined region
    """
    def __init__(self, min_lat, min_lng, max_lat, max_lng, distance):
        # take lower left corner of entire lat/lng region and add buffer space
        self.distance = distance
        self.lower_left = utils.add_distance(50, (min_lat, min_lng), "left-down")
        # approximate dimensions of lat/lng region based on distance
        lower_right = utils.add_distance(50, (min_lat, max_lng), "right-down") # add buffer
        upper_left = utils.add_distance(50, (max_lat, min_lng), "left-up") # add buffer
        dist_lng = utils.haversine(self.lower_left, lower_right)*1000 # in meters
        self.num_lng = ceil(dist_lng/self.distance)
        dist_lat = utils.haversine(upper_left, self.lower_left)*1000 # in meters
        self.num_lat = ceil(dist_lat/self.distance)
        print("num lat:", self.num_lat, "num lng:", self.num_lng)
        # for testing
        # self.num_lat = 2
        # self.num_lng = 1
        # create grid cells
        grid_cell_corner = self.lower_left
        self.cells = {}
        for i in range(self.num_lat):
            for j in range(self.num_lng):
                grid_cell = GridCell(grid_cell_corner, 400)
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
