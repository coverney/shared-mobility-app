import pandas as pd
import computePickupsData
import countIntervals
import estimateDemand
import time

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
        # self.df_demand = None
        self.df_demand = pd.read_csv('../../../data_files/20210216_demandLatLng.csv')
        # self.demand_file = None

    def get_demand(self):
        """ Return the demand dataframe after it has been generated
        """
        return self.df_demand

    # def get_demand_file(self):
    #     return self.demand_file

    def generate_lat_lng_rects(self, west_lngs, east_lngs, south_lats, north_lats):
        df = pd.DataFrame(columns=['id', 'lat', 'lng'])
        for index, west_lng in enumerate(west_lngs):
            # Goes upper left, bottom left, bottom right, upper right
            df = df.append({'id':index, 'lat':north_lats[index], 'lng':west_lng}, ignore_index=True)
            df = df.append({'id':index, 'lat':south_lats[index], 'lng':west_lng}, ignore_index=True)
            df = df.append({'id':index, 'lat':south_lats[index], 'lng':east_lngs[index]}, ignore_index=True)
            df = df.append({'id':index, 'lat':north_lats[index], 'lng':east_lngs[index]}, ignore_index=True)
        return df

    def build_shape_data(self):
        """ Build shape data from rounded lat/lng regions
        """
        rounding_value = 0.01
        df = self.df_demand.drop_duplicates(subset=['lat', 'lng'])
        lngs = df['lng']
        lats = df['lat']
        west_lngs = lngs-rounding_value/2
        east_lngs = lngs+rounding_value/2
        south_lats = lats-rounding_value/2
        north_lats = lats+rounding_value/2
        df_rects = self.generate_lat_lng_rects(west_lngs.values, east_lngs.values, south_lats.values, north_lats.values)
        print(df_rects.head(10))

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
    processor.build_shape_data()
