import numpy as np

"""
Source:
https://stackoverflow.com/a/238558
"""

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

def WGS84EarthRadius(lat):
    """
    Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
    
    Parameters
    ----------
    lat: latitude coordinate in degrees
    
    Returns
    -------
    estimated Earth radius at the given latitude
    """
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * np.cos(lat)
    Bn = WGS84_b*WGS84_b * np.sin(lat)
    Ad = WGS84_a * np.cos(lat)
    Bd = WGS84_b * np.sin(lat)
    return np.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )


def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    """
    Bounding box surrounding the point at given coordinates, assuming local approximation of Earth surface as a sphere of radius given by WGS84.
    
    Parameters
    ----------
    latitudeInDegrees: latitude coordinate in degrees
    longitudeInDegrees: longitude coordinate in degrees
    
    Returns
    -------
    tuple of 4 items:
      - latitude coordinate of the North of the bounding box
      - longitude coordinate of the West of the bounding box
      - latitude coordinate of the South of the bounding box
      - longitude coordinate of the East of the bounding box
    """
    lat = np.deg2rad(latitudeInDegrees)
    lon = np.deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm
    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*np.cos(lat)
    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius
    return (np.rad2deg(latMin), np.rad2deg(lonMin), np.rad2deg(latMax), np.rad2deg(lonMax))