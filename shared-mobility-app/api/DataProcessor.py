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

    # would need to incorporate in __init__ or take from data
    START = "2018-11-01T06:00:00-04:00"
    END = "2019-10-31T22:00:00-04:00"

    def __init__(self, df_events=None, df_locations=None):
        """ Constructor for DataProcessor class with the inputs being the events
            and location data files
        """
        self.df_events = df_events
        self.df_locations = df_locations
        self.df_demand = None
        # self.df_demand = pd.read_csv('../../../data_files/20210216_demandLatLng.csv')
        # self.demand_file = None

    def get_demand(self):
        """ Return the demand dataframe after it has been generated
        """
        return self.df_demand

    def set_events(self, df_events):
        self.df_events = df_events

    def set_locations(self, df_locations):
        self.df_locations = df_locations

    # def get_demand_file(self):
    #     return self.demand_file

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

    def generate_lat_lng_rects(self, west_lngs, east_lngs, south_lats, north_lats):
        """ Create DataFrame with lat/lng for each corner of a rectangle grid square.
            The id corresponds to a unique grid square and the other of points
            are upper left, upper right, bottom left, bottom right
        """
        df = pd.DataFrame(columns=['id', 'lat', 'lng'])
        for index, west_lng in enumerate(west_lngs):
            # Goes upper left, upper right, bottom left, bottom right
            df = df.append({'id':index, 'lat':north_lats[index], 'lng':west_lng}, ignore_index=True) # upper left
            df = df.append({'id':index, 'lat':north_lats[index], 'lng':east_lngs[index]}, ignore_index=True) # upper right
            df = df.append({'id':index, 'lat':south_lats[index], 'lng':west_lng}, ignore_index=True) # bottom left
            df = df.append({'id':index, 'lat':south_lats[index], 'lng':east_lngs[index]}, ignore_index=True) # bottom right
        return df

    def create_rectangle_lst(self, df):
        """ Create list of dictionaries with each dict containing information
            needed to create the React Leaflet rectangles (name, bounds, color)
        """
        rects = []
        for index, row in df.iterrows():
            rect_dict = {}
            # get the upper left and bottom right coordinates
            upper_left = [row['north_lat'], row['west_lng']]
            bottom_right = [row['south_lat'], row['east_lng']]
            rect_dict['bounds'] = [upper_left, bottom_right]
            rect_dict['name'] = "Rectangle " + str(index)
            rect_dict['trips_color'] = row['trips_color']
            rect_dict['trips'] = round(row['trips'], 2)
            rect_dict['adj_trips_color'] = row['adj_trips_color']
            rect_dict['adj_trips'] = round(row['adj_trips'], 2)
            rect_dict['lat'] = row['lat']
            rect_dict['lng'] = row['lng']
            rects.append(rect_dict)

        # for index, west_lng in enumerate(west_lngs):
        #     rect_dict = {}
        #     # get the upper left and bottom right coordinates
        #     upper_left = [north_lats[index], west_lng]
        #     bottom_right = [south_lats[index], east_lngs[index]]
        #     rect_dict['bounds'] = [upper_left, bottom_right]
        #     rect_dict['name'] = "Rectangle " + str(index)
        #     rect_dict['color'] = '#39B32D'
        #     rects.append(rect_dict)
        return rects

    def build_shape_data(self):
        """ Build shape data from rounded lat/lng regions.
            Also take the average of the trips and adj_trips cols for each region
            and create corresponding hex color columns
        """
        # Group demand data by lat/lng region and average across other cols
        df = self.df_demand.groupby(['tract', 'lat', 'lng'])[['avail_perc', 'count_time', 'cdf_sum', 'trips', 'adj_trips']].mean().reset_index()
        # print(df.head())
        # Create color columns
        df = self.map_values_to_color(df, 'trips')
        df = self.map_values_to_color(df, 'adj_trips')
        # Round lat/lng regions to find coordinates of the rectangles
        rounding_value = 0.01
        df['west_lng'] = df['lng']-rounding_value/2
        df['east_lng'] = df['lng']+rounding_value/2
        df['south_lat'] = df['lat']-rounding_value/2
        df['north_lat'] = df['lat']+rounding_value/2
        rectangles = self.create_rectangle_lst(df)
        return rectangles

        # # Round lat/lng regions to find coordinates of the rectangles
        # rounding_value = 0.01
        # df = self.df_demand.drop_duplicates(subset=['lat', 'lng'])
        # lngs = df['lng']
        # lats = df['lat']
        # west_lngs = lngs-rounding_value/2
        # east_lngs = lngs+rounding_value/2
        # south_lats = lats-rounding_value/2
        # north_lats = lats+rounding_value/2
        # # df_rects = self.generate_lat_lng_rects(west_lngs.values, east_lngs.values, south_lats.values, north_lats.values)
        # return self.create_rectangle_lst(west_lngs.values, east_lngs.values, south_lats.values, north_lats.values)

    def process_data(self):
        """ Takes in events and locations data, computes availability and pickup
            info, and estimates demand
        """
        timer_start = time.time()
        # df_interval = pd.read_csv('../../../data_files/20210206_intervalCountsLATLNG.csv')
        df_interval = countIntervals.count_intervals(self.df_locations, self.START, self.END)
        # save dataframes for testing purposes
        # df_interval.to_csv('../../../data_files/20210216_intervalCountsLATLNG.csv', index=False)
        print("Finished computing interval data")
        # df_pickup = pd.read_csv('../../../data_files/20210206_pickupsLatLng.csv')
        df_pickup = computePickupsData.compute_pickups(self.df_events, self.START, self.END)
        # save dataframes for testing purposes
        # df_pickup.to_csv('../../../data_files/20210216_pickupsLatLng.csv', index=False)
        print("Finished computing pickups data")
        df_demand = estimateDemand.estimate_demand(self.df_events, df_pickup, df_interval, self.START, self.END)
        print("Finished estimating demand")
        timer_end = time.time()
        print('Elapsed time to process data:', (timer_end - timer_start)/60.0, 'minutes')
        # rename lat2 and lng2 columns
        df_demand = df_demand.rename(columns={'lat2': 'lat', 'lng2': 'lng'})
        df_demand = df_demand[["date", "tract", "lat", "lng", "avail_perc", "count_time", "cdf_sum", "trips", "adj_trips"]]
        # save dataframes for testing purposes
        # df_demand.to_csv('../../../data_files/20210216_demandLatLng.csv', index=False)
        self.df_demand = df_demand

if __name__ == '__main__':
    # eventsFile = '../../../data_files/events.csv'
    # locationsFile = '../../../data_files/locations_for_multiple_providers_from_18-11-01_to_19-11-01.csv'
    # df_events = pd.read_csv(eventsFile)
    # df_locations = pd.read_csv(locationsFile)
    # processor = DataProcessor(df_events, df_locations)
    # processor.process_data()
    # print(processor.get_demand().shape)

    processor = DataProcessor()
    df = processor.build_shape_data()
    print(df[:5])
    # df = processor.map_values_to_color(processor.get_demand(), 'trips')
    # print(df.head())
