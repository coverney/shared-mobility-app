import utils

class GridCell:
    """ Represents a lat/long grid cell
    """
    def __init__(self, lower_left, distance, dists):
        """ Create GridCell object from inputted lower_left corner and
            expected dimenions of the grid cell (assume square shape)
        """
        self.lower_left = lower_left
        self.lower_right = utils.add_distance(distance, self.lower_left, "right")
        self.upper_left = utils.add_distance(distance, self.lower_left, "up")
        self.upper_right = utils.add_distance(distance, self.lower_right, "up")
        self.center = utils.add_distance(distance/2, self.lower_left, "right-up")
        self.identifier = self.compute_id() # TODO: re-think format?
        # dictionary where key is distance and value is num scooters at that distance
        self.counts_by_distance = {key: 0 for key in dists} # gets reset on a new day
        # most recent time an event happened involving this grid cell
        self.current_time = ""
        # estimated number of trips originating from the cell (from trips data)
        self.demand_probs = 0 # gets reset on a new day
        # number of minutes a scooter is available in this grid cell for an interval
        # difference between end and start
        self.avail_mins = 0 # gets reset on a new interval
        # sum the following product over intervals:
        # prob a user arrives in interval (ecdf) *
        # prob a scooter is within user threshold (from half normal distribution)
        self.avail_cdf = 0 # gets reset on a new day

    def __str__(self):
        return "Grid cell object with center at " + self.center

    def compute_id(self):
        """ Compute GridCell id, which takes the first 5 decimals of lat (x)
            and the first 5 decimals of lng (y) and returns a string of the format
            "x.y"
        """
        # get decimal portions of center lat and long
        lat, lng = self.center
        # print(self.center)
        lat_dec = round(abs(lat) % 1, 5)
        lng_dec = round(abs(lng) % 1, 5)
        # combine the decimals
        return "{}.{}".format(int(lat_dec * 100000), int(lng_dec * 100000)) # string

    def get_id(self):
        return self.identifier

    def get_center(self):
        return self.center

    def get_upper_left(self):
        return self.upper_left

    def get_lower_right(self):
        return self.lower_right

    def get_lower_left(self):
        return self.lower_left

    def get_upper_right(self):
        return self.upper_right
