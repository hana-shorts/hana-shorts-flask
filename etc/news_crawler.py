from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

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

# 네이버 금융 뉴스 페이지로 이동
news_list_url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&date=20240827&page=1"
driver.get(news_list_url)

# 요소가 나타날 때까지 기다림
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'articleSubject')))

# 뉴스 목록에서 제목과 링크 추출
def get_article_links():
    articles = driver.find_elements(By.CLASS_NAME, 'articleSubject')
    article_links = [article.find_element(By.TAG_NAME, 'a').get_attribute('href') for article in articles]
    return article_links

# 각 기사 페이지에서 필요한 정보 추출
def scrape_article(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title = soup.find('h2', class_='media_end_head_headline').get_text(strip=True)

    # 기사 작성 시간 추출
    time = soup.find('span', class_='media_end_head_info_datestamp_time').get_text(strip=True)

    # 이미지 URL 추출
    image_tag = soup.find('img', id='img1')
    image_url = image_tag['data-src'] if image_tag else ""

    # 기자 이름 추출 (존재 여부 확인 후 처리)
    journalist_tag = soup.find('em', class_='media_end_head_journalist_name')
    journalist_name = journalist_tag.get_text(strip=True) if journalist_tag else ""

    # 기사 본문 추출
    article_body = soup.find('article', id='dic_area').get_text(separator='\n', strip=True)

    # 결과 출력
    print("URL:", article_url)
    print("제목:", title)
    print("시간:", time)
    print("이미지 URL:", image_url)
    print("기자 이름:", journalist_name)
    print("본문:", article_body)
    print("-" * 80)

# 링크 추출 및 기사 데이터 스크래핑
article_links = get_article_links()
for link in article_links:
    scrape_article(link)

# WebDriver 종료
driver.quit()
