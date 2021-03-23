import pandas as pd
import time
import utils
import createHalfNormal
from Grid import Grid

class DataProcessor:

    MAX_DISTANCE = 1000
    START = "2018-11-01T06:00:00-04:00"
    END = "2019-10-31T22:00:00-04:00"

    def __init__(self, df_events=None, df_locations=None, distance=400, p0=0.7):
        """ Constructor for DataProcessor class with the inputs being the events
            and location data files. Also take in distance and p0 for spatial modeling
        """
        self.df_events = df_events
        self.df_locations = df_locations
        self.distance = distance
        self.p0 = p0
        self.df_demand = None

    def get_demand(self):
        """ Return the demand dataframe after it has been generated
        """
        return self.df_demand

    def set_events(self, df_events):
        self.df_events = df_events

    def set_locations(self, df_locations):
        self.df_locations = df_locations

    def set_demand(self, df_demand):
        self.df_demand = df_demand

    def compute_grid_cells(self, df):
        """ Take in a dataframe and calculate lat/lng grid cells of a certain distance.
            The output is Grid object
        """
        # create half normal distribution
        cdfs = createHalfNormal.create_distribution(self.p0, self.distance, self.MAX_DISTANCE)
        # find corners of entire lat/ lng region and compute grid cells
        min_lat = min(df['lat'].values)
        min_lng = min(df['lng'].values)
        max_lat = max(df['lat'].values)
        max_lng = max(df['lng'].values)
        grid = Grid(min_lat, min_lng, max_lat, max_lng, self.distance, cdfs)
        return grid

    def combine_events_and_locations(self):
        """ Clean up locations and events data and then concat the two dfs
            and sort the time column
        """
        # clean locations data
        df_locations_cleaned = utils.clean_locations_data(self.df_locations, self.START, self.END)
        # clean events data
        df_events_cleaned = utils.clean_events_data(self.df_events, self.START, self.END)
        # combine and sort
        df_both = pd.concat([df_locations_cleaned, df_events_cleaned])
        # also sort time_type since want trips to be first when time is tied
        return df_both.sort_values(by=['time', 'time_type'], ascending=[True, False])

    def process_data(self):
        """ Computes availability and pickup info and estimates demand.
            Also employs spatial modeling
        """
        timer_start = time.time()
        # create Grid object before processing any data
        grid = self.compute_grid_cells(self.df_locations)
        # clean and combine events and locations data
        df_data = self.combine_events_and_locations()
        # process data within grid class
        df_processed = grid.process_data(df_data)
        timer_end = time.time()
        print('Elapsed time to process data:', (timer_end - timer_start)/60.0, 'minutes')

if __name__ == '__main__':
    eventsFile = '../../../data_files/events.csv'
    locationsFile = '../../../data_files/locations_for_multiple_providers_from_18-11-01_to_19-11-01.csv'
    df_events = pd.read_csv(eventsFile)
    df_locations = pd.read_csv(locationsFile)
    processor = DataProcessor(df_events, df_locations)
    processor.process_data()
