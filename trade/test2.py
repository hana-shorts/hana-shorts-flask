from pykrx import stock
import pandas as pd

# 주식 티커 리스트
tickers = [
    "064850",
    "036560",
    "007340",
    "078140",
    "310210",
    "354200",
    "119650",
    "089790",
    "119830",
    "006740"
]

# 기준 날짜와 종료 날짜 설정
base_date = "20240925"
start_date = "20240926"  # 최저 저가 계산 시작 날짜
end_date = "20241011"

# 결과를 저장할 리스트 초기화
results = []

for ticker in tickers:
    try:
        # 해당 티커의 OHLCV 데이터 가져오기
        df = stock.get_market_ohlcv(base_date, end_date, ticker)

        # 데이터프레임의 인덱스를 문자열 형식으로 변환 (필요 시)
        df.index = df.index.strftime('%Y%m%d')

        # 기준 날짜의 종가 확인
        if base_date not in df.index:
            print(f"티커 {ticker}의 기준 날짜 {base_date} 데이터가 없습니다. 건너뜁니다.")
            continue
        base_close = df.loc[base_date, '종가']

        # 기간 내 최저 저가 계산 (기준 날짜 제외)
        df_min = df.loc[start_date:end_date]
        if df_min.empty:
            print(f"티커 {ticker}의 {start_date}부터 {end_date}까지 데이터가 없습니다. 건너뜁니다.")
            continue

        # 저가가 0이 아닌 값들만 필터링
        df_min_filtered = df_min[df_min['저가'] > 0]

        if df_min_filtered.empty:
            print(f"티커 {ticker}의 {start_date}부터 {end_date}까지의 저가가 모두 0입니다. 건너뜁니다.")
            continue

        min_low = df_min_filtered['저가'].min()
        min_return = ((min_low - base_close) / base_close) * 100

        # 종료 날짜의 종가 확인
        if end_date in df.index:
            end_close = df.loc[end_date, '종가']
            end_return = ((end_close - base_close) / base_close) * 100
        else:
            print(f"티커 {ticker}의 종료 날짜 {end_date} 데이터가 없습니다. 수익률 계산 불가.")
            end_close = None
            end_return = None

        # 결과 저장
        results.append({
            '티커': ticker,
            '기준 종가': base_close,
            '기간 내 최저 저가': min_low,
            '최저 수익률 (%)': round(min_return, 2),
            '2024-10-11 종가': end_close if end_close is not None else 'N/A',
            '2024-10-11 수익률 (%)': round(end_return, 2) if end_return is not None else 'N/A'
        })

    except Exception as e:
        print(f"티커 {ticker} 처리 중 오류 발생: {e}")
        continue

# 결과를 데이터프레임으로 변환
results_df = pd.DataFrame(results)

# 결과 출력
print(results_df)
