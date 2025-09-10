# -*- coding: utf-8 -*-

import os
import glob
import geopandas as gpd
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ---1. 사용자 설정 부분----
GEOJSON_FOLDER = 'result_geojson'
TARGET_VARIABLES = ['yield', 'protein']

def main():
    print('상관관게 분석 스크립트 실행 시작...')

    #1. 모든 GeoJSON 파일 목록 가져와서 하나의 DataFrame으로 합치기
    geojson_files = glob.glob(os.path.join(GEOJSON_FOLDER, '*_zonal_stats.geojson'))
    if not geojson_files:
        print(f"[오류] GeoJSON 결과 폴더에 파일이 없습니다:{GEOJSON_FOLDER}")
        return

    gdf_list = [gpd.read_file(f) for f in geojson_files]
    full_df = pd.concat(gdf_list, ignore_index=True)
    print(f"총 {len(gdf_list)} 개 파일, {len(full_df)} 개 레코드를 성공적으로 불러왔습니다.")

    #2. 분석에 사용할 컬럼 선택
    # 식생 지수 컬럼 목록을 자동으로 생성
    index_names = ['BNVI', 'GNDVI', 'LCI', 'MTCI', 'NDRE', 'NDVI']
    predictor_variables = [col for col in full_df.columns if col.split('_')[0] in index_names]

    analysis_columns = TARGET_VARIABLES + predictor_variables
    analysis_df = full_df[analysis_columns]

    #3  상관관계 행렬 계산
    print("\n수확량, 단백질과 식생 지수 간의 상관관계를 계산합니다...")
    corr_matrix = analysis_df.corr()

    #4. 결과 출력:  목표 변수와 상관관계가 높은 순서대로 정렬하여 보여주기
    for target in TARGET_VARIABLES:
    # 자기 자신과의 상관관계는 제외하고, 절대값 기준으로 정렬
        sorted_corr = corr_matrix[target].drop(TARGET_VARIABLES).abs().sort_values(ascending=False)
        print(f"\n--- '{target}'와(과) 상관관계가 높은 상위 10개 식생지수 ---")
        print(sorted_corr)

    #5. 결과 시각화: 히트맵으로 저장
    print("\n상관관게 분석 결과를 히트맵 이미지로 저장합니다...")

    # 한글 폰트 설정
    try:
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
    except:
        print("[경고] 'Malgun Gothic' 폰트를 찾을 수 없습니다. 히트맵의 한글이 깨질 수 있습니다.")

    heatmap_data = corr_matrix.loc[TARGET_VARIABLES, predictor_variables]
    plt.figure(figsize=(14, 10))
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
    plt.title('수확량/단백질과 식생 지수의 상관관계', fontsize=16)
    plt.tight_layout()

    output_image_path = 'correlation_heatmap_2.png'
    plt.savefig(output_image_path, dpi=200)
    print(f"[성공] 히트맵이 '{output_image_path}' 파일로 저장되었습니다.")

if __name__ == '__main__':
    main()
