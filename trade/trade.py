from pykrx import stock
from pykrx import bond

import kis_auth as ka
import kis_domstk as kb

import kis_paper_auth as kpa
import kis_paper_domstk as kpb

ka.auth()

# KIS 인증
kpa.auth()


# # [국내주식] 기본시세 > 주식현재가 시세 (종목번호 6자리)
# rt_data = kb.get_inquire_price(itm_no="005930")
# print(rt_data)    # 현재가, 전일대비

# # [국내주식] 기본시세 > 주식현재가 체결 (종목번호 6자리)
# rt_data = kb.get_inquire_ccnl(itm_no="005930")
# print(rt_data)

# # [국내주식] 기본시세 > 주식현재가 일자별 (종목번호 6자리 + 기간분류코드)
# # 기간분류코드 	D : (일)최근 30거래일  W : (주)최근 30주   M : (월)최근 30개월
# # 수정주가기준이며 수정주가미반영 기준을 원하시면 인자값 adj_prc_code="2" 추가
# rt_data = kb.get_inquire_daily_price(itm_no="005930", period_code="D")
# print(rt_data)

# # [국내주식] 기본시세 > 주식현재가 호가 (종목번호 6자리)
# rt_data = kb.get_inquire_asking_price_exp_ccn(itm_no="005930")
# print(rt_data)

# # [국내주식] 기본시세 > 주식현재가 호가 2 (종목번호 6자리)
# rt_data = kb.get_inquire_asking_price_exp_ccn("2","J","005930")
# print(rt_data)

# # [국내주식] 기본시세 > 주식현재가 투자자 (종목번호 6자리)
# rt_data = kb.get_inquire_investor(itm_no="005930")
# print(rt_data)

# # [국내주식] 종목정보 > 대차대조표 (종목번호 6자리)
# rt_data = kb.get_balance_sheet(itm_no="005930")
# print(rt_data)

# # [국내주식] 종목정보 > 손익계산서 (종목번호 6자리)
# rt_data = kb.get_income_statment(itm_no="005930")
# print(rt_data)

# # [국내주식] 종목정보 > 재무비율 (종목번호 6자리)
# rt_data = kb.get_financial_ratio(itm_no="005930")
# print(rt_data)


# # [국내주식] 주문/계좌 > 주식현금주문 (매수매도구분 buy,sell + 종목번호 6자리 + 주문수량 + 주문단가)
# # 지정가 기준이며 시장가 옵션(주문구분코드)을 사용하는 경우 kis_domstk.py get_order_cash 수정요망!
# rt_data = kpb.get_order_cash(ord_dv="buy",itm_no="445680", qty=100, unpr=16110)
# print(rt_data)

# # # [국내주식] 주문/계좌 > 주식일별주문체결조회
# rt_data = kpb.get_inquire_daily_ccld_lst(dv="01")
# print(rt_data)

# rt_data = kpb.get_inquire_daily_ccld_obj(dv="01")
# print(rt_data)

# # [국내주식] 주문/계좌 > 주식잔고조회
rt_data = kpb.get_inquire_balance_lst()
print(rt_data)

# # [국내주식] 주문/계좌 > 주식잔고조회
# rt_data = kpb.get_inquire_balance_obj()
# print(rt_data)

# # [국내주식] 주문/계좌 > 주식정정취소가능주문조회[v1_국내주식-004]
# rt_data = kb.get_inquire_psbl_rvsecncl_lst()
# print(rt_data)

# # [국내주식] 주문/계좌 > 매수가능조회
# rt_data = kpb.get_inquire_psbl_order("005930")
# print(rt_data)


# # [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)
# rt_data = kpb.get_inquire_daily_itemchartprice(itm_no="005930", inqr_strt_dt="20240801", inqr_end_dt="20240831")
# print(rt_data)

# # [국내주식] 기본시세 > 주식당일분봉조회
# rt_data = kb.get_inquire_time_itemchartprice("000660")
# print(rt_data)

# df = stock.get_market_ohlcv("20240918", market="KOSPI")
# print(df)

# tickers = stock.get_market_ticker_list()
# print(tickers)
#
# df = stock.get_market_ohlcv("20140914","20240923", "250060")
# print(df)

# from datetime import datetime, timedelta  # 추가
# start_date = (datetime.today() - timedelta(days=365*5)).strftime('%Y%m%d')
# end_date = datetime.today().strftime('%Y%m%d')
#
# print(start_date)
# print(end_date)

# df = stock.get_index_fundamental("20210101", "20210130", "2001")
# print(df.head())