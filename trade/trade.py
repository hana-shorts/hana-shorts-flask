import kis_auth as ka
import kis_domstk as kb

# KIS 인증
ka.auth()


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

# [국내주식] 기본시세 > 주식현재가 호가 (종목번호 6자리)
rt_data = kb.get_inquire_asking_price_exp_ccn("2","J","005930")
print(rt_data)

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
# rt_data = kb.get_order_cash(ord_dv="buy",itm_no="005930", qty=2000, unpr=76000)
# print(rt_data.KRX_FWDG_ORD_ORGNO + "+" + rt_data.ODNO + "+" + rt_data.ORD_TMD) # 주문접수조직번호+주문접수번호+주문시각

# # [국내주식] 주문/계좌 > 주식일별주문체결조회
# rt_data = kb.get_inquire_daily_ccld_lst(dv="01")
# print(rt_data)

# # [국내주식] 주문/계좌 > 주식잔고조회
# rt_data = kb.get_inquire_balance_lst()
# print(rt_data)

