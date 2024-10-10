import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
import random  # 랜덤 모듈 추가

def fetch_latest_news():
    try:
        current_date = datetime.now().strftime('%Y%m%d')
        # current_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        news_list_url = f"https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&date={current_date}&page=1"
        response = requests.get(news_list_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        dt_tags = soup.select('.realtimeNewsList._replaceNewsLink dt.thumb')
        subject_tags = soup.select('.realtimeNewsList._replaceNewsLink dd.articleSubject')
        summary_tags = soup.select('.realtimeNewsList._replaceNewsLink dd.articleSummary')

        news_list = []
        for i in range(len(subject_tags)):
            try:
                thumb_url = dt_tags[i].find('img')['src']
            except (IndexError, KeyError, TypeError):
                thumb_url = None

            title_tag = subject_tags[i].find('a')
            article_link = title_tag['href']
            title = title_tag['title']

            query_params = parse_qs(urlparse(article_link).query)
            article_id = query_params.get('article_id', [None])[0]
            office_id = query_params.get('office_id', [None])[0]

            if article_id and office_id:
                final_article_link = f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
            else:
                final_article_link = article_link

            summary_tag = summary_tags[i]
            press = summary_tag.find('span', class_='press').text.strip()
            wdate_str = summary_tag.find('span', class_='wdate').text.strip()

            for span in summary_tag.find_all('span'):
                span.extract()

            summary = summary_tag.text.strip()
            published_datetime = datetime.strptime(wdate_str, '%Y-%m-%d %H:%M')
            published_date = published_datetime.strftime('%Y년 %m월 %d일')
            published_time = published_datetime.strftime('%H:%M')

            news_list.append({
                'title': title,
                'date': published_date,
                'time': published_time,
                'description': summary,
                'img': thumb_url,
                'press': press,
                'link': final_article_link
            })

        return news_list
    except Exception as e:
        print(f"Error occurred while fetching latest news: {e}")
        return None

def fetch_popular_news():
    try:
        current_date = datetime.now().strftime('%Y%m%d')
        # current_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        news_list_url = f"https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&date={current_date}&page=2"
        response = requests.get(news_list_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        dt_tags = soup.select('.realtimeNewsList._replaceNewsLink dt.thumb')
        subject_tags = soup.select('.realtimeNewsList._replaceNewsLink dd.articleSubject')
        summary_tags = soup.select('.realtimeNewsList._replaceNewsLink dd.articleSummary')

        news_list = []
        for i in range(len(subject_tags)):
            try:
                thumb_url = dt_tags[i].find('img')['src']
            except (IndexError, KeyError, TypeError):
                thumb_url = None

            title_tag = subject_tags[i].find('a')
            article_link = title_tag['href']
            title = title_tag['title']

            query_params = parse_qs(urlparse(article_link).query)
            article_id = query_params.get('article_id', [None])[0]
            office_id = query_params.get('office_id', [None])[0]

            if article_id and office_id:
                final_article_link = f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
            else:
                final_article_link = article_link

            summary_tag = summary_tags[i]
            press = summary_tag.find('span', class_='press').text.strip()
            wdate_str = summary_tag.find('span', class_='wdate').text.strip()

            for span in summary_tag.find_all('span'):
                span.extract()

            summary = summary_tag.text.strip()
            published_datetime = datetime.strptime(wdate_str, '%Y-%m-%d %H:%M')
            published_date = published_datetime.strftime('%Y년 %m월 %d일')
            published_time = published_datetime.strftime('%H:%M')

            news_list.append({
                'title': title,
                'date': published_date,
                'time': published_time,
                'description': summary,
                'img': thumb_url,
                'press': press,
                'link': final_article_link
            })

        # 시드값을 설정하여 뉴스 리스트를 섞음 (예: 시드값 42)
        random.seed(42)  # 원하는 시드값으로 변경 가능
        random.shuffle(news_list)

        return news_list
    except Exception as e:
        print(f"Error occurred while fetching popular news: {e}")
        return None
