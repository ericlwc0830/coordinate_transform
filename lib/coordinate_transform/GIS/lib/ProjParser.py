import pyproj

# 識別一段內容是否為地理/投影座標系統資訊，並以pyproj.crs.CRS物件回傳
def parse_crs(coordinate_system):
    """
    
    識別一段內容是否為地理/投影座標系統資訊，並以pyproj.crs.CRS物件回傳

    Args:
        coordinate_system: The coordinate system. It can be an EPSG code if int or numeric str, a WKT string if str, or a pyproj CRS object.
    
    Returns:
        A pyproj CRS object (pyproj.crs.CRS) that contains the coordinate system information.
    """
    # if coordinate_system is EPSG code
    if isinstance(coordinate_system, int):
        coordinate_system = pyproj.crs.CRS.from_epsg(coordinate_system)
    elif isinstance(coordinate_system, str) and coordinate_system.isnumeric():
        coordinate_system = pyproj.crs.CRS.from_epsg(int(coordinate_system))
    # if coordinate_system is WKT string
    elif isinstance(coordinate_system, str) and coordinate_system.isnumeric() is False:
        coordinate_system = pyproj.crs.CRS.from_wkt(coordinate_system)
    # if coordinate_system is pyproj CRS object
    elif isinstance(coordinate_system, pyproj.crs.CRS):
        coordinate_system = coordinate_system
    # if coordinate_system is not EPSG code, WKT string, or pyproj CRS object raise an error
    elif coordinate_system is None:
        return None
    # else raise an error
    else:
        raise ValueError("Invalid coordinate system. It must be an EPSG code, a WKT string, or a pyproj CRS object.")

    return coordinate_system