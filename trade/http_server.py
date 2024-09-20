# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import pandas as pd
from db_connection import get_db_connection

# KIS 인증 모듈 임포트
import kis_auth as ka
import kis_domstk as kb
import kis_paper_auth as kpa
import kis_paper_domstk as kpb
import pykrx.stock as stock

# KIS 인증
ka.auth()
kpa.auth()

app = Flask(__name__)
CORS(app)

@app.route('/api/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        indicators = data.get('indicators', [])
        selected_sectors = data.get('selected_sectors', [])

        if not indicators or not selected_sectors:
            return jsonify({"error": "No indicators or sectors selected"}), 400

        # 선택된 지표에 따른 컬럼 매핑
        indicator_columns = {
            'Relative Strength Index (RSI)': 'rsi_score',
            'MACD': 'macd_score',
            'Stochastic Oscillator': 'stochastic_score',
            'Commodity Channel Index (CCI)': 'cci_score',
            'Average Directional Index (ADX)': 'adx_score',
            'Momentum': 'momentum_score',
            'Moving Average (MA)': 'ma_score',
            'Bollinger Bands': 'bb_score',
            'On-Balance Volume (OBV)': 'obv_score',
            'Ichimoku Cloud': 'ichimoku_score',
            'VWAP': 'vwap_score',
            'Price Channel': 'price_channel_score'
        }

        selected_columns = []
        for indicator in indicators:
            column = indicator_columns.get(indicator)
            if column:
                selected_columns.append(column)

        if not selected_columns:
            return jsonify({"error": "Invalid indicators selected"}), 400

        # 업종에 해당하는 종목 코드와 종목명 가져오기
        connection = get_db_connection()
        cursor = connection.cursor()

        sectors_placeholder = ','.join([f":sector{i}" for i in range(len(selected_sectors))])
        sectors_params = {f"sector{i}": sector for i, sector in enumerate(selected_sectors)}

        cursor.execute(f"""
            SELECT stock_code, stock_name
            FROM stock_item 
            WHERE sector_type IN ({sectors_placeholder})
        """, sectors_params)

        tickers_data = cursor.fetchall()
        tickers = [row[0] for row in tickers_data]
        ticker_names = {row[0]: row[1] for row in tickers_data}  # 종목 코드와 이름을 매핑

        if not tickers:
            return jsonify({"error": "No tickers found for the selected sectors"}), 404

        query = f"""
        SELECT stock_code, {', '.join(selected_columns)}
        FROM STOCK_MODEL_SCORES
        WHERE stock_code IN ({', '.join([f"'{ticker}'" for ticker in tickers])}) 
        AND trading_date = (SELECT MAX(trading_date) FROM STOCK_MODEL_SCORES)
        """
        df = pd.read_sql(query, con=connection)
        connection.close()

        df.columns = [col.lower() for col in df.columns]

        if df.empty:
            return jsonify({"error": "No data available for the latest date"}), 404

        df['calculated_score'] = df[selected_columns].astype(float).mean(axis=1)
        df['stock_name'] = df['stock_code'].map(ticker_names)

        # 매수 상위 5개, 매도 하위 5개
        buy_recommendations = df.sort_values(by='calculated_score', ascending=False).head(5)['stock_name'].tolist()
        sell_recommendations = df.sort_values(by='calculated_score', ascending=True).head(5)['stock_name'].tolist()

        result = {
            'buy': buy_recommendations,
            'sell': sell_recommendations
        }

        return jsonify(result)

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/orderbook', methods=['GET'])
def get_orderbook():
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({"error": "Stock code is required"}), 400

    ask_data = kb.get_inquire_asking_price_exp_ccn("2", "J", stock_code)
    ask_data_dict = ask_data.to_dict(orient='records')

    return jsonify(ask_data_dict)

@app.route('/api/balance', methods=['GET'])
def get_balance():
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({"error": "Stock code is required"}), 400

    ask_data = kpb.get_inquire_psbl_order(stock_code)
    ask_data_dict = ask_data.to_dict(orient='records')

    return jsonify(ask_data_dict)

@app.route('/api/chart', methods=['GET'])
def get_chart():
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({"error": "Stock code is required"}), 400

    start_date = (datetime.today() - timedelta(days=365*10)).strftime('%Y%m%d')
    end_date = datetime.today().strftime('%Y%m%d')

    chart_data = stock.get_market_ohlcv_by_date(start_date, end_date, stock_code)
    chart_data = chart_data[chart_data['거래량'] > 0]
    chart_data.index = chart_data.index.strftime('%Y-%m-%d')
    chart_data_dict = chart_data.reset_index().to_dict(orient='records')

    return jsonify(chart_data_dict)

if __name__ == '__main__':
    app.run(port=5002)
