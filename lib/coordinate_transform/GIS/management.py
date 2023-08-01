# Author: ericlwc

import geopandas as gpd
import os
import pandas as pd
import rasterio
from shapely.geometry import Point
import shutil

try:
    from .lib.ProjParser import parse_crs
    from .lib.PathParser import Path
except:
    from lib.ProjParser import parse_crs
    from lib.PathParser import Path


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


def DefineProjection(in_dataset, coor_system):
    """
    Overwrites the coordinate system information (map projection and datum) stored with a raster(GeoTIFF) or feature(shp). This tool is intended for datasets that have an unknown or incorrect coordinate system defined.
    定義一個地理資料(圖徵或網格)的座標系統，並且覆寫該檔案原本的座標系統

    Args:
        in_dataset: The file path of feature(must be shp) or raster(must be GeoTIFF) to be projected.
        coor_system: The coordinate system to which the input feature will be projected. It can be an EPSG code if int, a WKT string if str, or a pyproj CRS object.
    """
    # 編輯記錄
    # 2023/06/29 撰寫
    
    # check in_dataset argument
    if os.path.isfile(in_dataset):
        pass
    else:
        raise ValueError("Invalid input dataset. It must be a path to a shapefile or a GeoTIFF file.")
    
    # check in_dataset data type
    if in_dataset.lower().endswith(".shp"):
        data_type = "feature"
    elif in_dataset.lower().endswith(".tif") or in_dataset.lower().endswith(".tiff"):
        data_type = "raster"
    else:
        raise ValueError("Invalid input dataset. It must be a path to a shapefile(.shp) or a GeoTIFF(.tif/tiff) file.")
    
    # check in_dataset is correct feature or raster or not, if is correct, read it
    if data_type == "feature":
        gpd.read_file(in_dataset)
    elif data_type == "raster":
        rasterio.open(in_dataset)
        
    # check coor_system argument
    new_crs = parse_crs(coor_system)

    # if is a feature, create(overwrite) a .prj file with 
    if data_type == "feature":
        # 創建一個空的GeoDataFrame，設定座標系統，並儲存至in_dataset的同一個資料夾，但命名為TeMp.shp
        point = Point(0, 0)
        gdf = gpd.GeoDataFrame(geometry=[point])
        gdf.crs = new_crs
        gdf.to_file(os.path.dirname(in_dataset) + "/TeMp.shp", driver="ESRI Shapefile", crs=new_crs)

        # 將TeMp.prj改名成"in_dataset"的prj檔案
        ori = os.path.dirname(in_dataset) + "/TeMp.prj"
        new = os.path.dirname(in_dataset) + "/" + os.path.basename(in_dataset).split(".")[0] + ".prj"
        os.rename(ori, new)

        # 刪除資料夾中包含TeMp名稱的檔案
        for file in os.listdir(os.path.dirname(in_dataset)):
            if "TeMp" in file:
                os.remove(os.path.dirname(in_dataset) + "/" + file)


    # if is a raster
    elif data_type == "raster":
        with rasterio.open(in_dataset, "r+") as raster_file: # r+模式使改變屬性的同時可以一起儲存
            # update crs
            raster_file.crs = new_crs

            # 更新其他資料
            raster_file.update_tags(**new_crs.to_dict())
            raster_file.update_tags(**raster_file.profile)

    
def CopyFeatures(in_features, out_feature_class):
    """
    Copies feature (all file associated with shp file) from path.

    Args:
        input_features: SHP file path of features to be copied.
        output_feature_class:  SHP file path of features to be created.
    """
    # 編輯記錄
    # 2023/06/29 撰寫

    # create Path object
    src = Path(in_features, type="file")
    dst = Path(out_feature_class, type="file")

    # check
    src_is_shp = src.extension == "shp"
    dst_is_shp = dst.extension == "shp"
    src_is_existed_file = src.is_existed_file

    if (not src_is_shp) or (not src_is_existed_file):
        raise ValueError("Invalid input features. It must be a path to a shapefile(shp).")
    if (not dst_is_shp):
        raise ValueError("Invalid output feature class. It must be a path to a shapefile(shp).")
    
    # list path of all required subfiles (.shp, .shx, .dbf) of input shp file, check if all of them are existed, if yes, copy them to dst, else raise error
    # list
    required_files = {
        src.abs_path : dst.abs_path,
        src.abs_path[:-4] + ".shx" : dst.abs_path[:-4] + ".shx",
        src.abs_path[:-4] + ".dbf" : dst.abs_path[:-4] + ".dbf"
    }
    # check if required files are all existed
    for src_file in required_files.keys():
        if not Path(src_file, type="file").is_existed_file:
            raise ValueError(f"Invalid input features. '{src_file}' missed.")
    # copy
    for src_file, dst_file in required_files.items():
        shutil.copy(src_file, dst_file)

    # list path of all optional subfiles [.prj, .sbn, .sbx, .fbn, .fbx, .ain, .aih, .ixs, .mxs, .cpg, .shp.xml] of input shp file, check if all of them are existed, if yes, copy them to dst
    # list
    optional_files = {
        src.abs_path[:-4] + ".prj" : dst.abs_path[:-4] + ".prj",
        src.abs_path[:-4] + ".sbn" : dst.abs_path[:-4] + ".sbn",
        src.abs_path[:-4] + ".sbx" : dst.abs_path[:-4] + ".sbx",
        src.abs_path[:-4] + ".fbn" : dst.abs_path[:-4] + ".fbn",
        src.abs_path[:-4] + ".fbx" : dst.abs_path[:-4] + ".fbx",
        src.abs_path[:-4] + ".ain" : dst.abs_path[:-4] + ".ain",
        src.abs_path[:-4] + ".aih" : dst.abs_path[:-4] + ".aih",
        src.abs_path[:-4] + ".ixs" : dst.abs_path[:-4] + ".ixs",
        src.abs_path[:-4] + ".mxs" : dst.abs_path[:-4] + ".mxs",
        src.abs_path[:-4] + ".cpg" : dst.abs_path[:-4] + ".cpg",
        src.abs_path[:-4] + ".shp.xml" : dst.abs_path[:-4] + ".shp.xml"
    }
    # copy if is existed
    for src_file, dst_file in optional_files.items():
        if Path(src_file, type="file").is_existed_file:
            shutil.copy(src_file, dst_file)
    

