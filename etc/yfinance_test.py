import yfinance as yf

def fetch_stock_data(ticker):
    """
    주식 데이터를 실시간으로 가져오는 함수
    ticker: 주식 티커 심볼 (예: 'AAPL')
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d", interval="1m")  # 1일치 데이터, 1분 간격
    return hist

# 예시 데이터 호출
data = fetch_stock_data('TSLA')
print(data)
