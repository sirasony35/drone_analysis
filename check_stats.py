# check_stats.py
import os, sys, glob

QGIS_INSTALL_PATH = 'C:/Program Files/QGIS 3.40.10' # 사용자의 QGIS 경로
INPUT_FOLDER = 'data'

# --- QGIS 환경 설정 ---
py_path = os.path.join(QGIS_INSTALL_PATH, 'apps/qgis-ltr/python')
if not os.path.isdir(py_path): py_path = os.path.join(QGIS_INSTALL_PATH, 'apps/qgis/python')
sys.path.append(py_path)
from qgis.core import QgsApplication, QgsRasterLayer
qgs = QgsApplication([], False)
qgs.initQgis()

print("--- 각 GeoTIFF 파일의 통계 정보 ---")
search_path = os.path.join(INPUT_FOLDER, '*.tif')
for file_path in glob.glob(search_path):
    layer = QgsRasterLayer(file_path, os.path.basename(file_path))
    if layer.isValid():
        stats = layer.dataProvider().bandStatistics(1)
        print(f"{os.path.basename(file_path):<25} -> Min: {stats.minimumValue:.4f}, Max: {stats.maximumValue:.4f}")

qgs.exitQgis()
print("---------------------------------")