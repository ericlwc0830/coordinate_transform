# **coordinate_transform** (csv table tool)
```python
coordinate_transform(in_table_path, in_x_field, in_y_field, in_crs, out_table_path, out_x_field, out_y_field, out_crs)
```

## 函式說明

將輸入表格中的座標欄位從一個座標系統轉換成另一個座標系統，並新增轉換過的座標欄位至已經帶有舊座標欄位的表格並儲存。

這個功能不會異動原本的資料，除非 in_table_path 與 out_table_path 相同，並經過確認。


## 參數說明
- **in_table_path** (str): 輸入表格的路徑
- **in_x_field** (str): 輸入表格的x座標欄位
- **in_y_field** (str): 輸入表格的y座標欄位
- **in_crs** (int/str/CRS): 輸入表格的座標系統，可以是epsg代碼、wkt字串、prj檔路徑、pyproj.crs.CRS物件
- **out_table_path** (str/None): 輸出表格的路徑，若與in_table_path相同則會覆蓋原本的檔案，若為None則不會儲存
- **out_x_field** (str): 輸出表格的x座標欄位，該欄位若不存在則創建，存在則覆蓋該欄位原本的內容
- **out_y_field** (str): 輸出表格的y座標欄位，該欄位若不存在則創建，存在則覆蓋該欄位原本的內容
- **out_crs** (int/str/CRS): 輸出表格的座標系統，可以是epsg代碼、wkt字串、prj檔路徑、pyproj.crs.CRS物件

## 回傳值
轉換過的padnas.DataFrame

## 使用前準備

1. 將 `./lib` 內的 `coordinate_transform` 資料夾放到你的專案資料夾下的 `lib` 資料夾裡面。

2. 在你的程式碼裡面加入以下程式碼：
    ```python
    # 將專案資料夾加入環境變數
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # import本函式
    from lib.coordinate_transform.coordinate_transform import coordinate_transform
    ```

3. 如此便可使用 `coordinate_transform` 函式了

## 使用範例
1. `example1.py`
    ```python
    # 將資料夾加入環境變數
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # 引入寫好的函式
    from lib.coordinate_transform.coordinate_transform import coordinate_transform

    # 使用函式
    coordinate_transform(
        in_table_path='example1_input.csv',
        in_x_field='x',
        in_y_field='y',
        # 以下的in_crs是以五分山雷達站為中心且以公尺為單位的等距方位座標（極投影）wkt字串
        in_crs="""\
    PROJCS["RCWF_projection",
    GEOGCS["GCS_WGS_1984",
        DATUM["D_WGS_1984",
            SPHEROID["WGS_1984",6378137.0,298.257223563]],
        PRIMEM["Greenwich",0.0],
        UNIT["Degree",0.0174532925199433]],
    PROJECTION["Azimuthal_Equidistant"],
    PARAMETER["False_Easting",0.0],
    PARAMETER["False_Northing",0.0],
    PARAMETER["Central_Meridian",121.7806142],
    PARAMETER["Latitude_Of_Origin",25.071246],
    UNIT["Meter",1.0]]""",
        out_table_path='example1_output.csv',
        out_x_field='lon',
        out_y_field='lat',
        # 以下的out_crs是以WGS1984經緯座標系統的epsg代碼
        out_crs=4326
    )

    # 即可得到新的檔案example_output.csv
    ```

## 作者
ericlwc

## 更新紀錄

2023/07/05 撰寫

2023/08/01 更新
- 刪去對shp暫存檔進行操作的過程，以移除對shp檔格式的依賴
- 針對記憶體效率與儲存效率進行優化
