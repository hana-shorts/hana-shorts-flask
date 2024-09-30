import requests
from bs4 import BeautifulSoup
from datetime import datetime
from db_connection import get_db_connection  # DB 연결 설정 가져오기

# Base URL
BASE_URL = 'https://www.hanaw.com'

# Function to parse and extract data from a single list item
def parse_list_item(li, category):
    try:
        # Image URL
        img_tag = li.find('li', class_='view-img').find('img')
        image_url = img_tag['src'].strip() if img_tag and 'src' in img_tag.attrs else None
        if image_url and not image_url.startswith('http'):
            image_url = BASE_URL + image_url  # 상대 경로일 경우 절대 경로로 변환

        # Author
        author_li = li.find('li', class_='view-txt')
        author = author_li.get_text(separator=" ", strip=True) if author_li else None

        # Title
        title_tag = li.find('h3').find('a', class_='more_btn title')
        title = title_tag.get_text(strip=True) if title_tag else None

        # Date and Time
        info_li = li.find('li', class_='mb7 m-info info')
        date_span = info_li.find_all('span', class_='txtbasic') if info_li else []
        article_date = date_span[0].get_text(strip=True) if len(date_span) > 0 else None
        article_time = date_span[1].get_text(strip=True) if len(date_span) > 1 else None

        # Download URL
        pdf_div = li.find('div', class_='pdf')
        download_link = pdf_div.find('a', class_='j_fileLink') if pdf_div else None
        download_url = download_link['href'].strip() if download_link and 'href' in download_link.attrs else None
        if download_url and not download_url.startswith('http'):
            download_url = BASE_URL + download_url  # 상대 경로일 경우 절대 경로로 변환

        # Convert article_date to DATE type
        if article_date:
            article_date_obj = datetime.strptime(article_date, '%Y.%m.%d').date()
        else:
            article_date_obj = None

        data = {
            'category': category,
            'image_url': image_url,
            'author': author,
            'title': title,
            'article_date': article_date_obj,
            'article_time': article_time,
            'download_url': download_url
        }

        return data
    except Exception as e:
        print(f"Error parsing list item: {e}")
        return None

# Function to insert data into the Oracle DB
def insert_into_db(connection, data):
    insert_sql = """
    INSERT INTO research_analysis (
        category,
        image_url,
        author,
        title,
        article_date,
        article_time,
        download_url
    ) VALUES (
        :category,
        :image_url,
        :author,
        :title,
        :article_date,
        :article_time,
        :download_url
    )
    """
    try:
        cursor = connection.cursor()
        cursor.execute(insert_sql, data)
        connection.commit()
        print(f"Inserted: {data['title']}")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        cursor.close()

# Main scraping function
def scrape_and_store():
    # Define the URLs and their corresponding subcategories
    urls = {
        '글로벌 리서치' : 'https://www.hanaw.com/main/research/research/list.cmd?pid=8&cid=1',
        '글로벌 자산전략': 'https://www.hanaw.com/main/research/research/list.cmd?pid=1&cid=1',
        '주식 전략': 'https://www.hanaw.com/main/research/research/list.cmd?pid=2&cid=1',
        '산업/기업': 'https://www.hanaw.com/main/research/research/list.cmd?pid=3&cid=1'
    }

    # Initialize database connection
    connection = get_db_connection()

    try:
        for category, url in urls.items():
            print(f"Scraping category: {category} from URL: {url}")
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to retrieve {url} with status code {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the main div containing the list
            main_div = soup.find('div', class_='daily_bbs m-mb20')
            if not main_div:
                print(f"No main div found in {url}")
                continue

            # Find the ul within main_div
            ul = main_div.find('ul')
            if not ul:
                print(f"No ul found within main_div in {url}")
                continue

            # Iterate through each direct li child of ul
            list_items = ul.find_all('li', recursive=False)
            print(f"Found {len(list_items)} list items.")
            for li in list_items:
                data = parse_list_item(li, category)
                if data:
                    print(data)  # Print the extracted data
                    insert_into_db(connection, data)
    finally:
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    # Uncomment the following line to create the table (Run only once)
    # create_table()

    scrape_and_store()
