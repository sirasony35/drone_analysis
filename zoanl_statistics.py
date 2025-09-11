# -*- coding: utf-8 -*-
import os
import sys
import glob
import geopandas as gpd
from rasterstats import zonal_stats

# --- 1. 사용자 설정 부분 ---
GEOJSON_FOLDER = 'geo_json_data'
RASTER_FOLDER = 'drone_data_reprojected_5179'

# 최종 결과 GeoJSON 파일이 저장될 폴더 경로
OUTPUT_FOLDER = 'result_geojson'


# -------------------------

def main():
    """메인 실행 함수"""
    print("일괄 처리 스크립트 실행 시작...")

    # 결과 폴더가 없으면 생성
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"출력 폴더 생성: {OUTPUT_FOLDER}")

    # 1. 모든 GeoJSON 파일 목록 가져오기
    geojson_files = glob.glob(os.path.join(GEOJSON_FOLDER, '*.geojson'))

    if not geojson_files:
        print(f"[오류] GeoJSON 입력 폴더에 파일이 없습니다: {GEOJSON_FOLDER}")
        return

    print(f"\n총 {len(geojson_files)}개의 GeoJSON 파일을 처리합니다.")

    # 2. 각 GeoJSON 파일에 대해 반복 작업 수행
    for geojson_path in geojson_files:
        print(f"\n--- 처리 중인 파일: {os.path.basename(geojson_path)} ---")

        # GeoJSON 파일을 GeoDataFrame으로 읽기
        gdf = gpd.read_file(geojson_path)

        # GeoJSON 파일명에서 필드 ID 추출 (예: 'wheat_yield_GJ-W1.geojson' -> 'GJW1')
        base_name = os.path.splitext(os.path.basename(geojson_path))[0]
        field_id = base_name.split('_')[-1].replace('-', '')
        print(f"필드명: {field_id}")

        # 3. 해당 필드 ID에 맞는 모든 래스터 파일 찾기 (예: GJW1*.tif)
        raster_search_path = os.path.join(RASTER_FOLDER, f'{field_id}*.tif')
        raster_files = glob.glob(raster_search_path)

        if not raster_files:
            print(f"   [경고] '{field_id}'에 해당하는 래스터 파일을 찾을 수 없습니다. 건너<binary data, 2 bytes>니다.")
            continue  # 다음 GeoJSON 파일로 넘어감

        print(f"   > 총 {len(raster_files)}개의 연관 래스터 파일을 찾았습니다. 구역 통계를 시작합니다.")

        # 4. 찾은 래스터 파일들을 하나씩 처리
        for raster_path in sorted(raster_files):
            raster_filename = os.path.basename(raster_path)
            try:
                # 래스터 파일명에서 식생 지수와 회차 정보 추출
                parts = raster_filename.split('_')
                session = int(parts[1])
                index_name = parts[3].split('.')[0]

                # 새로운 컬럼 이름 생성 (예: 'BNVI_1')
                column_name = f"{index_name}_{session}"

                print(f"     - 계산 중: {raster_filename} -> '{column_name}' 컬럼")

                # 핵심 기능: zonal_stats로 구역별 평균 통계 계산
                stats = zonal_stats(gdf, raster_path, stats="mean")
                print(f"{column_name}의 구역통계 {stats}")

                # 결과에서 평균값만 추출하여 리스트로 만듦
                mean_values = [s['mean'] for s in stats]
                print(f"{column_name}의 구역통계 {mean_values}")

                # GeoDataFrame에 새로운 컬럼으로 추가
                gdf[column_name] = mean_values

            except Exception as e:
                print(f"     [오류] '{raster_filename}' 처리 중 문제 발생: {e}")

        # 5. 모든 래스터 처리가 끝난 후, 결과 GeoJSON 파일 저장
        base_name_with_ext = os.path.basename(geojson_path)
        name_part, extension = os.path.splitext(base_name_with_ext)

        # 파일명에 _zonal_stats 추가
        new_output_filename = f"{name_part}_zonal_stats{extension}"

        output_path = os.path.join(OUTPUT_FOLDER, new_output_filename)

        gdf.to_file(output_path, driver='GeoJSON', encoding='utf-8')
        print(f"   [성공] 최종 결과 파일 저장 완료: {new_output_filename}")

    print("\n--- 모든 작업이 완료되었습니다. ---")


if __name__ == '__main__':
    main()