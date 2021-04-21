import pandas as pd
import time
import numpy as np
import iso8601
import datetime
from statsmodels.distributions.empirical_distribution import ECDF
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import utils
import createHalfNormal
from Grid import Grid # commented for testing

class DataProcessor:

    MAX_DISTANCE = 1000

    def __init__(self, df_events=None, df_locations=None, distance=400, p0=0.7):
        """ Constructor for DataProcessor class with the inputs being the events
            and location data files. Also take in distance and p0 for spatial modeling
        """
        self.df_events = df_events
        self.df_locations = df_locations
        self.distance = distance
        self.p0 = p0
        self.df_demand = None
        # set start and end in self.process_data()
        self.start = None
        self.end = None

    def get_demand(self):
        """ Return the demand dataframe after it has been generated
        """
        return self.df_demand

    def set_events(self, df_events):
        self.df_events = df_events

    def set_locations(self, df_locations):
        self.df_locations = df_locations

    def set_p0(self, p0):
        self.p0 = p0

    def set_distance(self, distance):
        self.distance = distance

    def set_demand(self, df_demand):
        self.df_demand = df_demand

    def is_valid_df_demand(self, df_demand):
        """ Check to make sure df_demand is valid in terms of its columns
        """
        cols = ["date", "left_lng", "right_lng", "lower_lat", "upper_lat",
                "avail_count", "avail_mins", "prob_scooter_avail", "trips", "adj_trips"]
        for col in cols:
            if col not in df_demand.columns:
                return False
        return True

    def get_relevant_demand_cols(self):
        """ Returns the subset of self.df_demand that we want to save to a CSV
            file if the user clicks on the download data button
        """
        # select for cols we want
        df = self.df_demand[["date", "left_lng", "right_lng", "lower_lat",
                                "upper_lat", "avail_count", "avail_mins",
                                "prob_scooter_avail", "trips", "adj_trips"]]
        return df

    def map_values_to_color(self, df, col_name):
        """ Takes in a column name (x) in self.demand and returns a DataFrame with
            a new column called x_color that mapped the values of x to a hex code
            that will be visualized on the grid squares
        """
        # map values to colors in hex via
        # creating a hex Look up table table and apply the normalized data to it
        norm = mcolors.Normalize(vmin=np.nanmin(df[col_name].values),
                                    vmax=np.nanmax(df[col_name].values), clip=True)
        # alternative way of generating hex values
        # mapper = plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.viridis)
        # a = mapper.to_rgba(df[col_name])
        # color_col_name = col_name + '_color'
        # df[color_col_name] =  np.apply_along_axis(mcolors.to_hex, 1, a)

        lut = plt.cm.viridis(np.linspace(0,1,256))
        lut = np.apply_along_axis(mcolors.to_hex, 1, lut)
        a = (norm(df[col_name].values)*255).astype(np.int16)
        color_col_name = col_name + '_color'
        df[color_col_name] = lut[a]
        return df

    def create_log_column(self, df, name):
        """ Create log of df['name']
        """
        # print(f"mean of name {name} is {df[name].mean()}")
        df['log_'+name] = np.log10(df[name].replace(0, df[name].mean()))
        df = self.map_values_to_color(df, 'log_'+name)
        return df

    def create_rectangle_lst(self, df, factors):
        """ Create list of dictionaries with each dict containing information
            needed to create the React Leaflet rectangles (name, bounds, color).
            The factors variable provides the data that we want to include in the
            tooltip besides the center lat/lng. Each elment in the factors list
            will be a tuple where the first value is the column name, and the second
            is the column type (e.g. 'decimal' or 'percent' or 'itself')
        """
        rects = []
        for index, row in df.iterrows():
            rect_dict = {}
            # get the upper left and bottom right coordinates
            upper_left = [row['upper_lat'], row['left_lng']]
            bottom_right = [row['lower_lat'], row['right_lng']]
            rect_dict['bounds'] = [upper_left, bottom_right]
            rect_dict['name'] = "Rectangle " + str(index)
            # get center lat/lng for tooltip
            center_lat, center_lng = utils.add_distance(self.distance/2, (row['lower_lat'], row['left_lng']), "right-up")
            rect_dict['lat'] = round(center_lat, 5)
            rect_dict['lng'] = round(center_lng, 5)
            # add in the factors, rounding the decimals to 2 digits after point
            # also writing percents with proper formatting
            for factor in factors:
                name, type = factor
                if type == 'itself':
                    rect_dict[name] = row[name]
                elif type == 'decimal':
                    rect_dict[name] = round(row[name], 2)
                else: # type == 'percent'
                    rect_dict[name] = str(int(row[name]*100))+"%"
                # add in the color info
                rect_dict[name+'_color'] = row[name+'_color']
            rects.append(rect_dict)
        return rects

    def build_shape_data(self, start=None, end=None):
        """ Build shape data from rounded lat/lng regions within start and end.
            Also take the average of the cols for each region and create
            corresponding hex color columns
        """
        # If start and end are None, then set them to be min/max of self.df_demand
        if start is None:
            start = self.df_demand['date'].min()
        if end is None:
            end = self.df_demand['date'].max()
        print(f"date range for shape data is from {start} to {end}")
        # Extract part of df_demand that is within start and end
        df_sub = self.df_demand[(self.df_demand['date'] >= start) & (self.df_demand['date'] <= end)]
        assert df_sub['date'].min() >= start
        assert df_sub['date'].max() <= end
        # Group demand data by lat/lng region and average across other cols
        df = df_sub.groupby(['left_lng', 'right_lng', 'lower_lat', 'upper_lat'])[['avail_count', 'avail_mins', 'prob_scooter_avail', 'trips', 'adj_trips']].mean().reset_index()
        # print(df.head())
        # For each var col, create corresponding color columns (log and unlog)
        # Also create the factors list that get passed into self.create_rectangle_lst
        factors = [('avail_count', 'decimal'), ('avail_mins', 'decimal'),
                        ('prob_scooter_avail', 'percent'), ('trips', 'itself'), ('adj_trips', 'decimal')]
        i = 0
        original_len = len(factors)
        while i < original_len:
            name, type = factors[i]
            # print(f"name={name}, type={type}")
            # Create color column
            df = self.map_values_to_color(df, name)
            # If type is not percent than create log version
            if type != 'percent':
                df = self.create_log_column(df, name)
                factors.append(('log_'+name, type))
            i += 1
        # Create Rectangle information
        rectangles = self.create_rectangle_lst(df, factors)
        return rectangles

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
        grid = Grid(min_lat, min_lng, max_lat, max_lng, self.distance, cdfs, ecdf, self.start)
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
        df = df[(df['event_type_reason'] == "user_pick_up") & (df['event_time'] >= iso8601.parse_date(self.start)) & (df['event_time'] <= iso8601.parse_date(self.end))]
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
        df_locations_cleaned = utils.clean_locations_data(self.df_locations, self.start, self.end)
        # clean events data
        df_events_cleaned = utils.clean_events_data(self.df_events, self.start, self.end)
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
        # ensure self.df_events and self.df_locations are not None
        if self.df_events is None or self.df_locations is None:
            print("Missing data: either df_events or df_locations is None")
            return
        # set start and end based on self.df_events
        self.start = self.df_events['event_time'].min()
        self.end = self.df_events['event_time'].max()
        print(f"date range for events data is from {self.start} to {self.end}")
        # create Grid object before processing any data
        grid = self.compute_grid_cells(self.df_locations)
        # clean and combine events and locations data
        df_data = self.combine_events_and_locations(grid)
        print(df_data.shape)
        # df_data.to_csv('../../../data_files/20210421_cleanedInputDataCumSum.csv', index=False)
        # df_data = pd.read_csv('../../../data_files/20210415_cleanedInputDataAprilCumSum.csv')
        # process data within grid class
        df_processed = grid.process_data(df_data, 'weekly')
        # df_processed = self.calculate_demand(df_processed)
        # df_processed.to_csv('../../../data_files/20210421_demandLatLng.csv')
        # set df_demand to be df_processed
        df_processed.reset_index(inplace=True)
        df_processed = df_processed.astype({'date': 'str', 'avail_count': 'float', 'avail_mins': 'float', 'prob_scooter_avail': 'float', 'trips': 'float', 'adj_trips': 'float'})
        self.set_demand(df_processed)
        timer_end = time.time()
        print('Elapsed time to process data:', (timer_end - timer_start)/60.0, 'minutes')

if __name__ == '__main__':
    eventsFile = '../../../data_files/events.csv'
    locationsFile = '../../../data_files/locations_for_multiple_providers_from_18-11-01_to_19-11-01.csv'
    df_events = pd.read_csv(eventsFile)
    df_locations = pd.read_csv(locationsFile)
    processor = DataProcessor(df_events, df_locations, 500, 0.7)
    processor.process_data()
