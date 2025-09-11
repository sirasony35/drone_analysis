# -*- coding: utf-8 -*-
import os
import glob
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. 사용자 설정 부분 ---
# 이전 스크립트(zonal_statistics.py)의 결과 폴더를 입력합니다.
GEOJSON_FOLDER = 'result_geojson'


# -------------------------

def main():
    """메인 실행 함수"""
    print("그래프 생성 스크립트 실행 시작...")

    # 1. 모든 GeoJSON 파일 목록 가져와서 하나의 DataFrame으로 합치기
    geojson_files = glob.glob(os.path.join(GEOJSON_FOLDER, '*_zonal_stats.geojson'))
    if not geojson_files:
        print(f"[오류] GeoJSON 결과 폴더에 파일이 없습니다: {GEOJSON_FOLDER}")
        return

    gdf_list = [gpd.read_file(f) for f in geojson_files]
    full_df = pd.concat(gdf_list, ignore_index=True)

    # 'no' 컬럼을 기준으로 정렬하여 그래프의 X축 순서를 맞춥니다.
    full_df = full_df.sort_values(by='no').reset_index(drop=True)

    print(f"총 {len(geojson_files)}개 파일, {len(full_df)}개 레코드(구역)를 성공적으로 불러왔습니다.")

    # 2. 그래프를 생성할 식생 지수 목록 정의
    index_names = ['BNVI', 'NDVI', 'GNDVI', 'LCI', 'MTCI', 'NDRE']

    # 3. 각 식생 지수별로 별도의 그래프 생성
    for index_name in index_names:
        print(f"\n--- '{index_name}' 그래프 생성 중... ---")

        # Y축 3개를 사용하기 위해 서브플롯 스펙 설정
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # A. 왼쪽 Y축: 식생 지수 1~6회차 라인 추가
        for i in range(1, 7):
            column_name = f"{index_name}_{i}"
            fig.add_trace(
                go.Scatter(x=full_df['code'], y=full_df[column_name], name=column_name),
                secondary_y=False
            )

        # B. 오른쪽 Y축 1: 수확량(yield) 라인 추가
        fig.add_trace(
            go.Scatter(x=full_df['code'], y=full_df['yield'], name='수확량',
                       line=dict(color='black', dash='dash')),
            secondary_y=True
        )

        # C. 오른쪽 Y축 2: 단백질(protein) 라인 추가 (수동으로 세 번째 Y축 생성)
        fig.add_trace(
            go.Scatter(x=full_df['code'], y=full_df['protein'], name='단백질', yaxis='y3',
                       line=dict(color='grey', dash='dot'))
        )

        # D. 그래프 레이아웃 및 축 설정
        fig.update_layout(
            title_text=f"<b>{index_name} 시계열 변화와 수확량/단백질 관계</b>",
            xaxis_title="구역",
            legend_title="데이터",
            # 왼쪽 Y축 (기본)
            yaxis=dict(
                title=f"{index_name} 값"
            ),
            # 오른쪽 Y축 1 (수확량)
            yaxis2=dict(
                title="<b>수확량</b>",
                side='right',
                anchor="x",
                overlaying="y",
            ),
            # 오른쪽 Y축 2 (단백질) - 수동 생성
            yaxis3=dict(
                title="<b>단백질</b>",
                side='right',
                anchor="free",  # 다른 축에 고정되지 않음
                overlaying="y",
                position=1.0  # 오른쪽 끝에 위치
            )
        )

        # 오른쪽 두 축의 제목이 겹치지 않도록 조정
        fig.update_yaxes(title_font=dict(color="black"), secondary_y=True)
        fig.update_yaxes(title_font=dict(color="grey"), secondary_y=False)  # 왼쪽 축 제목 색상 변경으로 구분감 부여

        # 4. 대화형 HTML 파일로 그래프 저장
        output_filename = f"result_graph/{index_name}_graph.html"
        fig.write_html(output_filename)
        print(f"   [성공] 그래프가 '{output_filename}' 파일로 저장되었습니다.")

    print("\n--- 모든 그래프 생성이 완료되었습니다. ---")


if __name__ == '__main__':
    main()