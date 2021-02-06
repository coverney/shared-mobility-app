import pandas as pd
import computePickupsData
import countIntervals
import estimateDemand
import time

start = "2018-11-01T06:00:00-04:00"
end = "2019-10-31T22:00:00-04:00"

def process_data(df_events, df_locations):
    """ Takes in events and locations data, computes availability and pickup
        info, and estimates demand
    """
    timer_start = time.time()
    # df_interval = pd.read_csv('../../../data_files/20210120_intervalCountsLATLNG.csv')
    df_interval = countIntervals.count_intervals(df_locations, start, end)
    # save dataframes for testing purposes
    # df_interval.to_csv('../../../data_files/20210206_intervalCountsLATLNG.csv', index=False)
    print("Finished computing interval data")
    # df_pickup = pd.read_csv('../../../data_files/20210120_pickupsLatLng.csv')
    df_pickup = computePickupsData.compute_pickups(df_events, start, end)
    # save dataframes for testing purposes
    # df_pickup.to_csv('../../../data_files/20210206_pickupsLatLng.csv', index=False)
    print("Finished computing pickups data")
    df_demand = estimateDemand.estimate_demand(df_events, df_pickup, df_interval, start, end)
    # save dataframes for testing purposes
    # df_demand.to_csv('../../../data_files/20210206_demandLatLng.csv', index=False)
    print("Finished estimating demand")
    timer_end = time.time()
    print('Elapsed time to process data:', (timer_end - timer_start)/60.0, 'minutes')

if __name__ == '__main__':
    eventsFile = '../../../data_files/events.csv'
    locationsFile = '../../../data_files/locations_for_multiple_providers_from_18-11-01_to_19-11-01.csv'
    df_events = pd.read_csv(eventsFile)
    df_locations = pd.read_csv(locationsFile)
    process_data(df_events, df_locations)
