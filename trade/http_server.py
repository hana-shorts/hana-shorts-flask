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


@app.route('/api/get_research_analysis', methods=['GET'])
def get_research_analysis():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 모든 연구 분석 데이터를 가져옵니다.
        cursor.execute("""
            SELECT category, image_url, author, title, 
                   TO_CHAR(article_date, 'YY/MM/DD') AS article_date,
                   article_time, download_url
            FROM research_analysis
            ORDER BY category, article_date DESC
        """)

        rows = cursor.fetchall()
        connection.close()

        # 데이터를 카테고리별로 그룹화합니다.
        research_data = {}
        for row in rows:
            category = row[0]
            if category not in research_data:
                research_data[category] = []
            research_data[category].append({
                "image": row[1],
                "author": row[2],
                "title": row[3],
                "textLine1": row[4],
                "textLine2": row[5],
                "fileLink": row[6]
            })

        return jsonify(research_data)

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        indicators = data.get('indicators', [])
        selected_sectors = data.get('selected_sectors', [])

        if not indicators or not selected_sectors:
            return jsonify({"error": "No indicators or sectors selected"}), 400

        # Check if 'AI Model' is selected
        if 'AI Model' in indicators:
            use_ai_model = True
            indicators.remove('AI Model')  # Remove 'AI Model' from indicators
        else:
            use_ai_model = False

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

        if not selected_columns and not use_ai_model:
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

        # Fetch technical indicator scores
        if selected_columns:
            query = f"""
            SELECT stock_code, {', '.join(selected_columns)}
            FROM STOCK_MODEL_SCORES
            WHERE stock_code IN ({', '.join([f"'{ticker}'" for ticker in tickers])}) 
            AND trading_date = (SELECT MAX(trading_date) FROM STOCK_MODEL_SCORES)
            """
            df = pd.read_sql(query, con=connection)
            df.columns = [col.lower() for col in df.columns]
        else:
            df = pd.DataFrame({'stock_code': tickers})

        # Fetch AI scores if selected
        if use_ai_model:
            ai_query = f"""
            SELECT stock_code, ai_score
            FROM stock_ai_model_scores
            WHERE stock_code IN ({', '.join([f"'{ticker}'" for ticker in tickers])}) 
            AND trading_date = (SELECT MAX(trading_date) FROM stock_ai_model_scores)
            """
            df_ai = pd.read_sql(ai_query, con=connection)
            df_ai.columns = [col.lower() for col in df_ai.columns]
            # Merge with df
            df = pd.merge(df, df_ai, on='stock_code', how='left')
        else:
            df['ai_score'] = None

        connection.close()

        if df.empty:
            return jsonify({"error": "No data available for the latest date"}), 404

        # Convert scores to numeric, handle missing values
        score_columns = selected_columns + ['ai_score'] if use_ai_model else selected_columns
        for col in score_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Rank the scores
        for col in selected_columns:
            df[f"{col}_rank"] = df[col].rank(ascending=False, method='min')

        if use_ai_model:
            # For AI scores, rank them
            df['ai_score_rank'] = df['ai_score'].rank(ascending=False, method='min')

        # Calculate average rank
        rank_columns = [f"{col}_rank" for col in selected_columns]
        if use_ai_model:
            rank_columns.append('ai_score_rank')

        df['average_rank'] = df[rank_columns].mean(axis=1)

        df['stock_name'] = df['stock_code'].map(ticker_names)

        # Sort by average rank
        df_sorted = df.sort_values(by='average_rank', ascending=True)

        # 매수 상위 5개, 매도 하위 5개
        buy_recommendations = df_sorted.head(5)
        sell_recommendations = df_sorted.tail(5)

        # Fetch recent 6 months of data for each recommended stock
        end_date = datetime.today()
        start_date = end_date - timedelta(days=180)
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')

        connection = get_db_connection()
        buy_data = {}
        for index, row in buy_recommendations.iterrows():
            stock_code = row['stock_code']
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT trading_date, closing_price
                FROM daily_stock_price
                WHERE stock_code = :stock_code
                AND trading_date BETWEEN :start_date AND :end_date
                ORDER BY trading_date
            """, {'stock_code': stock_code, 'start_date': start_date_str, 'end_date': end_date_str})
            price_data = cursor.fetchall()
            price_df = pd.DataFrame(price_data, columns=['trading_date', 'close_price'])
            buy_data[stock_code] = price_df.to_dict(orient='records')

        sell_data = {}
        for index, row in sell_recommendations.iterrows():
            stock_code = row['stock_code']
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT trading_date, closing_price
                FROM daily_stock_price
                WHERE stock_code = :stock_code
                AND trading_date BETWEEN :start_date AND :end_date
                ORDER BY trading_date
            """, {'stock_code': stock_code, 'start_date': start_date_str, 'end_date': end_date_str})
            price_data = cursor.fetchall()
            price_df = pd.DataFrame(price_data, columns=['trading_date', 'close_price'])
            sell_data[stock_code] = price_df.to_dict(orient='records')

        connection.close()

        # 기존의 result 딕셔너리 생성 부분을 수정합니다.
        result = {
            'buy': buy_recommendations[['stock_code', 'stock_name']].to_dict(orient='records'),
            'sell': sell_recommendations[['stock_code', 'stock_name']].to_dict(orient='records'),
            'buy_data': buy_data,
            'sell_data': sell_data
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

    chart_data = stock.get_market_ohlcv(start_date, end_date, stock_code)
    chart_data = chart_data[chart_data['거래량'] > 0]
    chart_data.index = chart_data.index.strftime('%Y-%m-%d')
    chart_data_dict = chart_data.reset_index().to_dict(orient='records')

    return jsonify(chart_data_dict)


@app.route('/api/index_data', methods=['GET'])
def get_index_data():
    market_id = request.args.get('market_id')
    if not market_id:
        return jsonify({"error": "Market ID is required"}), 400
    start_date = (datetime.today() - timedelta(days=180)).strftime('%Y%m%d')  # 6개월 전
    end_date = datetime.today().strftime('%Y%m%d')  # 오늘 날짜
    df = stock.get_index_ohlcv_by_date(start_date, end_date, market_id)
    df = df.reset_index()
    df['Date'] = df['날짜'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df_dict = df[['Date', '종가']].to_dict(orient='records')
    return jsonify(df_dict)

if __name__ == '__main__':
    app.run(port=5002)
