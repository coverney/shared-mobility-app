import utils
import iso8601
# import datetime
from datetime import timedelta

class GridCell:
    """ Represents a lat/long grid cell
    """
    def __init__(self, lower_left, distance, cdfs, ecdf, start_time):
        """ Create GridCell object from inputted lower_left corner and
            expected dimenions of the grid cell (assume square shape)
        """
        self.lower_left = lower_left
        self.lower_right = utils.add_distance(distance, self.lower_left, "right")
        self.upper_left = utils.add_distance(distance, self.lower_left, "up")
        self.upper_right = utils.add_distance(distance, self.lower_right, "up")
        self.center = utils.add_distance(distance/2, self.lower_left, "right-up")
        self.identifier = self.compute_id() # TODO: re-think format?
        # half normal distribution
        self.cdfs = cdfs
        # empirical distribution
        self.ecdf = ecdf
        # dictionary where key is distance and value is num scooters at that distance
        self.counts_by_distance = {key: 0 for key in cdfs.keys()} # gets reset on a new day
        # most recent time an event happened involving this grid cell
        self.current_time = start_time
        # number of trips that took place in cell
        self.num_trips = 0
        # estimated number of trips originating from the cell (from trips data)
        self.demand_probs = 0 # gets reset on a new day
        # number of minutes a scooter is available in this grid cell for the day
        # sum of differences between end and start (if count at 0 dist > 0)
        # basically it's the number of minutes >= 1 scooter is in this grid cell
        self.avail_mins = 0 # gets reset on a new day
        # used to get average number of scooters in the day
        # value is avail_mins * the number of scooters
        self.avail_count_mins = 0 # gets reset on a new day
        # sum the following product over intervals:
        # prob a user arrives in interval (ecdf) *
        # prob a scooter is within user threshold (from half normal distribution)
        self.prob_scooter_avail = 0 # gets reset on a new day

    def __str__(self):
        return "Grid cell object with center at " + str(self.center)

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

    def get_geo_data(self):
        upper_lat, left_lng = self.upper_left
        lower_lat, right_lng = self.lower_right
        return [round(upper_lat, 5), round(left_lng, 5), round(lower_lat, 5), round(right_lng, 5)]

    def get_data(self):
        """ Return dictionary of data for grid cell for one day
        """
        upper_lat, left_lng = self.upper_left
        lower_lat, right_lng = self.lower_right
        data = {'left_lng':round(left_lng, 5), 'right_lng':round(right_lng, 5),
                'lower_lat':round(lower_lat, 5), 'upper_lat':round(upper_lat, 5),
                'avail_count':self.avail_count_mins/(24*60), 'avail_mins':self.avail_mins,
                'prob_scooter_avail':self.prob_scooter_avail, 'trips':self.num_trips, 'adj_trips':self.demand_probs}
        # reset values
        self.num_trips = 0
        self.demand_probs = 0
        self.avail_mins = 0
        self.prob_scooter_avail = 0
        self.avail_count_mins = 0
        return data

    def get_count_at_dist(self, count, dist):
        return self.counts_by_distance[dist] 
    
    def set_all_counts_zero(self):
        for dist in self.counts_by_distance:
            self.counts_by_distance[dist] = 0
    
    def set_count_at_dist(self, count, dist):
        if dist == 0:
            self.counts_by_distance[dist] = count
        else:
            self.counts_by_distance[dist] += count

    def set_current_time(self, time):
        self.current_time = time

    def get_current_time(self):
        return self.current_time

    def add_to_demand_prob(self, prob):
        self.demand_probs += prob

    def increment_num_trips(self):
        self.num_trips += 1

    def get_minutes_from_string(self, time_stamp):
        """ Convert time part of a time stamp string into minutes
        """
        t = iso8601.parse_date(time_stamp)
        return (t.hour*60.0+t.minute+t.second/60.0)

    def values_not_zero(self):
        return any([self.avail_count_mins, self.avail_mins, self.prob_scooter_avail, self.num_trips, self.demand_probs])

    def get_min_dist(self):
        # get the distances in ascending order starting from dist
        dists = sorted(self.counts_by_distance.keys())
        for dist in dists:
            if self.counts_by_distance[dist] > 0:
                return dist
        return None

    def get_prob_user_accept(self, dist):
        if dist == 0:
            return 1
        if self.get_min_dist() is not None:
            if self.get_min_dist() < dist:
                return 0

        # get the distances in descending order starting from dist
        dists = [x for x in sorted(self.counts_by_distance.keys(), reverse=True) if x <= dist]
        prob = 1 - (self.cdfs[dists[1]][0])
        return prob
            #min_dist = dist
            #next_idx = 1
            #for index, d in enumerate(dists):
            #    if d < min_dist and self.counts_by_distance[d] > 0:
            #        min_dist = d
            #        next_idx = index+1
            #if next_idx >= len(dists):
            #    return 1
            #else:
            #    # get the distance threshold before min_dist
            #    return 1 - (self.cdfs[dists[next_idx]][0])

    def process_interval(self, type, next_time, dist):
        """ Type is either 'start_time' or 'end_time' or 'none'. If it's 'start_time', then
            we want to increase self.counts_by_distance[dist] by 1.
            If it's 'end_time', then we want to decrease by 1. We also want to
            update self.avail_mins and self.prob_scooter_avail before updating self.current_time.
            We should update counts and time last.
        """
        if iso8601.parse_date(next_time).date() != iso8601.parse_date(self.current_time).date():
            print(f"for type={type}, next_time={next_time} and current_time={self.current_time} not on same day")
        # update self.avail_mins
        interval_length = ((iso8601.parse_date(next_time) - iso8601.parse_date(self.current_time)).total_seconds() / 60.0)
        if interval_length < 0:
            print(f"negative interval length for next_time={next_time} and current_time={self.current_time}")
        if self.counts_by_distance[0] > 0:
            self.avail_mins += interval_length
            self.avail_count_mins += interval_length*self.counts_by_distance[0]
        # update self.prob_scooter_avail
        # check if count > 0 and interval length > 0.1 minute
        if (self.get_min_dist() is not None) and (interval_length > 0.1):
            prob_user_accept = self.get_prob_user_accept(self.get_min_dist())
            cdf_diff = self.ecdf(self.get_minutes_from_string(next_time)) - self.ecdf(self.get_minutes_from_string(self.current_time))
            # all the probs should be positive
            if prob_user_accept < 0:
                print(f"prob user accept scooter is negative: {prob_user_accept}")
            if cdf_diff < 0:
                print(f"cdf for interval is negative: {cdf_diff} from {self.current_time} to {next_time}")
            self.prob_scooter_avail += prob_user_accept * cdf_diff
            # prob user accept: take cdf of one before the min distance and subtract from 1 (reference Alice's drawing)
        # update count
        if type == 'start_time':
            self.counts_by_distance[dist] += 1
        elif type == 'end_time':
            self.counts_by_distance[dist] -= 1
        # update time
        if type != 'none':
            self.current_time = next_time

    def get_trip_prob(self, dist):
        """ Get the probability a user would choose a scooter at dist away from
            this grid cell. This can be found by finding self.cdfs[dist][0]
            (prob scooter within user threshold) and dividing it by the number of
            avail scooters, self.counts_by_distance[dist].
            Return 0 if there is a closer scooter (greedy perspective)
        """
        # return 0 is there is a closer scooter available
        if (self.get_min_dist() is not None) and (self.get_min_dist() < dist):
            # print("Closer scooter available")
            return 0
        if self.counts_by_distance[dist] < 1:
            # print(f"Grid cell with id={self.identifier} has no scooters available at dist={dist} when trip occurred")
            return 0
        return self.get_prob_user_accept(dist)/self.counts_by_distance[dist]
