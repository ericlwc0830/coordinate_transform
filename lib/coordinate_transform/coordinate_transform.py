# Author: ericlwc

import os

from GIS.management import *
from GIS.lib.ProjParser import parse_crs

def coordinate_transform(in_table_path, in_x_field, in_y_field, in_crs, out_table_path, out_x_field, out_y_field, out_crs):
    """
    將輸入表格中的座標欄位從一個座標系統轉換成另一個座標系統，並新增轉換過的座標欄位至已經帶有舊座標欄位的表格並儲存。這個功能不會異動原本的資料，除非 in_table_path 與 out_table_path 相同。

    Args:
        in_table_path (str): 輸入表格的路徑
        in_x_field (str): 輸入表格的x座標欄位
        in_y_field (str): 輸入表格的y座標欄位
        in_crs (int/str/CRS): 輸入表格的座標系統，可以是epsg代碼、wkt字串、prj檔路徑、pyproj.crs.CRS物件
        out_table_path (str/None): 輸出表格的路徑，若與in_table_path相同則會覆蓋原本的檔案，若為None則不會儲存
        out_x_field (str): 輸出表格的x座標欄位，該欄位若不存在則創建，存在則覆蓋該欄位原本的內容
        out_y_field (str): 輸出表格的y座標欄位，該欄位若不存在則創建，存在則覆蓋該欄位原本的內容
        out_crs (int/str/CRS): 輸出表格的座標系統，可以是epsg代碼、wkt字串、prj檔路徑、pyproj.crs.CRS物件

    Returns:
        轉換過的padnas.DataFrame
    """
    # CHECK in_table_path
    if not os.path.isfile(in_table_path):
        raise ValueError("in_table_path does not exist.")

    # READ in_table_path
    df = pd.read_csv(in_table_path)

    # CHECK if in_x_field == in_y_field
    if in_x_field == in_y_field:
        raise ValueError("in_x_field same as in_y_field")
    
    # CHECK if in_x_field is in df.columns
    if not isinstance(in_x_field, str):
        raise ValueError("in_x_field must be a string")
    if in_x_field not in df.columns:
        raise ValueError("in_x_field does not exist in the input table")
    
    # CHECK if in_y_field is in df.columns
    if not isinstance(in_y_field, str):
        raise ValueError("in_y_field must be a string")
    if in_y_field not in df.columns:
        raise ValueError("in_y_field does not exist in the input table")
    
    # CHECK if in_crs is valid
    in_crs = parse_crs(in_crs)

    # CHECK if out_table_path is valid
    if out_table_path is None:
        pass
    elif not isinstance(out_table_path, str):
        raise ValueError("out_table_path must be a string")

    # CHECK if out_x_field == out_y_field
    if out_x_field == out_y_field:
        raise ValueError("out_x_field same as out_y_field")
    
    # CHECK if out_x_field is valid
    if not isinstance(out_x_field, str):
        raise ValueError("out_x_field must be a string")
    
    # CHECK if out_y_field is valid
    if not isinstance(out_y_field, str):
        raise ValueError("out_y_field must be a string")
    
    # CHECK if out_crs is valid
    out_crs = parse_crs(out_crs)

    # PROCESS XYTableToPoint工具將csv轉成shp
    df = XYTableToPoint(
        in_table=df, 
        out_feature_class=None, 
        x_field=in_x_field,
        y_field=in_y_field,
        coordinate_system=in_crs
        )

    # PROCESS 將他投影成經緯度座標系統
    df = Project(
        in_dataset=df,
        out_dataset=None,
        out_coor_system=out_crs
        )

    # PROCESS 將geometry欄位轉成x、y欄位，並刪除geometry欄位
    df[out_x_field] = df['geometry'].x
    df[out_y_field] = df['geometry'].y
    df.drop(columns=['geometry'], inplace=True)

    # SAVE 將轉換過的表格儲存成csv
    if out_table_path is None:
        pass
    elif out_table_path == in_table_path:
        # print warning message in yellow color text style
        print('\033[33m' + 'Warning: The output table path is the same as the input table path. Are you sure you want to overwrite? (Y/n)' + '\033[0m')
        save_even_path_is_same = input() == "Y"
        if save_even_path_is_same: 
            df.to_csv(out_table_path, index=False)
        else: 
            raise Exception('The original file will not be overwritten.')
    else:
        df.to_csv(out_table_path, index=False)

    return df