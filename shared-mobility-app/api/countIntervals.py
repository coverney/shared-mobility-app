import pandas as pd
import numpy as np
import utils
import time
from multiprocessing import Pool, cpu_count
from functools import partial
import iso8601

def prep_count_data(df, start, end):
    """ Prepare locations data to generate intervals
    """
    df = df.copy()
    df = df.dropna() # remove Nans
    df = df[(df['vehicle_status'] == "available") & (df['provider'] != "JUMP")] # select providers that aren't jump and are available
    df = df.drop(['provider', 'vehicle_status', 'vehicle_status_reason', 'device_type', 'areas'], axis=1) # remove unneeded columns
    df = df[((df['start_time'] >= start) & (df['start_time'] <= end)) |
            ((df['end_time'] >= start) & (df['end_time'] <= end))] # filter out times out of the inputted range
    df_subset = df.drop(['start_time', 'end_time'], axis=1) # drop start_time and end_time
    # duplicate the dataframe because we are separating the start and end times
    df_repeated_subset = pd.DataFrame(np.repeat(df_subset.values, 2, axis=0))
    df_repeated_subset.columns = df_subset.columns
    df_repeated_subset['time'] = df[['start_time', 'end_time']].stack().reset_index(level=[0,1], drop=True) # stack the start and end time into one column
    df_repeated_subset['time_type'] = pd.Series(['start_time', 'end_time']*int(df_repeated_subset.shape[0]/2)) # create time_type column
    return df_repeated_subset

def count_region(df, start, end):
    """ Aggregates availability for df, which represents one lat/long region
    """
    df = df.copy()
    df = df.sort_values(by='time', ignore_index=True) # sort df by time (ascending)
    df_interval = pd.DataFrame(index=range(df.shape[0]), columns=['tract', 'start', 'end', 'count', 'avail']) # create df_interval
    current_time = start
    current_count = 0
    for index, row in df.iterrows():
        # find the next time and count
        next_time = row['time']
        next_count = current_count + 1
        if row['time_type'] == 'end_time':
            next_count -= 2
        # if within time then record interval
        if (next_time >= start) and (current_time <= end):
            df_interval.loc[index] = {'tract':row['tract'], 'start':current_time, 'end':next_time, 'count':current_count,
                                    'avail':((iso8601.parse_date(next_time) - iso8601.parse_date(current_time)).total_seconds() / 60)}
        current_count = next_count
        current_time = next_time
    return df_interval

def get_count_data(df, func, start, end):
    """ Counts availability within intervals based on locations data
    via parallelization. Each lat/long region is treated separately
    """
    df = df.copy()
    df_grouped = df.groupby('tract', sort=False, as_index=False) # group df by tract
    assert len(df_grouped) == len(set(df['tract'].values))
    # print('Number of groups:', len(df_grouped))
    # df_sub_grouped = [g[1] for g in list(df_grouped)[:3]] # for testing only
    with Pool(cpu_count()) as p:
        # ret_list = p.map(partial(func, start=start, end=end), [group for group in df_sub_grouped]) # for testing only
        ret_list = p.map(partial(func, start=start, end=end), [group for name, group in df_grouped])
    return pd.concat(ret_list)

def count_intervals(df_locations, start, end):
    """ Generate interval data, which gives time intervals within a lat/long region
    where a certain number of scooters are available
    """
    df_locations_latlng = utils.round_lat_long(df_locations)
    df_locations_tracts = utils.create_fake_tract(df_locations_latlng)
    df_locations_cleaned = prep_count_data(df_locations_tracts, start, end)
    timer_start = time.time()
    df_result = get_count_data(df_locations_cleaned, count_region, start, end)
    timer_end = time.time()
    print('Elapsed time to count intervals with parallelization:', (timer_end - timer_start)/60.0, 'minutes')
    # doing some further processing before saving
    return utils.undo_fake_tract(df_result.dropna())
