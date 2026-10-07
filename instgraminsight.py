# 미니 프로젝트
# 파이썬을 활용한 데이터 분석 프로젝트

# 인스타그램 인사이트 분석

# 김신희, 김혜림

# 데이터 수집 - 인스타그램 게시물 업로드 날짜+시간, 좋아요수, 도달한계정수 등
# ㄴ 웹 크롤링 사용 selenium


# # 웹 크롤링

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# 인스타그램 로그인 정보
USERNAME = '**********'
PASSWORD = '*************'

# Edge 웹 드라이버 설정
service = Service()
driver = webdriver.Edge(service=service)

# 인스타그램 접속 및 로그인
driver.get('https://www.instagram.com/accounts/login/')
time.sleep(5)  # 페이지 로딩 대기

# 로그인 폼에서 사용자명과 비밀번호 입력 필드를 찾음
username_input = driver.find_element(By.NAME, 'username')
password_input = driver.find_element(By.NAME, 'password')

# 입력 필드에 로그인 정보 입력
username_input.send_keys(USERNAME)
password_input.send_keys(PASSWORD)
password_input.send_keys(Keys.RETURN)

time.sleep(10)  # 로그인 완료 대기

# 개인 프로필로 이동
driver.get(f'https://www.instagram.com/{USERNAME}/')
time.sleep(10)  # 프로필 페이지 로딩 대기

# 스크롤 끝까지 내려서 모든 게시물 로드
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # 페이지 로딩 대기 시간 늘림
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 게시물 링크 추출
posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
post_links = [post.get_attribute('href') for post in posts]
print(f"Found {len(post_links)} posts.")

# 날짜 넣을 빈 리스트 생성
dates = []

for link in post_links:
    driver.get(link)
    time.sleep(5)
    
    # 업로드 날짜 + 시간 추출
    try:
        date_time = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
        dates.append(date_time)
    except Exception as e:
        print(f"Error extracting date from {link}: {e}")
        continue

# 데이터 프레임 생성
df_date = pd.DataFrame(dates, columns=['날짜_시간'])

# 엑셀로 저장
df_date.to_excel('C:/KEPCO/MiniProject/Project/instagram_dates.xlsx', index=False)

# 브라우저 종료
driver.quit()


# # 시간대 크롤링 하다가 인스타그램 측에서 경고 날림
# # 좋아요수와 도달 수는 직접 수집

# # instagram_likes.xlsx
# # instagram_dates.xlsx



# 라이브러리 설정
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta

# 데이터 불러오기
like = pd.read_excel("C:/KEPCO/MiniProject/Project/instagram_likes.xlsx")
date = pd.read_excel("C:/KEPCO/MiniProject/Project/instagram_dates.xlsx")
reach = pd.read_excel("C:/KEPCO/MiniProject/Project/instagram_reach.xlsx")

# 데이터프레임 병합
insight = pd.merge(date, like, left_index=True, right_index=True)
insight = pd.merge(insight, reach, left_index=True, right_index=True)

# '날짜_시간' 열을 datetime 형식으로 변환하고 9시간을 추가
insight['날짜_시간'] = pd.to_datetime(insight['날짜_시간']) + timedelta(hours=9)

# 날짜와 시간을 각각의 열로 분리
insight['날짜'] = insight['날짜_시간'].dt.date
insight['시간'] = insight['날짜_시간'].dt.time

# 불필요한 '날짜_시간' 열 삭제
insight = insight.drop(columns=['날짜_시간'])

# 열 순서 변경
insight = insight[['날짜', '시간', '좋아요', '도달']]

# '날짜' 열을 datetime 형식으로 변환
insight['날짜'] = pd.to_datetime(insight['날짜'])

# 영어 요일을 한글 요일로 변환하는 딕셔너리
weekday_map = {
    'Monday': '월요일',
    'Tuesday': '화요일',
    'Wednesday': '수요일',
    'Thursday': '목요일',
    'Friday': '금요일',
    'Saturday': '토요일',
    'Sunday': '일요일'
}

# '요일' 열 추가: 날짜에 해당하는 영어 요일을 한글로 변환
insight['요일'] = insight['날짜'].dt.day_name().map(weekday_map)

# 도달 열의 NaN(결측값)을 평균값으로 대체
average_reach = insight['도달'].mean()
insight['도달'] = insight['도달'].fillna(average_reach)

# 데이터프레임을 CSV 파일로 저장 (필요 시)
insight.to_csv('C:/KEPCO/MiniProject/Project/insight.csv', index=False, encoding='utf-8-sig')


### 데이터 분석 ###

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows의 경우 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 부호 깨짐 방지



# 요일 순서 정의
day_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
insight['요일'] = pd.Categorical(insight['요일'], categories=day_order, ordered=True)

# 요일별 좋아요 수의 평균
likes_by_day = insight.groupby('요일')['좋아요'].mean()

