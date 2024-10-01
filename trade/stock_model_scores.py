import pandas as pd
import pandas_ta as ta
from db_connection import get_db_connection

def calculate_indicators(df):
    # 열 이름을 소문자로 변환하여 일관성 확보
    df.columns = [col.lower() for col in df.columns]

    # 'trading_date' 열이 있는지 확인
    if 'trading_date' not in df.columns:
        raise KeyError("'trading_date' 열이 데이터프레임에 없습니다.")

    # 날짜 형식 변환 및 정렬
    df['trading_date'] = pd.to_datetime(df['trading_date'], format='%Y%m%d')
    df.sort_values('trading_date', inplace=True)
    df.set_index('trading_date', inplace=True)

    # 데이터 타입 변환
    df = df.astype({
        'closing_price': 'float',
        'opening_price': 'float',
        'high_price': 'float',
        'low_price': 'float',
        'trading_volume': 'float'
    })

    # 기술 지표 계산
    df['RSI'] = ta.rsi(df['closing_price'], length=14)
    macd = ta.macd(df['closing_price'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    stoch = ta.stoch(df['high_price'], df['low_price'], df['closing_price'])
    df['Stochastic_K'] = stoch['STOCHk_14_3_3']
    df['Stochastic_D'] = stoch['STOCHd_14_3_3']
    df['CCI'] = ta.cci(df['high_price'], df['low_price'], df['closing_price'], length=20)
    adx = ta.adx(df['high_price'], df['low_price'], df['closing_price'])
    df['ADX'] = adx['ADX_14']
    df['Momentum'] = ta.mom(df['closing_price'], length=10)
    df['OBV'] = ta.obv(df['closing_price'], df['trading_volume'])
    df['MA5'] = df['closing_price'].rolling(window=5).mean()
    df['MA20'] = df['closing_price'].rolling(window=20).mean()
    bb = ta.bbands(df['closing_price'], length=20, std=2)
    df['BB_upper'] = bb['BBU_20_2.0']
    df['BB_middle'] = bb['BBM_20_2.0']
    df['BB_lower'] = bb['BBL_20_2.0']

    # Ichimoku Cloud 계산 (closing_price 추가)
    ichimoku = ta.ichimoku(df['high_price'], df['low_price'], df['closing_price'])
    if isinstance(ichimoku, pd.DataFrame):
        df['Tenkan_sen'] = ichimoku['ITS_9']
        df['Kijun_sen'] = ichimoku['IKS_26']
    elif isinstance(ichimoku, tuple):
        df['Tenkan_sen'] = ichimoku[0]['ITS_9']
        df['Kijun_sen'] = ichimoku[0]['IKS_26']
    else:
        raise TypeError("ta.ichimoku 반환값의 타입을 확인하세요.")

    # VWAP 계산
    df['VWAP'] = ta.vwap(df['high_price'], df['low_price'], df['closing_price'], df['trading_volume'])

    # Price Channel 계산
    df['Price_Channel_High'] = df['high_price'].rolling(window=20).max()
    df['Price_Channel_Low'] = df['low_price'].rolling(window=20).min()

    return df


def calculate_scores(df):
    # 각 지표를 0에서 1 사이의 값으로 스케일링하여 동일한 비중으로 점수화
    scores = {}

    # MA 점수 (개선된 방식)
    ma_diff = df['MA5'].iloc[-1] - df['MA20'].iloc[-1]
    scores['ma_score'] = (ma_diff / df['MA20'].iloc[-1]) if df['MA20'].iloc[-1] != 0 else 0

    # RSI 점수 (개선된 방식)
    rsi = df['RSI'].iloc[-1]
    if rsi >= 70:
        scores['rsi_score'] = 0  # 과매수
    elif rsi <= 30:
        scores['rsi_score'] = 1  # 과매도
    else:
        scores['rsi_score'] = (70 - rsi) / 40  # 중립 구간

    # 볼린저 밴드 점수 (개선된 방식)
    close = df['closing_price'].iloc[-1]
    lower = df['BB_lower'].iloc[-1]
    upper = df['BB_upper'].iloc[-1]
    middle = df['BB_middle'].iloc[-1]
    if close < lower:
        scores['bb_score'] = 1  # 매수 신호
    elif close > upper:
        scores['bb_score'] = 0  # 매도 신호
    else:
        scores['bb_score'] = (upper - close) / (upper - lower)  # 중립

    # MACD 점수 (개선된 방식)
    macd = df['MACD'].iloc[-1]
    macd_signal = df['MACD_signal'].iloc[-1]
    macd_diff = macd - macd_signal
    scores['macd_score'] = macd_diff / abs(macd_signal) if abs(macd_signal) != 0 else 0

    # 스토캐스틱 점수 (개선된 방식)
    stoch_k = df['Stochastic_K'].iloc[-1]
    stoch_d = df['Stochastic_D'].iloc[-1]
    stoch_diff = stoch_k - stoch_d
    scores['stochastic_score'] = stoch_diff / 100

    # ADX 점수 (개선된 방식)
    adx = df['ADX'].iloc[-1]
    scores['adx_score'] = adx / 50  # 추세 강도는 0~50으로 제한 (50 이상은 매우 강한 추세)

    # CCI 점수 (개선된 방식)
    cci = df['CCI'].iloc[-1]
    scores['cci_score'] = (cci + 100) / 200 if -100 <= cci <= 100 else 0

    # 모멘텀 점수 (개선된 방식)
    momentum = df['Momentum'].iloc[-1]
    max_mom = df['Momentum'].abs().max()
    scores['momentum_score'] = (momentum + max_mom) / (2 * max_mom) if max_mom != 0 else 0

    # OBV 점수 (개선된 방식)
    obv = df['OBV'].iloc[-1]
    obv_prev = df['OBV'].iloc[-2] if len(df['OBV']) > 1 else obv
    obv_diff = obv - obv_prev
    scores['obv_score'] = obv_diff / abs(obv_prev) if abs(obv_prev) != 0 else 0

    # 일목균형표 점수 (개선된 방식)
    tenkan = df['Tenkan_sen'].iloc[-1]
    kijun = df['Kijun_sen'].iloc[-1]
    scores['ichimoku_score'] = (tenkan - kijun) / abs(kijun) if abs(kijun) != 0 else 0

    # VWAP 점수 (개선된 방식)
    vwap = df['VWAP'].iloc[-1]
    scores['vwap_score'] = (close - vwap) / abs(vwap) if abs(vwap) != 0 else 0

    # 가격 채널 점수 (개선된 방식)
    price_channel_high = df['Price_Channel_High'].iloc[-1]
    price_channel_low = df['Price_Channel_Low'].iloc[-1]
    scores['price_channel_score'] = (close - price_channel_low) / (price_channel_high - price_channel_low) if (price_channel_high - price_channel_low) != 0 else 0

    return scores

# stock_model_scores.py

def main():
    connection = get_db_connection()
    cursor = connection.cursor()

    # 종목 리스트 가져오기
    cursor.execute("SELECT DISTINCT stock_code FROM DAILY_STOCK_PRICE")
    tickers = [row[0] for row in cursor.fetchall()]

    for ticker in tickers:
        query = f"""
        SELECT
            stock_code,
            opening_price,
            high_price,
            low_price,
            closing_price,
            trading_volume,
            trading_date
        FROM DAILY_STOCK_PRICE
        WHERE stock_code = :ticker
        ORDER BY trading_date
        """
        df = pd.read_sql(query, con=connection, params={'ticker': ticker})

        # 열 이름을 소문자로 변환
        df.columns = [col.lower() for col in df.columns]

        # 'trading_date' 열이 있는지 확인
        if 'trading_date' not in df.columns:
            print(f"'trading_date' 열이 {ticker} 종목의 데이터에 없습니다.")
            continue

        if df.empty or len(df) < 30:
            continue

        try:
            # 기술 지표 및 점수 계산
            df = calculate_indicators(df)
            scores = calculate_scores(df)

            # 데이터베이스에 점수 저장
            insert_sql = """
            MERGE INTO STOCK_MODEL_SCORES T
            USING (SELECT :stock_code AS stock_code, :trading_date AS trading_date FROM dual) S
            ON (T.stock_code = S.stock_code AND T.trading_date = S.trading_date)
            WHEN MATCHED THEN
                UPDATE SET
                    ma_score = :ma_score,
                    rsi_score = :rsi_score,
                    bb_score = :bb_score,
                    macd_score = :macd_score,
                    stochastic_score = :stochastic_score,
                    adx_score = :adx_score,
                    cci_score = :cci_score,
                    momentum_score = :momentum_score,
                    obv_score = :obv_score,
                    ichimoku_score = :ichimoku_score,
                    vwap_score = :vwap_score,
                    price_channel_score = :price_channel_score
            WHEN NOT MATCHED THEN
                INSERT (stock_code, trading_date, ma_score, rsi_score, bb_score, macd_score, stochastic_score,
                        adx_score, cci_score, momentum_score, obv_score, ichimoku_score, vwap_score, price_channel_score)
                VALUES (:stock_code, :trading_date, :ma_score, :rsi_score, :bb_score, :macd_score, :stochastic_score,
                        :adx_score, :cci_score, :momentum_score, :obv_score, :ichimoku_score, :vwap_score, :price_channel_score)
            """

            data = {
                'stock_code': ticker,
                'trading_date': df.index[-1].strftime('%Y%m%d'),
                'ma_score': str(scores['ma_score']),
                'rsi_score': str(scores['rsi_score']),
                'bb_score': str(scores['bb_score']),
                'macd_score': str(scores['macd_score']),
                'stochastic_score': str(scores['stochastic_score']),
                'adx_score': str(scores['adx_score']),
                'cci_score': str(scores['cci_score']),
                'momentum_score': str(scores['momentum_score']),
                'obv_score': str(scores['obv_score']),
                'ichimoku_score': str(scores['ichimoku_score']),
                'vwap_score': str(scores['vwap_score']),
                'price_channel_score': str(scores['price_channel_score'])
            }

            cursor.execute(insert_sql, data)
            connection.commit()

        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
            continue

    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
