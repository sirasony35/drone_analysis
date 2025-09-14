# -*- coding: utf-8 -*-
import os
import glob
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. 사용자 설정 부분 ---
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

    # 'no' 또는 'code' 컬럼을 기준으로 정렬합니다. (파일에 있는 컬럼명 사용)
    sort_column = 'code'
    full_df = full_df.sort_values(by=sort_column).reset_index(drop=True)
    x_axis_data = full_df[sort_column]

    print(f"총 {len(geojson_files)}개 파일, {len(full_df)}개 레코드(구역)를 성공적으로 불러왔습니다.")

    # 2. 그래프를 생성할 식생 지수 목록 정의
    index_names = ['BNVI', 'NDVI', 'GNDVI', 'LCI', 'MTCI', 'NDRE']

    # 3. 각 식생 지수별로 별도의 그래프 생성
    for index_name in index_names:
        print(f"\n--- '{index_name}' 그래프 생성 중... ---")
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # A. 왼쪽 Y축: 식생 지수 1~6회차 라인 추가
        for i in range(1, 7):
            column_name = f"{index_name}_{i}"
            fig.add_trace(
                go.Scatter(x=x_axis_data, y=full_df[column_name], name=column_name),
                secondary_y=False
            )

        # B. 오른쪽 Y축 1: 수확량(yield) 막대그래프 추가
        fig.add_trace(
            go.Bar(x=x_axis_data, y=full_df['yield'], name='수확량',
                   marker_color='rgba(150, 150, 150, 0.6)'),  # 수확량 색상을 회색 계열로 변경
            secondary_y=True
        )

        # C. 오른쪽 Y축 2: 단백질(protein) 막대그래프 추가 (Scatter -> Bar 변경)
        # ★★★ 수정된 부분: secondary_y=False 옵션 제거 ★★★
        fig.add_trace(
            go.Bar(x=x_axis_data, y=full_df['protein'], name='단백질', yaxis='y3',
                   marker_color='rgba(150, 150, 150, 0.6)')  # 단백질 색상을 회색 계열로 변경
        )

        # D. 그래프 레이아웃 및 축 설정
        fig.update_layout(
            title_text=f"<b>{index_name} 시계열 변화와 수확량/단백질 관계</b>",
            xaxis_title=f"구역 ID ({sort_column})",
            legend_title="데이터",
            barmode='overlay',
            yaxis=dict(
                title=f"{index_name} 값"
            ),
            yaxis2=dict(
                title="<b>수확량</b>",
                side='right'
            ),
            yaxis3=dict(
                title="<b>단백질</b>",
                side='right',
                anchor="free",
                overlaying="y",
                position=1.0
            )
        )
        fig.update_traces(opacity=0.7, selector=dict(type="bar"))

        # 4. 대화형 HTML과 PNG 이미지로 그래프 저장
        output_folder = "result_graph"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_html = os.path.join(output_folder, f"{index_name}_graph.html")
        output_png = os.path.join(output_folder, f"{index_name}_graph.png")

        fig.write_html(output_html)
        print(f"   [성공] HTML 그래프가 '{output_html}' 파일로 저장되었습니다.")

        fig.write_image(output_png, width=1200, height=700, scale=2)
        print(f"   [성공] 이미지 파일이 '{output_png}' 파일로 저장되었습니다.")

    print("\n--- 모든 그래프 생성이 완료되었습니다. ---")


if __name__ == '__main__':
    main()