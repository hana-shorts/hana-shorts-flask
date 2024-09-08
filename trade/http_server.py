from flask import Flask, request, jsonify
from flask_cors import CORS  # 추가
import kis_auth as ka
import kis_domstk as kb

# KIS 인증
ka.auth()

app = Flask(__name__)
CORS(app)  # CORS 활성화

@app.route('/api/ask-order', methods=['GET'])
def get_ask_order():
    stock_code = request.args.get('code')
    if not stock_code:
        return jsonify({"error": "Stock code is required"}), 400

    # KIS API 호출하여 호가창 데이터 가져오기
    ask_data = kb.get_inquire_asking_price_exp_ccn("2", "J", stock_code)
    ask_data_dict = ask_data.to_dict(orient='records')

    return jsonify(ask_data_dict)

if __name__ == '__main__':
    app.run(port=5002)  # HTTP 서버는 포트 6000에서 실행
