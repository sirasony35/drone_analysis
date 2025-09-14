# -*- coding: utf-8 -*-
import os
import glob
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# --- 1. 사용자 설정 부분 ---
INPUT_FOLDER = 'drone_data'
OUTPUT_FOLDER = 'result_histogram'


# -------------------------

def create_raster_histogram(raster_path, output_path):
    """단일 래스터 파일의 히스토그램을 생성하고 상위 2개의 최빈값을 표시하여 이미지 파일로 저장합니다."""
    print(f"-> 처리 중: {os.path.basename(raster_path)}")
    try:
        # 1. Rasterio를 사용하여 래스터 파일 열기
        with rasterio.open(raster_path) as src:
            image_data = src.read(1)
            nodata_value = src.nodata

        # 2. 데이터 정제: 유효한 픽셀 값만 추출
        if nodata_value is not None:
            valid_data = image_data[image_data != nodata_value].flatten()
        else:
            valid_data = image_data.flatten()

        valid_data = valid_data[(valid_data > -2) & (valid_data < 5)]

        if valid_data.size < 2:  # 데이터가 2개 미만이면 통계 계산 불가
            print("   [경고] 분석할 유효한 데이터가 부족합니다. 건너<binary data, 2 bytes><binary data, 2 bytes><binary data, 2 bytes>니다.")
            return

        # 3. Matplotlib를 사용하여 히스토그램 생성
        fig, ax = plt.subplots(figsize=(12, 7))

        # === ★★★ 변경된 부분 1: 상위 2개 최빈값(Peak) 계산 ★★★ ===
        counts, bin_edges = np.histogram(valid_data, bins=256)

        # 빈도수(counts)를 기준으로 내림차순 정렬된 인덱스를 가져옴
        sorted_indices = np.argsort(counts)[::-1]

        # 1위 최빈값 계산
        peak1_index = sorted_indices[0]
        peak1_value = (bin_edges[peak1_index] + bin_edges[peak1_index + 1]) / 2
        peak1_count = counts[peak1_index]
        print(f"   [정보] 1st Peak: {peak1_value:.4f}, 빈도수: {peak1_count}")

        # 2위 최빈값 계산
        peak2_index = sorted_indices[1]
        peak2_value = (bin_edges[peak2_index] + bin_edges[peak2_index + 1]) / 2
        peak2_count = counts[peak2_index]
        print(f"   [정보] 2nd Peak: {peak2_value:.4f}, 빈도수: {peak2_count}")

        # 기존 히스토그램 그리기
        ax.hist(valid_data, bins=256, color='skyblue', edgecolor='black')

        # === ★★★ 변경된 부분 2: 계산된 최빈값들 그래프에 표시 ★★★ ===
        # 1위 최빈값 표시 (빨간색)
        ax.axvline(peak1_value, color='red', linestyle='--', linewidth=2, label=f'1st Peak: {peak1_value:.4f}')
        ax.text(peak1_value, peak1_count, f' 1st Peak\n {peak1_value:.4f}',
                color='red', ha='left', va='bottom', fontsize=12, weight='bold')

        # 2위 최빈값 표시 (보라색)
        ax.axvline(peak2_value, color='purple', linestyle=':', linewidth=2, label=f'2nd Peak: {peak2_value:.4f}')
        ax.text(peak2_value, peak2_count, f' 2nd Peak\n {peak2_value:.4f}',
                color='purple', ha='right', va='bottom', fontsize=12, weight='bold')

        # 그래프 제목 및 축 레이블 설정
        ax.set_title(f'{os.path.basename(raster_path)} - Pixel Value Distribution', fontsize=16)
        ax.set_xlabel('Vegetation Index Value', fontsize=12)
        ax.set_ylabel('Pixel Count (Frequency)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

        # 4. 생성된 그래프를 이미지 파일로 저장
        plt.savefig(output_path, dpi=150)
        plt.close(fig)

    except Exception as e:
        print(f"   [오류] 처리 중 문제가 발생했습니다: {e}")


def main():
    """메인 실행 함수"""

    # === ★★★ 수정된 부분: 스크립트 실행 동안 GDAL 환경 설정 적용 ★★★ ===
    with rasterio.Env(GTIFF_SRS_SOURCE='EPSG'):
        print("히스토그램 일괄 생성 스크립트 실행 시작...")

        # 한글 폰트 설정 (Windows 기준)
        try:
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
        except:
            print("[경고] 'Malgun Gothic' 폰트를 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")

        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
            print(f"출력 폴더 생성: {OUTPUT_FOLDER}")

        raster_files = glob.glob(os.path.join(INPUT_FOLDER, '*.tif'))
        if not raster_files:
            print(f"[오류] 입력 폴더에 TIF 파일이 없습니다: {INPUT_FOLDER}")
            return

        print(f"\n총 {len(raster_files)}개의 파일에 대한 히스토그램을 생성합니다.")

        for raster_path in raster_files:
            base_name = os.path.splitext(os.path.basename(raster_path))[0]
            output_filename = f"{base_name}_histogram.png"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            create_raster_histogram(raster_path, output_path)

        print("\n--- 모든 작업이 완료되었습니다. ---")
        print(f"결과물은 '{OUTPUT_FOLDER}' 폴더에 저장되었습니다.")


if __name__ == '__main__':
    main()