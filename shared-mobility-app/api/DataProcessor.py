import pandas as pd
import time
import numpy as np
import iso8601
import datetime
from statsmodels.distributions.empirical_distribution import ECDF
import utils
import createHalfNormal
from Grid import Grid # commented for testing

class DataProcessor:

    MAX_DISTANCE = 1000
    START = "2018-11-01T06:00:00-04:00"
    END = "2019-10-31T22:00:00-04:00"
    # START = "2018-11-01T06:00:00-04:00"
    # END = "2018-11-30T22:00:00-04:00"
    # START = "2019-04-01T06:00:00-04:00"
    # END = "2019-04-22T22:00:00-04:00"

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
        # create ecdf from df_events
        ecdf = self.calculate_cdf()
        assert (ecdf(24*60)-ecdf(1*60)) == 1
        # find corners of entire lat/ lng region and compute grid cells
        min_lat = min(df['lat'].values)
        min_lng = min(df['lng'].values)
        max_lat = max(df['lat'].values)
        max_lng = max(df['lng'].values)
        grid = Grid(min_lat, min_lng, max_lat, max_lng, self.distance, cdfs, ecdf, self.START)
        return grid

    def get_date(self, datetime):
        """ Return the date part of a datetime object
        """
        return datetime.date()

    def get_minutes(self, datetime):
        """ Convert time part of a datetime object into minutes
        """
        return datetime.hour*60.0+datetime.minute+datetime.second/60

    def parse_time_stamp(self, time_stamp):
        """ Convert time stamp to datetime
        """
        # return iso8601.parse_date(time_stamp).replace(tzinfo=datetime.timezone.utc)
        return iso8601.parse_date(time_stamp)

    def get_cdf_data(self):
        """ Get cdf data from df_events
        """
        df = self.df_events.copy()
        df['event_time'] = df['event_time'].apply(self.parse_time_stamp) # convert strings to datetime objects
        # only get the rows with event_type_reason == "user_pick_up" and event_time between 6 am and 10 pm
        # also make sure dates are between the start and end period
        df = df[(df['event_type_reason'] == "user_pick_up") & (df['event_time'] >= iso8601.parse_date(self.START)) & (df['event_time'] <= iso8601.parse_date(self.END))]
        df['date'] = df['event_time'].apply(self.get_date).astype(str) # get date part of datetime object
        df['minute'] = df['event_time'].apply(self.get_minutes).astype(float)
        # consider only trips that began with operating hours
        df = df[(df['minute'] >= (6*60)) & (df['minute'] < (22*60))]
        return df[['date', 'minute']].reset_index(drop=True)

    def calculate_cdf(self):
        """ Calculate CDF of pickup times
        """
        df_cdf = self.get_cdf_data()
        return ECDF(df_cdf['minute'])

    def combine_events_and_locations(self, grid):
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
        df_both = df_both.sort_values(by=['time', 'time_type'], ascending=[True, False])
        # include grid data
        df_both['grid_coord'] = df_both.apply(lambda x: grid.locate_point((x.lat, x.lng)), axis=1)
        df_both['grid_id'] = df_both.apply(lambda x: grid.get_cells()[x['grid_coord']].get_id(), axis=1)
        return self.find_cum_sum(df_both)

    def find_cum_sum(self, df):
        df.loc[(df['time_type'] == 'trip'), 'value'] = 0
        df.loc[(df['time_type'] == 'start_time'), 'value'] = 1
        df.loc[(df['time_type'] == 'end_time'), 'value'] = -1
        df['cum_value'] = df.groupby('grid_coord')['value'].cumsum()
        return df

    # def calculate_demand(self, df):
    #     df['estimated_demand'] = df['adj_trips'].divide(df['prob_scooter_avail'].where(df['prob_scooter_avail'] != 0, np.nan))
    #     return df

    def process_data(self):
        """ Computes availability and pickup info and estimates demand.
            Also employs spatial modeling
        """
        timer_start = time.time()
        # create Grid object before processing any data
        grid = self.compute_grid_cells(self.df_locations)
        # clean and combine events and locations data
        df_data = self.combine_events_and_locations(grid)
        print(df_data.shape)
        df_data.to_csv('../../../data_files/20210415_cleanedInputDataCumSum.csv', index=False)
        # df_data = pd.read_csv('../../../data_files/20210415_cleanedInputDataAprilCumSum.csv')
        # process data within grid class
        df_processed = grid.process_data(df_data, 'weekly')
        # df_processed = self.calculate_demand(df_processed)
        df_processed.to_csv('../../../data_files/20210415_demandLatLng.csv')
        timer_end = time.time()
        print('Elapsed time to process data:', (timer_end - timer_start)/60.0, 'minutes')

if __name__ == '__main__':
    eventsFile = '../../../data_files/events.csv'
    locationsFile = '../../../data_files/locations_for_multiple_providers_from_18-11-01_to_19-11-01.csv'
    df_events = pd.read_csv(eventsFile)
    df_locations = pd.read_csv(locationsFile)
    processor = DataProcessor(df_events, df_locations, 500, 0.7)
    processor.process_data()
