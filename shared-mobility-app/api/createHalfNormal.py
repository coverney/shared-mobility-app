import numpy as np
from math import sqrt, floor
from scipy.stats import halfnorm

def get_distances(distance, max_distance):
    """ Generate a sorted list of all possible distances given the size of each grid cell and
        the maximum distance. This relies on the pythagorean theorem!
        Also creates a dictionary that maps distance with triangle dimensions
    """
    # find the ratio of max_distance to distance
    # the side lengths of all the triangles can not exceed that ratio
    factor = floor(max_distance/distance)
    dists = set([0, max_distance])
    triangles = {0:(0,0)} # make the dict that maps dist to triangle dimensions
    # create list of distances that are purely in vertical or horizontal direction
    for i in range(1, factor+1):
        dists.add(i*distance)
        triangles[i*distance] = (i, 0)
    # create the triangles and include distances that are less than max_distance
    for i in range(1, factor+1):
        for j in range(i, factor+1):
            hypotenuse_dist = sqrt(i**2+j**2) * distance
            if hypotenuse_dist < max_distance:
                dists.add(hypotenuse_dist)
                triangles[hypotenuse_dist] = (i, j)
    return sorted(list(dists)), triangles

def generate_cdfs(sigma, distance, max_distance, checkNorm=True, returnTriangles=False):
    """ Given sigma, create half normal distribution and discretize by outputting a dictionary
        where the key is the distance and the value is the cdf at that distance
    """
    # create array of distances
    distances, triangles = get_distances(distance, max_distance)
    # print(f"Distances are {distances}")
    # create half normal distribution
    rv = halfnorm(scale=sigma, loc=0)
    # find cdf values
    cdfs = {}
    prob_sum = 0
    for left, right in zip(distances, distances[1:]):
        prob_sum = rv.cdf(right)-rv.cdf(0) 
        cdfs[left] = prob_sum
    
    # normalize cdfs
    norm_cdfs = {k: v / prob_sum for k, v in cdfs.items()}

    #if checkNorm:
    #    assert int(round(sum(norm_cdfs.values(), 0.0))) == 1
    if returnTriangles:
        # combine triangles into norm_cdfs
        ds = [norm_cdfs, triangles]
        combined_dict = {}
        for k in norm_cdfs.keys():
            combined_dict[k] = tuple(d[k] for d in ds)
        return combined_dict
    else:
        return norm_cdfs

def get_p0(sigma, distance, max_distance):
    """ From sigma value make half normal distribution and calculate p0 value.
        p0 is basically cdf(distance)
    """
    norm_cdfs = generate_cdfs(sigma, distance, max_distance)
    return norm_cdfs[0]

def search_sigma(p0, distance, max_distance):
    """ Binary search over sigma range to find which sigma gives us the expected p0
    """
    # if p0 in percent form, then convert to decimal
    if p0 > 1:
        p0 = p0/100.0
    min_sigma = 50
    max_sigma = 1500
    # sigmas = list(range(min_sigma, max_sigma+1))
    sigmas = np.arange(min_sigma, max_sigma+0.25, 0.25)
    # do binary search
    left_idx = 0
    right_idx = len(sigmas)-1
    closest_sigma = float("inf")
    closest_p0 = float("inf")
    while(left_idx <= right_idx):
        mid_idx = (left_idx + right_idx) // 2
        mid_p0 = get_p0(sigmas[mid_idx], distance, max_distance)
        # update closest_sigma and closest_p0 if applicable
        if abs(p0 - mid_p0) < abs(p0 - closest_p0):
            closest_sigma = sigmas[mid_idx]
            closest_p0 = mid_p0
        if mid_p0 > p0: # sigma needs to be bigger
            left_idx = mid_idx + 1
        else:
            right_idx = mid_idx - 1
    print(f"found closeset match at sigma={closest_sigma} with p0={closest_p0}")
    return closest_sigma

def create_distribution(p0, distance, max_distance):
    """ Create discretized half normal distribution from inputted p0
        Return normalized cdf values
    """
    # find sigma from p0 value
    sigma = search_sigma(p0, distance, max_distance)
    return generate_cdfs(sigma, distance, max_distance, returnTriangles=True)
