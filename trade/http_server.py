from flask import Flask, request, jsonify
from flask_cors import CORS  # 추가
import kis_auth as ka
import kis_domstk as kb
import kis_paper_auth as kpa
import kis_paper_domstk as kpb
from pykrx import stock  # 추가
from datetime import datetime, timedelta  # 추가

# KIS 인증
ka.auth()
kpa.auth()

app = Flask(__name__)
CORS(app)  # CORS 활성화

@app.route('/api/orderbook', methods=['GET'])
def get_orderbook():
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({"error": "Stock code is required"}), 400

    # KIS API 호출하여 호가창 데이터 가져오기
    ask_data = kb.get_inquire_asking_price_exp_ccn("2", "J", stock_code)
    ask_data_dict = ask_data.to_dict(orient='records')

    return jsonify(ask_data_dict)


@app.route('/api/balance', methods=['GET'])
def get_balance():
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({"error": "Stock code is required"}), 400

    # KIS API 호출하여 호가창 데이터 가져오기
    ask_data = kpb.get_inquire_psbl_order(stock_code)

    # DataFrame을 JSON 형식으로 변환
    ask_data_dict = ask_data.to_dict(orient='records')

    return jsonify(ask_data_dict)

@app.route('/api/chart', methods=['GET'])
def get_chart():
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({"error": "Stock code is required"}), 400

    # 최근 5년 전부터 오늘까지의 날짜 계산
    start_date = (datetime.today() - timedelta(days=365*10)).strftime('%Y%m%d')
    end_date = datetime.today().strftime('%Y%m%d')

    # pykrx 라이브러리를 사용해 데이터 가져오기
    chart_data = stock.get_market_ohlcv(start_date, end_date, stock_code)
    chart_data = chart_data[chart_data['거래량'] > 0]  # 거래량이 0인 날짜 제거
    chart_data.index = chart_data.index.strftime('%Y-%m-%d')  # 날짜 포맷 변경
    chart_data_dict = chart_data.reset_index().to_dict(orient='records')

    return jsonify(chart_data_dict)


if __name__ == '__main__':
    app.run(port=5002)  # HTTP 서버는 포트 5002에서 실행
