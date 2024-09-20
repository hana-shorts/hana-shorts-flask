import pandas as pd
from tqdm import tqdm
from datetime import datetime
from pykrx import stock
from db_connection import get_db_connection  # DB 연결 함수 임포트

def get_market_data_for_today():
    """ 오늘 날짜의 영업일 데이터를 가져오는 함수 """
    today = datetime.today()
    today_str = today.strftime("%Y%m%d")

    try:
        # 오늘 날짜의 KOSPI 데이터 가져오기
        df = stock.get_market_ohlcv(today_str, market="KOSPI")
        df['date'] = today_str  # 거래일자 추가
        # 거래량 또는 종가가 0인 데이터는 주말/공휴일일 수 있으므로 제외
        if (df[['거래량', '시가', '고가', '저가', '종가']] == 0).all().any():
            print(f"{today_str}의 데이터는 0값이므로 제외합니다.")
            return None  # 데이터가 0이면 None 반환
        return df
    except Exception as e:
        print(f"Error on {today_str}: {e}")
        return None

def insert_data_to_db(df):
    """ KOSPI 데이터를 DB에 삽입하는 함수 """
    connection = get_db_connection()  # db_connection.py에서 가져온 함수로 DB 연결
    cursor = connection.cursor()

    # 데이터 삽입 SQL 쿼리
    insert_sql = """
    INSERT INTO DAILY_STOCK_PRICE (stock_code, opening_price, high_price, low_price, closing_price, trading_volume, trading_value, change_percent, trading_date)
    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
    """

    # tqdm을 이용해 진행률을 표시하며 데이터를 삽입
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="데이터 삽입 중"):
        cursor.execute(insert_sql, (
            row.name,                  # 티커 (종목코드)
            str(row['시가']),           # 시가를 문자열로 변환
            str(row['고가']),           # 고가를 문자열로 변환
            str(row['저가']),           # 저가를 문자열로 변환
            str(row['종가']),           # 종가를 문자열로 변환
            str(row['거래량']),         # 거래량을 문자열로 변환
            str(row['거래대금']),       # 거래대금을 문자열로 변환
            str(row['등락률']),         # 등락률을 문자열로 변환
            row['date']                # 거래일자 (이미 문자열)
        ))

    connection.commit()  # 데이터 삽입 후 커밋
    cursor.close()       # 커서 닫기
    connection.close()   # DB 연결 종료
    print("데이터 삽입 완료")

def process_kospi_data_for_today():
    """ 오늘 날짜 데이터를 가져와 DB에 삽입하는 함수 """
    print("오늘 날짜 데이터를 가져오는 중...")
    df = get_market_data_for_today()

    # 데이터가 존재하면 DB에 삽입
    if df is not None:
        insert_data_to_db(df)
    else:
        print("오늘은 영업일이 아닙니다. 데이터가 없습니다.")

# 데이터 처리 및 삽입 함수 실행
process_kospi_data_for_today()
