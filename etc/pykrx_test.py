from pykrx import stock
from pykrx import bond

# df = stock.get_shorting_investor_volume_by_date("20240415", "20240419", "KOSPI")
# print(df.head())    
# print(df)

df = stock.get_market_ohlcv("20240715", "20240719", "005930")
print(df)