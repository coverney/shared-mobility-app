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
        self.df_events = df_events
        self.df_locations = df_locations
        self.df_demand = None
        self.demand_file = None

    def get_demand(self):
        return self.df_demand

    def get_demand_file(self):
        return self.demand_file

    def process_data(self):
        """ Takes in events and locations data, computes availability and pickup
            info, and estimates demand
        """
        timer_start = time.time()
        # df_interval = pd.read_csv('../../../data_files/20210120_intervalCountsLATLNG.csv')
        df_interval = countIntervals.count_intervals(self.df_locations, self.START, self.END)
        # save dataframes for testing purposes
        # df_interval.to_csv('../../../data_files/20210206_intervalCountsLATLNG.csv', index=False)
        print("Finished computing interval data")
        # df_pickup = pd.read_csv('../../../data_files/20210120_pickupsLatLng.csv')
        df_pickup = computePickupsData.compute_pickups(self.df_events, self.START, self.END)
        # save dataframes for testing purposes
        # df_pickup.to_csv('../../../data_files/20210206_pickupsLatLng.csv', index=False)
        print("Finished computing pickups data")
        df_demand = estimateDemand.estimate_demand(self.df_events, df_pickup, df_interval, self.START, self.END)
        # save dataframes for testing purposes
        # df_demand.to_csv('../../../data_files/20210210_demandLatLng.csv', index=False)
        print("Finished estimating demand")
        timer_end = time.time()
        print('Elapsed time to process data:', (timer_end - timer_start)/60.0, 'minutes')
        self.df_demand = df_demand

if __name__ == '__main__':
    eventsFile = '../../../data_files/events.csv'
    locationsFile = '../../../data_files/locations_for_multiple_providers_from_18-11-01_to_19-11-01.csv'
    df_events = pd.read_csv(eventsFile)
    df_locations = pd.read_csv(locationsFile)
    processor = DataProcessor(df_events, df_locations)
    processor.process_data()
    print(processor.get_demand().shape)
