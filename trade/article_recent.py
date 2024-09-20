from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db_connection import get_db_connection  # DB 연결 설정 가져오기
from datetime import datetime

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

# 현재 날짜 가져오기 및 포맷팅 (예: '20240827')
current_date = datetime.now().strftime('%Y%m%d')

# 네이버 금융 뉴스 페이지로 이동 (현재 날짜 반영)
news_list_url = f"https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&date={current_date}&page=1"
driver.get(news_list_url)

# 요소가 나타날 때까지 기다림
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'articleSubject')))

# 'realtimeNewsList _replaceNewsLink' 클래스의 모든 기사를 포함하는 ul 태그 내 dt와 dd 태그들을 가져오기
dt_tags = driver.find_elements(By.CSS_SELECTOR, '.realtimeNewsList._replaceNewsLink dt.thumb')
subject_tags = driver.find_elements(By.CSS_SELECTOR, '.realtimeNewsList._replaceNewsLink dd.articleSubject')
summary_tags = driver.find_elements(By.CSS_SELECTOR, '.realtimeNewsList._replaceNewsLink dd.articleSummary')

# DB 연결
conn = get_db_connection()
cursor = conn.cursor()

# 기사 데이터 추출 및 프로시저 호출을 통한 DB 삽입
for i in range(len(subject_tags)):
    # 썸네일 추출 (존재하지 않을 수 있음)
    try:
        thumb_url = dt_tags[i].find_element(By.TAG_NAME, 'img').get_attribute('src')
    except:
        thumb_url = None

    # 기사 제목과 링크 추출
    title_tag = subject_tags[i].find_element(By.TAG_NAME, 'a')
    article_link = title_tag.get_attribute('href')
    title = title_tag.get_attribute('title')

    # 요약, 언론사, 작성 시간 추출
    summary = summary_tags[i].text
    press = summary_tags[i].find_element(By.CLASS_NAME, 'press').text
    wdate_str = summary_tags[i].find_element(By.CLASS_NAME, 'wdate').text

    # '2024-08-27 17:39' 형식의 문자열을 날짜와 시간으로 분리
    published_datetime = datetime.strptime(wdate_str, '%Y-%m-%d %H:%M')
    published_date = published_datetime.date()
    published_time = published_datetime.strftime('%H:%M')

    # 프로시저 호출을 통한 데이터 삽입
    cursor.callproc("insert_article_recent", [
        title,
        article_link,
        thumb_url,
        summary,
        press,
        published_date,
        published_time
    ])

# 커밋 및 DB 연결 종료
conn.commit()
cursor.close()
conn.close()

# WebDriver 종료
driver.quit()
