import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from db_connection import get_db_connection  # DB 연결 설정 가져오기
from datetime import datetime

# 시작 시간 기록
start_time = time.time()

# Chrome WebDriver 설정
chrome_driver_path = '../chromedriver.exe'  # chromedriver 경로 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# WebDriver 초기화
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Investing.com 페이지로 이동
url = "https://kr.investing.com/currencies/streaming-forex-rates-majors"
driver.get(url)

# 모든 <tr> 태그 찾기
rows = driver.find_elements(By.CSS_SELECTOR, 'tr.datatable-v2_row__hkEus.dynamic-table-v2_row__ILVMx')

# DB 연결
conn = get_db_connection()
cursor = conn.cursor()

try:
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        data = [cell.text for cell in cells]
        current_time = datetime.now().strftime('%H:%M:%S')

        currency_name = data[1]
        buy_price = data[2]
        sell_price = data[3]
        high_price = data[4]
        low_price = data[5]
        change_value = data[6]
        change_percent = data[7]
        update_time = current_time

        # 프로시저 호출
        cursor.callproc("update_or_insert_market_currency_price", [
            currency_name,
            buy_price,
            sell_price,
            high_price,
            low_price,
            change_value,
            change_percent,
            update_time
        ])

    # 커밋
    conn.commit()

except Exception as e:
    conn.rollback()
    print("Error occurred:", e)

finally:
    cursor.close()
    conn.close()
    driver.quit()

# 종료 시간 기록
end_time = time.time()

# 실행 시간 계산 및 출력
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.2f} seconds")

print("Currency data updated successfully!")
