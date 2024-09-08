from faker import Faker
import random

# FAKER 인스턴스 생성, 로케일 설정 가능 (예: 'en_US', 'ko_KR' 등)
fake = Faker()

def generate_member_data(num_members=10):
    members = []
    for _ in range(num_members):
        member = {
            "member_id": fake.uuid4(),           # 고유 회원 ID
            "password": fake.password(),         # 비밀번호
            "name": fake.name(),                 # 이름
            "email": fake.email(),               # 이메일
            "phone_number": fake.phone_number(), # 휴대폰 번호
            "signup_date": fake.date_between(start_date="-5y", end_date="today"), # 가입 날짜
            "last_login": fake.date_time_this_year(before_now=True, after_now=False, tzinfo=None), # 마지막 로그인
            "short_sale_notification": random.choice(['Y', 'N']), # 공매도 안내 여부
            "service_notification": random.choice(['Y', 'N'])     # 서비스 안내 여부
        }
        members.append(member)
    return members

# 10명의 회원 데이터 생성 예시
member_data = generate_member_data(10)
for data in member_data:
    print(data)
