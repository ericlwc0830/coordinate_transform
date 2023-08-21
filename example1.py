# 將專案檔的資料夾（./）加入為暫時的環境變數
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/lib")

# 引入寫好的函式
from coordinate_transform import coordinate_transform

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
