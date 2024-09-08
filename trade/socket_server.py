import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO, emit
import kis_auth as ka
import kis_domstk as kb
from threading import Event, Thread, Lock

# KIS 인증
ka.auth()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 호가창 전용 전역 변수
orderbook_stop_event = Event()
orderbook_thread = None
orderbook_thread_lock = Lock()

# 체결 데이터 전용 전역 변수
settlement_stop_event = Event()
settlement_thread = None
settlement_thread_lock = Lock()

# 일별 데이터 전용 전역 변수
daily_stop_event = Event()
daily_thread = None
daily_thread_lock = Lock()

# 주가 정보 전용 전역 변수
stockinfo_stop_event = Event()
stockinfo_thread = None
stockinfo_thread_lock = Lock()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    global orderbook_thread, settlement_thread, daily_thread, stockinfo_thread
    print('Client disconnected')

    # 클라이언트 연결 해제 시 작업 중단
    orderbook_stop_event.set()
    if orderbook_thread is not None:
        orderbook_thread.join()

    settlement_stop_event.set()
    if settlement_thread is not None:
        settlement_thread.join()

    daily_stop_event.set()
    if daily_thread is not None:
        daily_thread.join()

    stockinfo_stop_event.set()
    if stockinfo_thread is not None:
        stockinfo_thread.join()

@socketio.on('request_orderbook')
def handle_orderbook_request(data):
    global orderbook_stop_event, orderbook_thread

    with orderbook_thread_lock:
        if orderbook_thread is not None:
            orderbook_stop_event.set()
            orderbook_thread.join()
            orderbook_stop_event.clear()

        stock_code = data.get('code')
        if not stock_code:
            emit('error', {'message': 'Stock code is required'})
            return

        print(f"Fetching data for stock code: {stock_code}")

        orderbook_thread = Thread(target=fetch_orderbook_data, args=(stock_code,))
        orderbook_thread.start()

def fetch_orderbook_data(stock_code):
    while not orderbook_stop_event.is_set():
        ask_data = kb.get_inquire_asking_price_exp_ccn(itm_no=stock_code)
        ask_data_dict = ask_data.to_dict(orient='records')
        socketio.emit('orderbook_update', ask_data_dict)
        socketio.sleep(5)

@socketio.on('stop_orderbook_data')
def handle_stop_orderbook_request():
    global orderbook_stop_event, orderbook_thread

    with orderbook_thread_lock:
        if orderbook_thread is not None:
            orderbook_stop_event.set()
            orderbook_thread.join()
            orderbook_thread = None
            orderbook_stop_event.clear()

@socketio.on('request_settlement_data')
def handle_settlement_request(data):
    global settlement_stop_event, settlement_thread

    with settlement_thread_lock:
        if settlement_thread is not None:
            settlement_stop_event.set()
            settlement_thread.join()
            settlement_stop_event.clear()

        stock_code = data.get('code')
        if not stock_code:
            emit('error', {'message': 'Stock code is required'})
            return

        print(f"Fetching settlement data for stock code: {stock_code}")

        settlement_thread = Thread(target=fetch_settlement_data, args=(stock_code,))
        settlement_thread.start()

def fetch_settlement_data(stock_code):
    while not settlement_stop_event.is_set():
        settlement_data = kb.get_inquire_ccnl(itm_no=stock_code)
        settlement_data_dict = settlement_data.to_dict(orient='records')
        socketio.emit('settlement_update', settlement_data_dict)
        socketio.sleep(5)

@socketio.on('stop_settlement_data')
def handle_stop_settlement_request():
    global settlement_stop_event, settlement_thread

    with settlement_thread_lock:
        if settlement_thread is not None:
            settlement_stop_event.set()
            settlement_thread.join()
            settlement_thread = None
            settlement_stop_event.clear()

@socketio.on('request_daily_data')
def handle_daily_data_request(data):
    global daily_stop_event, daily_thread

    with daily_thread_lock:
        if daily_thread is not None:
            daily_stop_event.set()
            daily_thread.join()
            daily_stop_event.clear()

        stock_code = data.get('code')
        if not stock_code:
            emit('error', {'message': 'Stock code is required'})
            return

        print(f"Fetching daily data for stock code: {stock_code}")

        daily_thread = Thread(target=fetch_daily_data, args=(stock_code,))
        daily_thread.start()

def fetch_daily_data(stock_code):
    while not daily_stop_event.is_set():
        daily_data = kb.get_inquire_daily_price(itm_no=stock_code, period_code="D")
        daily_data_dict = daily_data.to_dict(orient='records')
        socketio.emit('daily_update', daily_data_dict)
        socketio.sleep(5)

@socketio.on('stop_daily_data')
def handle_stop_daily_request():
    global daily_stop_event, daily_thread

    with daily_thread_lock:
        if daily_thread is not None:
            daily_stop_event.set()
            daily_thread.join()
            daily_thread = None
            daily_stop_event.clear()

@socketio.on('request_stock_info')
def handle_stock_info_request(data):
    global stockinfo_stop_event, stockinfo_thread

    with stockinfo_thread_lock:
        if stockinfo_thread is not None:
            stockinfo_stop_event.set()
            stockinfo_thread.join()
            stockinfo_stop_event.clear()

        stock_code = data.get('code')
        if not stock_code:
            emit('error', {'message': 'Stock code is required'})
            return

        print(f"Fetching stock info for stock code: {stock_code}")

        stockinfo_thread = Thread(target=fetch_stock_info, args=(stock_code,))
        stockinfo_thread.start()

def fetch_stock_info(stock_code):
    while not stockinfo_stop_event.is_set():
        stock_info = kb.get_inquire_price(itm_no=stock_code)
        stock_info_dict = stock_info.to_dict(orient='records')
        socketio.emit('stock_info_update', stock_info_dict)
        socketio.sleep(5)

@socketio.on('stop_stock_info')
def handle_stop_stock_info_request():
    global stockinfo_stop_event, stockinfo_thread

    with stockinfo_thread_lock:
        if stockinfo_thread is not None:
            stockinfo_stop_event.set()
            stockinfo_thread.join()
            stockinfo_thread = None
            stockinfo_stop_event.clear()

if __name__ == '__main__':
    socketio.run(app, port=5001)
