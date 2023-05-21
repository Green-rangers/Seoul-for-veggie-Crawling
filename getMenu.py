import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, NoSuchFrameException

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")

# Setup options
option = Options()
option.add_argument("disable-infobars")
option.add_argument("disable-extensions")
option.add_argument('disable-gpu')

# 속도 향상을 위한 옵션 해제
prefs = {
    'profile.default_content_setting_values': {
        'cookies': 2,
        'images': 2,
        'plugins': 2,
        'popups': 2,
        'geolocation': 2,
        'notifications': 2,
        'auto_select_certificate': 2,
        'fullscreen': 2,
        'mouselock': 2,
        'mixed_script': 2,
        'media_stream': 2,
        'media_stream_mic': 2,
        'media_stream_camera': 2,
        'protocol_handlers': 2,
        'ppapi_broker': 2,
        'automatic_downloads': 2,
        'midi_sysex': 2,
        'push_messaging': 2,
        'ssl_cert_decisions': 2,
        'metro_switch_to_desktop': 2,
        'protected_media_identifier': 2,
        'app_banner': 2,
        'site_engagement': 2,
        'durable_storage': 2
    }
}
options.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()

# 기존의 'restaurant_data.csv' 파일이 존재하는지 확인합니다.
try:
    df_result = pd.read_csv('restaurant_data.csv')
except FileNotFoundError:
    # 파일이 없다면 새로운 DataFrame을 생성합니다.
    df_result = pd.DataFrame(columns=['가게이름', '메뉴', '주소', '전화번호', '카테고리', '영업시간1', '영업시간2'])


def menu(data):  # 메뉴 크롤링
    driver.get("https://map.naver.com/v5/search/" + data)
    time.sleep(3)
    driver.implicitly_wait(3)



    try:
        driver.switch_to.frame('searchIframe')
    except NoSuchFrameException as e:
        print(f'프레임을 찾을 수 없습니다: {e}')
        return

    try:
        temp = driver.find_element_by_xpath('//*[@id="_pcmap_list_scroll_container"]/ul')
    except NoSuchElementException:
        print(f'검색결과가 없는 가게입니다. {data}')
        return

    driver.implicitly_wait(20)
    button = temp.find_elements_by_tag_name('a')
    print(button)
    driver.implicitly_wait(20)
    if '이미지수' in button[0].text or button[0].text == '':
        button[1].send_keys(Keys.ENTER)
    else:
        button[0].send_keys(Keys.ENTER)
    driver.implicitly_wait(10)
    time.sleep(3)
    driver.switch_to.default_content()
    driver.switch_to.frame('entryIframe')
    driver.implicitly_wait(2)
    start = driver.find_elements_by_class_name('mpoxR')
    if len(start) == 0:
        start = driver.find_elements_by_class_name('jnwQZ')
    if len(start) == 0:
        print('메뉴가 없습니다')
        return -1

    found_name = driver.find_element_by_class_name('Fc1rA').text
    print(f"가게이름: {found_name}")
    simple_menu = start[0].text
    print(f"메뉴: {simple_menu}")
    address = driver.find_element_by_class_name('LDgIH').text
    print(f"주소: {address}")
    try:
        element = driver.find_element_by_class_name('xlx7Q')
    except NoSuchElementException:
        print('요소를 찾을 수 없습니다.')
        return
    phone = driver.find_element_by_class_name('xlx7Q').text
    print(f"전화번호: {phone}")
    category = driver.find_element_by_class_name('DJJvD').text
    print(f"카테고리: {category}")
    elements = driver.find_elements_by_class_name('_UCia')
    if len(elements) > 1:
        elements[1].click()
    else:
        print(f'데이터 요소 접근 불가 {data}')
        return

    driver.find_elements_by_class_name('_UCia')[1].click()
    open_time1 = driver.find_elements_by_class_name('vV_z_')[1].text
    print(f"영업시간1: {open_time1}")
    open_time2 = driver.find_elements_by_class_name('vV_z_')[2].text
    print(f"영업시간2: {open_time2}")

    try:
        simple_menu = start[0].text
    except StaleElementReferenceException:
        print(f'stale element reference 예외 처리. {data}')
        return

    # 데이터를 DataFrame에 저장
    data = {'가게이름': [found_name], '메뉴': [simple_menu], '주소': [address], '전화번호': [phone], '카테고리': [category],
            '영업시간1': [open_time1], '영업시간2': [open_time2]}
    df = pd.DataFrame(data)

    # 기존의 DataFrame에 새로운 데이터 추가
    global df_result
    df_result = df_result.append(df, ignore_index=True)

    # DataFrame을 CSV 파일로 저장
    df_result.to_csv('restaurant_data.csv', index=False)


# "real_seoul.csv" 파일 읽기
df1 = pd.read_csv("proud_seoul1.csv")

# "상호명" 열의 데이터를 하나씩 가져와서 menu 함수에 전달
for name in df1["상호명"]:
    try:
        menu(name)
    except NoSuchFrameException:
        print(f'프레임을 찾을 수 없어 다음 menu로 넘어갑니다: {name}')
        continue

# WebDriver 종료
driver.quit()
