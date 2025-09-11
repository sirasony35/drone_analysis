# -*- coding: utf-8 -*-
import os
import glob
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.crs import CRS
import shutil

# --- 1. 사용자 설정 부분 ---
INPUT_RASTER_FOLDER = 'drone_data'
OUTPUT_RASTER_FOLDER = 'drone_data_reprojected_5179'

TARGET_CRS_STRING = 'EPSG:5179'


# -------------------------

def main():
    """메인 실행 함수"""
    print("래스터 좌표계 변환 스크립트 실행 시작...")

    if not os.path.exists(OUTPUT_RASTER_FOLDER):
        os.makedirs(OUTPUT_RASTER_FOLDER)
        print(f"출력 폴더 생성: {OUTPUT_RASTER_FOLDER}")

    raster_files = glob.glob(os.path.join(INPUT_RASTER_FOLDER, '*.tif'))

    if not raster_files:
        print(f"[오류] 입력 폴더에 TIF 파일이 없습니다: {INPUT_RASTER_FOLDER}")
        return

    print(f"\n총 {len(raster_files)}개의 파일을 확인합니다.")

    # 목표 CRS의 EPSG 코드(숫자)를 미리 추출
    try:
        target_epsg_code = CRS.from_string(TARGET_CRS_STRING).to_epsg()
    except Exception as e:
        print(f"[오류] 목표 CRS '{TARGET_CRS_STRING}'를 해석할 수 없습니다: {e}")
        return

    for raster_path in raster_files:
        filename = os.path.basename(raster_path)
        output_path = os.path.join(OUTPUT_RASTER_FOLDER, filename)

        with rasterio.open(raster_path) as src:
            source_crs = src.crs

            # === ★★★ 수정된 부분: EPSG 코드(숫자)로 직접 비교 ★★★ ===
            source_epsg_code = None
            if source_crs:
                try:
                    source_epsg_code = source_crs.to_epsg()
                except:
                    # EPSG 코드를 추출할 수 없는 경우, 다르다고 간주
                    pass

            print(f"-> 확인 중: {filename} (감지된 EPSG 코드: {source_epsg_code})")

            # EPSG 코드가 다르거나, 소스 코드 인식이 불가능한 경우에만 변환 수행
            if source_epsg_code != target_epsg_code:
                print(f"   [변환 필요] 좌표계를 {TARGET_CRS_STRING}로 재투영합니다...")

                target_crs_object = CRS.from_string(TARGET_CRS_STRING)
                transform, width, height = calculate_default_transform(
                    source_crs, target_crs_object, src.width, src.height, *src.bounds)

                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': target_crs_object,
                    'transform': transform,
                    'width': width,
                    'height': height
                })

                with rasterio.open(output_path, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs_object,
                            resampling=Resampling.nearest)
                print(f"   [성공] 변환된 파일 저장 완료: {filename}")
            else:
                print("   [통과] EPSG 코드가 이미 올바릅니다. 파일을 복사합니다.")
                shutil.copy(raster_path, output_path)

    print("\n--- 모든 래스터 파일 처리가 완료되었습니다. ---")


if __name__ == '__main__':
    main()