def CopyRaster(in_raster, out_rasterdataset):
    """
    Copies raster (all file associated with tif file) from path.

    Args:
        in_raster: TIF file (.tif) path of raster to be copied.
        out_rasterdataset:  TIF file (.tif) path of raster to be created.
    """
    # 編輯記錄
    # 2023/07/05 撰寫

    # create Path object
    src = Path(in_raster, type="file")
    dst = Path(out_rasterdataset, type="file")

    # check
    src_is_tif = src.extension == "tif"
    dst_is_tif = dst.extension == "tif"

    if (not src_is_tif) or (not src.is_existed_file):
        raise ValueError("Invalid input raster. It must be a path to a tif file.")
    if (not dst_is_tif):
        raise ValueError("Invalid output raster. It must be a path to a tif file.")
    
    # list path of all required subfiles (.tif) of input tif file, check if all of them are existed, if yes, copy them to dst, else raise error
    # list
    required_files = {
        src.abs_path : dst.abs_path
        }
    # copy
    for src_file, dst_file in required_files.items():
        shutil.copy(src_file, dst_file)

    # list path of all optional subfiles [.tfw, .tif.aux.xml, .tif.ovr, .tif.xml] of input tif file, check if all of them are existed, if yes, copy them to dst
    # list
    optional_files = {
        src.abs_path[:-4] + ".tfw" : dst.abs_path[:-4] + ".tfw",
        src.abs_path[:-4] + ".tif.aux.xml" : dst.abs_path[:-4] + ".tif.aux.xml",
        src.abs_path[:-4] + ".tif.ovr" : dst.abs_path[:-4] + ".tif.ovr",
        src.abs_path[:-4] + ".tif.xml" : dst.abs_path[:-4] + ".tif.xml"
    }
    # copy if is existed
    for src_file, dst_file in optional_files.items():
        if Path(src_file, type="file").is_existed_file:
            shutil.copy(src_file, dst_file)


def Delete(in_data):
    """
    Deletes data from path.
    """
    # 編輯記錄
    # 2023/07/05 撰寫

    # 識別檔案是shp還是tif
    delete_path = Path(in_data, type="file")
    delete_path_is_shp = delete_path.extension == "shp"
    delete_path_is_tif = delete_path.extension == "tif"

    # 如果是shp，則刪除.shp, .shx, .dbf, .prj, .sbn, .sbx, .fbn, .fbx, .ain, .aih, .ixs, .mxs, .cpg, .shp.xml
    if delete_path_is_shp:
        delete_files = [
            delete_path.abs_path,
            delete_path.abs_path[:-4] + ".shx",
            delete_path.abs_path[:-4] + ".dbf",
            delete_path.abs_path[:-4] + ".prj",
            delete_path.abs_path[:-4] + ".sbn",
            delete_path.abs_path[:-4] + ".sbx",
            delete_path.abs_path[:-4] + ".fbn",
            delete_path.abs_path[:-4] + ".fbx",
            delete_path.abs_path[:-4] + ".ain",
            delete_path.abs_path[:-4] + ".aih",
            delete_path.abs_path[:-4] + ".ixs",
            delete_path.abs_path[:-4] + ".mxs",
            delete_path.abs_path[:-4] + ".cpg",
            delete_path.abs_path[:-4] + ".shp.xml"
        ]
        for delete_file in delete_files:
            if Path(delete_file, type="file").is_existed_file:
                os.remove(delete_file)

    # 如果是tif，則刪除.tif, .tfw, .tif.aux.xml, .tif.ovr, .tif.xml
    elif delete_path_is_tif:
        delete_files = [
            delete_path.abs_path,
            delete_path.abs_path[:-4] + ".tfw",
            delete_path.abs_path[:-4] + ".tif.aux.xml",
            delete_path.abs_path[:-4] + ".tif.ovr",
            delete_path.abs_path[:-4] + ".tif.xml"
        ]
        for delete_file in delete_files:
            if Path(delete_file, type="file").is_existed_file:
                os.remove(delete_file)