import pandas as pd
from math import radians, cos, sin, asin, degrees, sqrt

_AVG_EARTH_RADIUS_KM = 6371.0088
DIRECTIONS = ['up', 'down', 'left', 'right', 'left-down', 'left-up', 'right-down', 'right-up']

def get_grid_cell_info(coord, grid):
    """ Take in a lat/lng coordinate and does the following
        - Find which GridCell the coord belongs in
        - Retrieve the bounding lat/lngs and id from the GridCell
        - Return those values
    """
    grid_coord = grid.locate_point(coord)
    grid_cell = grid.get_cells()[grid_coord]
    upper_lat, left_lng = grid_cell.get_upper_left()
    lower_lat, right_lng = grid_cell.get_lower_right()
    return grid_cell.get_id(), round(left_lng, 5), round(right_lng, 5), round(lower_lat, 5), round(upper_lat, 5)

def haversine(p1, p2):
    """ Find distance in km between two lat/lng coordinates
    """
    # unpack latitude/longitude
    lat1, lng1 = p1
    lat2, lng2 = p2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2

    return 2 * _AVG_EARTH_RADIUS_KM * asin(sqrt(d))

def add_distance(distance, coord, direction):
    """ Add distance to inputted coordinate in a particular direction and return new coordinate.
        Diagonal directions means we go up/down and left/right for the inputted distance

        distance: in meters
        coord: (lat, lng)
        direction: up, down, left, right, left-down, left-up, right-down, right-up
    """
    if direction not in DIRECTIONS:
        print("invalid direction inputted")
        return None
    lat, lng = coord
    distance = float(distance / 1000) # convert to KM
    if direction == "up" or direction == "down":
        delta_lat = degrees(distance/_AVG_EARTH_RADIUS_KM)
        return (lat+delta_lat, lng) if direction == "up" else (lat-delta_lat, lng)
    elif direction == "left" or direction == "right":
        numerator = sin(distance / (2 * _AVG_EARTH_RADIUS_KM))
        denominator = cos(radians(lat))
        delta_lng = degrees(2 * asin(numerator/denominator))
        return (lat, lng-delta_lng) if direction == "left" else (lat, lng+delta_lng)
    else:
        # find new lat first
        delta_lat = degrees(distance/_AVG_EARTH_RADIUS_KM)
        lat2 = lat+delta_lat if "up" in direction else lat-delta_lat
        # find delta lng using lat2
        numerator = sin(distance / (2 * _AVG_EARTH_RADIUS_KM))
        denominator = cos(radians(lat2))
        delta_lng = degrees(2 * asin(numerator/denominator))
        return (lat2, lng-delta_lng) if "left" in direction else (lat2, lng+delta_lng)
