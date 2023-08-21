# Author: ericlwc

import geopandas as gpd
import pandas as pd

from GIS.lib.ProjParser import parse_crs

def XYTableToPoint(in_table, out_feature_class, x_field, y_field, z_field=None, coordinate_system=None):
    """
    Creates a point feature class from an input table with x, y and z coordinates.
    從包含x、y、z座標的輸入表格創建一個點圖徵類別。

    Args:
        in_table(str): The csv table or pandas dataframe that defines the point feature locations (containing x and y coordinates).
        out_feature_class(str, None): Save the output feature class as a shapefile at here, if don't want to save the output, set it to None.
        x_field(str): The field in the input table that contains the X coordinates (or longitude).
        y_field(str): The field in the input table that contains the Y coordinates (or latitude).
        z_field(str): (optional) The field in the input table that contains the Z coordinates. If not specified, the output point features will have no Z values.
        coordinate_system: (optional) The coordinate system of the x and y coordinates. It can be an EPSG code if int, a WKT string if str, or a pyproj CRS object. If not specified, the output feature class will have no coordinate system defined.
    
    Returns:
        A geopandas GeoDataFrame object that contains the point features.

    Output:
        A shapefile that contains the point features at specific (out_feature_class) path.

    Examples:
        >>> XYTableToPoint(
            in_table="data.csv", 
            out_feature_class="points.shp", 
            x_field="longitude", 
            y_field="latitude", 
            z_field="elevation", 
            coordinate_system="EPSG:4326")
    """    
    # 編輯記錄
    # 2023/06/24 撰寫

    # READ the input table as a pandas DataFrame
    if isinstance(in_table, str):
        df = pd.read_csv(in_table)
    elif isinstance(in_table, pd.DataFrame):
        df = in_table
    else:
        raise ValueError("Invalid input table. It must be a path to a csv or txt file, or a pandas DataFrame object.")
    
    # CHECK if the x and y fields exist in the input table
    if x_field not in df.columns:
        raise ValueError(f"The x field '{x_field}' does not exist in the input table.")
    if y_field not in df.columns:
        raise ValueError(f"The y field '{y_field}' does not exist in the input table.")
    if z_field is not None and z_field not in df.columns:
        raise ValueError(f"The z field '{z_field}' does not exist in the input table.")

    # Create a geopandas GeoDataFrame from the pandas DataFrame
    # Use geopandas.points_from_xy to create a geometry column from the x and y fields
    # Optionally, pass the z field to create 3D point geometries
    if z_field is not None:
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x_field], df[y_field], df[z_field]))
    else:
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x_field], df[y_field]))

    # Set CRS. Use geopandas.GeoDataFrame.set_crs to assign or change the CRS
    # If coordinate_system is not specified, the output feature class will have no coordinate system defined
    if coordinate_system is None:
        pass
    else:
        crs = parse_crs(coordinate_system)
        gdf = gdf.set_crs(crs = crs)

    # Check output feature's field name is under 10 characters

    # Write the output feature class as a shapefile or a geopackage file
    # Use geopandas.GeoDataFrame.to_file to save the GeoDataFrame to disk
    if isinstance(out_feature_class, str):
        gdf.to_file(out_feature_class, driver="ESRI Shapefile", encoding='utf-8')
    elif out_feature_class is None:
        pass
    else:
        raise ValueError("Invalid output feature class. It must be a path to a shapefile.")

    # Return the output feature class as a GeoDataFrame
    return gdf



def Project(in_dataset, out_dataset, out_coor_system):
    """
    Project a feature (shp file) to a new coordinate system.
    將資料集投影到新的座標系統。

    Args:
        in_dataset(str): The feature to be projected.
        out_dataset(str, None): The name and location of the output projected feature, if don't want to save the output, set it to None.
        out_coor_system: The coordinate system to which the input feature will be projected. It can be an EPSG code if int, a WKT string if str, or a pyproj CRS object.

    Returns:
        A geopandas GeoDataFrame object that contains the projected features.

    Output:
        A shapefile that contains the projected features at specific (out_dataset) path.

    Examples:
        >>> Project(
            in_dataset="data.shp",
            out_dataset="projected_data.shp",
            out_coor_system="EPSG:4326")
    """
    # 編輯記錄
    # 2023/06/25 撰寫

    # Read the input dataset as a geopandas GeoDataFrame
    if isinstance(in_dataset, str):
        gdf = gpd.read_file(in_dataset)
    elif isinstance(in_dataset, gpd.GeoDataFrame):
        gdf = in_dataset
    else:
        raise ValueError("Invalid input dataset. It must be a path to a shapefile or a geopandas GeoDataFrame object.")
    
    # transform CRS. Use geopandas.GeoDataFrame.set_crs to assign or change the CRS
    # If coordinate_system is not specified, the output feature class will have no coordinate system defined
    if out_coor_system is None:
        print("Warning: The output coordinate system is not specified. The output dataset will same as the input dataset.")
    else:
        out_coor_system = parse_crs(out_coor_system)
        gdf = gdf.to_crs(crs = out_coor_system)

    # Write the output dataset as a shapefile or a geopackage file
    # Use geopandas.GeoDataFrame.to_file to save the GeoDataFrame to disk
    if isinstance(out_dataset, str):
        gdf.to_file(out_dataset)
    elif out_dataset is None:
        pass
    else:
        raise ValueError("Invalid output dataset. It must be a path to a shapefile.")

    # Return the output dataset as a GeoDataFrame
    return gdf