# 시각화
plt.figure(figsize=(12, 6))
plt.plot(likes_by_day.index, likes_by_day, marker='o', color='skyblue', linestyle='-', linewidth=2, markersize=8)
plt.title('요일 별 좋아요 수')
plt.xlabel('요일')
plt.ylabel('평균 좋아요 수')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()


# 요일별 도달 수의 평균
reach_by_day = insight.groupby('요일')['도달'].mean()

# 시각화
plt.figure(figsize=(12, 6))
plt.plot(reach_by_day.index, reach_by_day, marker='o', color='salmon', linestyle='-', linewidth=2, markersize=8)
plt.title('요일 별 도달 수')
plt.xlabel('요일')
plt.ylabel('평균 도달 수')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

# 시간대 별 좋아요 수 (3시간씩 묶어서 분석)
insight['시간대'] = insight['시간'].apply(lambda x: f"{(x.hour // 3) * 3:02d}:00-{((x.hour // 3) * 3 + 3):02d}:00")
likes_by_time = insight.groupby('시간대')['좋아요'].mean()

# 시각화
plt.figure(figsize=(12, 6))
plt.plot(likes_by_time.index, likes_by_time, marker='o', color='lightgreen', linestyle='-', linewidth=2, markersize=8)
plt.title('시간대 별 좋아요 수')
plt.xlabel('시간대')
plt.ylabel('평균 좋아요 수')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()


# 시간대별 도달 수
reach_by_time = insight.groupby('시간대')['도달'].mean()

# 시각화
plt.figure(figsize=(12, 6))
plt.plot(reach_by_time.index, reach_by_time, marker='o', color='orange', linestyle='-', linewidth=2, markersize=8)
plt.title('시간대 별 도달 수')
plt.xlabel('시간대')
plt.ylabel('평균 도달 수')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()



# '요일'과 '시간대'별로 그룹화하여 평균 좋아요 수를 계산하고, 결과를 가로로 펼침
likes_by_day_time = insight.groupby(['요일', '시간대'])['좋아요'].mean().unstack()

# '요일'과 '시간대'별로 그룹화하여 평균 도달 수를 계산하고, 결과를 가로로 펼침
reach_by_day_time = insight.groupby(['요일', '시간대'])['도달'].mean().unstack()

# 두 결과(좋아요 수와 도달 수)를 확인
likes_by_day_time, reach_by_day_time


# 전체 시각화 설정 (캔버스 크기 설정)
plt.figure(figsize=(14, 8))


# 히트맵(Heatmap)은 데이터 값을 색상으로 표현한 그래프의 한 형태로, 
# 2차원 데이터에서 각 값의 크기에 따라 다른 색상을 사용하여 시각적으로 데이터를 표현합니다. 
# 히트맵은 주로 행(row)과 열(column)로 구성된 매트릭스 형태의 데이터를 시각화할 때 사용되며, 
# 데이터의 패턴, 분포, 상관관계 등을 쉽게 파악할 수 있게 도와줍니다.


# 요일 및 시간대별 평균 좋아요 수
plt.subplot(2, 1, 1)  # 첫 번째 subplot 설정
sns.heatmap(likes_by_day_time, annot=True, fmt=".1f", cmap="Blues", cbar=True, linewidths=.5)  # 히트맵 생성
plt.title('요일 및 시간대별 평균 좋아요 수')  # 그래프 제목 설정
plt.xlabel('시간대 (시)')  # X축 레이블 설정
plt.ylabel('요일')  # Y축 레이블 설정

# 요일 및 시간대별 평균 도달 수
plt.subplot(2, 1, 2)  # 두 번째 subplot 설정
sns.heatmap(reach_by_day_time, annot=True, fmt=".1f", cmap="Oranges", cbar=True, linewidths=.5)  # 히트맵 생성
plt.title('요일 및 시간대별 평균 도달 수')  # 그래프 제목 설정
plt.xlabel('시간대 (시)')  # X축 레이블 설정
plt.ylabel('요일')  # Y축 레이블 설정

# 레이아웃을 자동으로 조정하여 그래프 간 간격을 맞춤
plt.tight_layout()

plt.show()



# 전체 시각화 설정 (캔버스 크기 설정)
plt.figure(figsize=(12, 8))

# 요일 및 시간대별 평균 좋아요 수 (Blues 컬러맵, 투명도 설정)
sns.heatmap(likes_by_day_time, annot=False, fmt=".1f", cmap="Blues", cbar=True, linewidths=.5, alpha=0.5)

# 요일 및 시간대별 평균 도달 수 (Oranges 컬러맵, 투명도 설정)
sns.heatmap(reach_by_day_time, annot=False, fmt=".1f", cmap="Oranges", cbar=True, linewidths=.5, alpha=0.5)

# 그래프 제목 및 축 레이블 설정
plt.title('요일 및 시간대별 평균 좋아요 수 및 도달 수')
plt.xlabel('시간대 (시)')
plt.ylabel('요일')

plt.show()