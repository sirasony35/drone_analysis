# -*- coding: utf-8 -*-
import os
import sys

# --- 1. 사용자 설정 부분 ---
# ★★★ 새로 설치한 QGIS 경로로 수정해주세요 ★★★
QGIS_INSTALL_PATH = 'C:/Program Files/QGIS 3.40.10'  # 예시 경로

INPUT_GEOTIFF_PATH = 'data/GJW1_02_250313_BNVI.tif'
OUTPUT_PNG_PATH = 'result/GJW1_02_250313_BNVI.png'
OUTPUT_WIDTH_PX = 1200
# -------------------------

print("스크립트 실행 시작...")

# --- 2. QGIS 환경 설정 ---
# 이 부분은 자동으로 경로를 설정하므로 수정할 필요 없습니다.
py_path = os.path.join(QGIS_INSTALL_PATH, 'apps/qgis-ltr/python')
if os.path.isdir(py_path):  # 일반적인 설치 경로
    sys.path.append(py_path)
else:  # 다른 종류의 설치 경로
    sys.path.append(os.path.join(QGIS_INSTALL_PATH, 'apps/qgis/python'))

sys.path.append(os.path.join(QGIS_INSTALL_PATH, 'apps/qgis-ltr/python/plugins'))
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(QGIS_INSTALL_PATH, 'apps/Qt5/plugins')
os.environ['QT_PLUGIN_PATH'] = os.path.join(QGIS_INSTALL_PATH, 'apps/qgis-ltr/qtplugins')

from qgis.core import (
    QgsApplication, QgsProject, QgsRasterLayer,
    QgsSingleBandPseudoColorRenderer, QgsColorRampShader, QgsRasterShader,
    QgsMapSettings, QgsRectangle,
    QgsMapRendererParallelJob # 이 위치에 있어야 합니다.
)
# from qgis.gui import QgsMapRendererParallelJob # 이 줄은 삭제합니다.
from PyQt5.QtCore import QSize, QEventLoop
from PyQt5.QtGui import QColor, QImage

qgs = QgsApplication([], False)
qgs.initQgis()
print("QGIS 환경 설정 완료.")

try:
    project = QgsProject.instance()

    # --- 3. GeoTIFF 파일 로드 및 스타일링 ---
    print(f"GeoTIFF 파일 로드 중: {INPUT_GEOTIFF_PATH}")
    raster_layer = QgsRasterLayer(INPUT_GEOTIFF_PATH, 'bnvi_layer')
    if not raster_layer.isValid():
        raise IOError("에러: GeoTIFF 파일을 QGIS 레이어로 불러오는 데 실패했습니다.")
    print("레이어 로드 성공.")

    project.setCrs(raster_layer.crs())
    project.addMapLayer(raster_layer)

    provider = raster_layer.dataProvider()
    stats = provider.bandStatistics(1)
    max_value = stats.maximumValue

    print("심볼 스타일링 시작...")
    color_map = [
        (0.20, QColor('#c51f1e'), '<= 0.20'),        # 진한 빨강
        (0.40, QColor('#f5a361'), '0.20 - 0.40'),    # 밝은 주황
        (0.55, QColor('#faf7be'), '0.40 - 0.55'),    # 옅은 노랑
        (0.70, QColor('#a1d193'), '0.55 - 0.70'),    # 차분한 초록
        (max_value, QColor('#447cb9'), '> 0.70')    # 차분한 파랑
    ]
    qgis_color_ramp_list = [QgsColorRampShader.ColorRampItem(v, c, l) for v, c, l in color_map]
    color_ramp_shader = QgsColorRampShader()
    color_ramp_shader.setColorRampType(QgsColorRampShader.Discrete)
    color_ramp_shader.setColorRampItemList(qgis_color_ramp_list)
    raster_shader = QgsRasterShader()
    raster_shader.setRasterShaderFunction(color_ramp_shader)
    renderer = QgsSingleBandPseudoColorRenderer(provider, 1, raster_shader)
    raster_layer.setRenderer(renderer)
    print("심볼 스타일링 완료.")

    # --- 4. PNG 파일로 직접 내보내기 ---
    print("이미지 직접 렌더링 시작...")
    extent = raster_layer.extent()
    output_height = int(OUTPUT_WIDTH_PX * extent.height() / extent.width())

    settings = QgsMapSettings()
    settings.setLayers([raster_layer])
    settings.setExtent(extent)
    settings.setOutputSize(QSize(OUTPUT_WIDTH_PX, output_height))
    settings.setBackgroundColor(QColor(255, 255, 255, 0))

    job = QgsMapRendererParallelJob(settings)

    loop = QEventLoop()
    job.finished.connect(loop.quit)
    job.start()
    loop.exec_()

    image = job.renderedImage()
    image.save(OUTPUT_PNG_PATH, "png")

    print(f"성공: PNG 파일이 다음 경로에 저장되었습니다: {OUTPUT_PNG_PATH}")

except Exception as e:
    print(f"\n!!! 스크립트 실행 중 오류가 발생했습니다 !!!")
    print(e)
finally:
    qgs.exitQgis()
    print("스크립트 실행 종료.")