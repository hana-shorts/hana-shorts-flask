import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db_connection import get_db_connection  # DB 연결 설정 가져오기

# 시작 시간 기록
start_time = time.time()

# Chrome WebDriver 설정
chrome_driver_path = '../chromedriver.exe'  # chromedriver 경로 설정
options = Options()
options.add_argument("--headless")  # 브라우저를 숨김 모드로 실행
options.add_argument("--disable-gpu")  # GPU 가속 비활성화
options.add_argument("--window-size=1920,1080")  # 브라우저 창 크기 설정
options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용하지 않음

# WebDriver 초기화
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Investing.com 페이지로 이동
url = "https://kr.investing.com/commodities/real-time-futures"
driver.get(url)

# 버튼을 클릭하여 데이터를 로드
button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test="quote-tab"][data-test-tab-id="1"]'))
)
button.click()

# 모든 <tr> 태그 찾기
rows = driver.find_elements(By.CSS_SELECTOR, 'tr.datatable-v2_row__hkEus.dynamic-table-v2_row__ILVMx')

# DB 연결
conn = get_db_connection()
cursor = conn.cursor()

try:
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        data = [cell.text for cell in cells]

        # 필요한 데이터 추출
        commodity_name = data[1]
        period_daily = data[2]
        period_weekly = data[3]
        period_monthly = data[4]
        period_ytd = data[5]
        period_yearly = data[6]
        period_3years = data[7]

        # 프로시저 호출
        cursor.callproc("update_or_insert_commodity_period_data", [
            commodity_name,
            period_daily,
            period_weekly,
            period_monthly,
            period_ytd,
            period_yearly,
            period_3years
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

print("Commodity period data updated successfully!")
