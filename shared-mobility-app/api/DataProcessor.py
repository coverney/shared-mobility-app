import pandas as pd
import computePickupsData
import countIntervals
import estimateDemand
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

class DataProcessor:

    # TODO: would need to incorporate in __init__ or take from data
    START = "2018-11-01T06:00:00-04:00"
    END = "2019-10-31T22:00:00-04:00"

    def __init__(self, df_events=None, df_locations=None):
        """ Constructor for DataProcessor class with the inputs being the events
            and location data files
        """
        self.df_events = df_events
        self.df_locations = df_locations
        self.df_demand = None
        # self.df_demand = pd.read_csv('../../../data_files/20210223_demandLatLng.csv')

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

    def is_valid_df_demand(self, df_demand):
        """ Check to make sure df_demand is valid in terms of its columns
        """
        cols = ["date", "upper_lat", "lower_lat",
                "left_long", "right_long", "avail_perc",
                "count_time", "cdf_sum", "trips", "adj_trips"]
        for col in cols:
            if col not in df_demand.columns:
                return False
        return True

    def get_relevant_demand_cols(self):
        """ Returns the subset of self.df_demand that we want to save to a CSV
            file if the user clicks on the download data button

            This function may no longer be necessary!
        """
        # select for cols we want
        df = self.df_demand[["date", "upper_lat", "lower_lat",
                                "left_long", "right_long", "avail_perc",
                                "count_time", "cdf_sum", "trips", "adj_trips"]]
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

    def create_rectangle_lst(self, df):
        """ Create list of dictionaries with each dict containing information
            needed to create the React Leaflet rectangles (name, bounds, color)
        """
        rects = []
        for index, row in df.iterrows():
            rect_dict = {}
            # get the upper left and bottom right coordinates
            upper_left = [row['upper_lat'], row['left_long']]
            bottom_right = [row['lower_lat'], row['right_long']]
            rect_dict['bounds'] = [upper_left, bottom_right]
            rect_dict['name'] = "Rectangle " + str(index)

            rect_dict['trips_color'] = row['trips_color']
            rect_dict['trips'] = round(row['trips'], 2)
            rect_dict['adj_trips_color'] = row['adj_trips_color']
            rect_dict['adj_trips'] = round(row['adj_trips'], 2)

            rect_dict['log_trips_color'] = row['log_trips_color']
            rect_dict['log_trips'] = round(row['log_trips'], 2)
            rect_dict['log_adj_trips_color'] = row['log_adj_trips_color']
            rect_dict['log_adj_trips'] = round(row['log_adj_trips'], 2)

            rects.append(rect_dict)
        return rects

    def build_shape_data(self):
        """ Build shape data from rounded lat/lng regions.
            Also take the average of the trips and adj_trips cols for each region
            and create corresponding hex color columns
        """
        # Group demand data by lat/lng region and average across other cols
        df = self.df_demand.groupby(['upper_lat', 'lower_lat', 'left_long', 'right_long'])[['avail_perc', 'count_time', 'cdf_sum', 'trips', 'adj_trips']].mean().reset_index()
        print(df.head())
        # Create color columns
        df = self.map_values_to_color(df, 'trips')
        df = self.map_values_to_color(df, 'adj_trips')
        # Create log of trips and adj_trips and generate those color cols
        df['log_trips'] = np.log10(df['trips'])
        df['log_adj_trips'] = np.log10(df['adj_trips'])
        df = self.map_values_to_color(df, 'log_trips')
        df = self.map_values_to_color(df, 'log_adj_trips')
        # Create Rectangle information
        rectangles = self.create_rectangle_lst(df)
        return rectangles

    def get_bounding_lat_long(self, df_demand):
        """ Replace rounded lat/long with bounding lat/longs in self.df_demand
            Instead of the lat long columns, we want to have 4 cols: upper lat,
            lower lat, left long, right long
        """
        rounding_value = 0.01
        # delete lat and lng columns (if they exist)
        if 'lat' in df_demand.columns:
            del df_demand['lat']
        if 'lng' in df_demand.columns:
             del df_demand['lng']
        # rename lat2 and lng2 columns
        df_demand = df_demand.rename(columns={'lat2': 'lat', 'lng2': 'lng'})
        # create bounding lat/long cols
        df_demand['upper_lat'] = df_demand['lat']+(rounding_value/2) # north
        df_demand['lower_lat'] = df_demand['lat']-rounding_value/2 # south
        df_demand['left_long'] = df_demand['lng']-rounding_value/2 # west
        df_demand['right_long'] = df_demand['lng']+rounding_value/2 # east
        # select for cols we want
        df_demand = df_demand[["date", "upper_lat", "lower_lat",
                                "left_long", "right_long", "avail_perc",
                                "count_time", "cdf_sum", "trips", "adj_trips"]]
        return df_demand

    def process_data(self):
        """ Takes in events and locations data, computes availability and pickup
            info, and estimates demand
        """
        timer_start = time.time()
        # df_interval = pd.read_csv('../../../data_files/20210206_intervalCountsLATLNG.csv')
        df_interval = countIntervals.count_intervals(self.df_locations, self.START, self.END)
        print("Finished computing interval data")
        # df_pickup = pd.read_csv('../../../data_files/20210206_pickupsLatLng.csv')
        df_pickup = computePickupsData.compute_pickups(self.df_events, self.START, self.END)
        print("Finished computing pickups data")
        df_demand = estimateDemand.estimate_demand(self.df_events, df_pickup, df_interval, self.START, self.END)
        print("Finished estimating demand")
        # Complete some further demand data processing
        df_demand = self.get_bounding_lat_long(df_demand)
        timer_end = time.time()
        print('Elapsed time to process data:', (timer_end - timer_start)/60.0, 'minutes')
        self.df_demand = df_demand
        # save dataframes for testing purposes
        # df_interval.to_csv('../../../data_files/20210216_intervalCountsLATLNG.csv', index=False)
        # df_pickup.to_csv('../../../data_files/20210216_pickupsLatLng.csv', index=False)
        # df_demand.to_csv('../../../data_files/20210223_demandLatLng.csv', index=False)

if __name__ == '__main__':
    # eventsFile = '../../../data_files/events.csv'
    # locationsFile = '../../../data_files/locations_for_multiple_providers_from_18-11-01_to_19-11-01.csv'
    # df_events = pd.read_csv(eventsFile)
    # df_locations = pd.read_csv(locationsFile)
    # processor = DataProcessor(df_events, df_locations)
    # processor.process_data()
    # print(processor.get_demand().shape)

    processor = DataProcessor()
    rects = processor.build_shape_data()
    print(rects[:5])
    # df = processor.map_values_to_color(processor.get_demand(), 'trips')
    # print(df.head())
