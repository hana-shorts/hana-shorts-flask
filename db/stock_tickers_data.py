from pykrx import stock
from db.db_connection import get_db_connection

def get_ticker_with_names_and_market(date=None, market="KOSPI"):
    tickers = stock.get_market_ticker_list(date, market=market)
    ticker_with_details = []

    for ticker in tickers:
        name = stock.get_market_ticker_name(ticker)
        sector = None  # 섹터 정보를 NULL로 설정
        ticker_with_details.append((ticker, name, market, sector))

    return ticker_with_details

def insert_tickers_to_db(ticker_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_sql = """
    INSERT INTO stock_tickers (ticker_code, ticker_name, market_type, sector_type)
    VALUES (:1, :2, :3, :4)
    """

    try:
        cursor.executemany(insert_sql, ticker_data)
        conn.commit()
        print(f"{cursor.rowcount}개의 종목 정보가 삽입되었습니다.")
    except Exception as e:
        conn.rollback()
        print("데이터 삽입 중 오류 발생:", e)
    finally:
        cursor.close()
        conn.close()

# 예시: 최근 영업일의 KOSPI 시장 주식 코드, 명칭, 시장 구분, 섹터 구분을 가져와 DB에 삽입
ticker_details = get_ticker_with_names_and_market()
print(ticker_details)
insert_tickers_to_db(ticker_details)
