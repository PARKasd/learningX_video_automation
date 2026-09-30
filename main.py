from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import time
import math
import random
import os
import sys
import json
import getpass
import requests
 
# User credentials
username = "" #ID 입력 예) "asdf1234"
password = "" #비밀번호 입력 예) "1q2w3e4r5t!"
target_id = list()
 
 
def delay():
    delay_time = math.log10(random.randint(300, 350))
    print(delay_time)
    time.sleep(delay_time)
 
 
def is_chrome_installed():
    """Check if Google Chrome is installed on the system."""
    try:
        # Try to open Chrome with --version argument to check if it is installed
        subprocess.run(["chrome", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False
 
 
def download_and_install_chrome():
    """Download and install Google Chrome."""
    chrome_installer_url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    installer_path = os.path.join(os.getcwd(), "chrome_installer.exe")
 
    # Download the installer
    try:
        import urllib.request
        print("크롬이 감지되지 않아 다운로드를 시작합니다.")
        urllib.request.urlretrieve(chrome_installer_url, installer_path)
        print("다운로드 완료")
    except Exception as e:
        print(f"다운로드중 오류발생: {e}")
        return
 
    # Run the installer
    try:
        print("크롬 설치중")
        subprocess.run([installer_path, "/silent", "/install"], check=True)
        print("설치완료")
    except subprocess.CalledProcessError as e:
        print(f"설치 실패: {e}")
    finally:
        # Clean up the installer file
        if os.path.exists(installer_path):
            os.remove(installer_path)
            print("설치 파일 삭제.")
 
 
chrome_options = Options()
user_agent = 'user_agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
chrome_options.add_argument(user_agent)
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=chrome_options)
 
try:
    # Navigate to the login page
    driver.get('https://learning.hanyang.ac.kr')
 
    # Wait until the login form is present
    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.presence_of_element_located((By.ID, 'uid')))  # Update the ID
    password_field = driver.find_element(By.ID, 'upw')  # Update the ID
 
    # Enter the username and password
    username_field.send_keys(username)
    password_field.send_keys(password)
    delay()
 
    # Submit the login form
    password_field.send_keys(Keys.RETURN)
    driver.implicitly_wait(5)
 
    # Handle potential alert
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        print("팝업 무시 완료")
    except:
        print("팝업 없음")
 
    # Wait for the login to complete, you might need to adjust the conditions
    wait.until(EC.url_changes('https://learning.hanyang.ac.kr'))
    print("Logged in successfully")
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="DashboardCard_Container"]/div/div[1]')))
 
    for i in range(1, 200):
        try:
            subject = driver.find_element(By.XPATH, f'//*[@id="DashboardCard_Container"]/div/div[{i}]')
            print(subject.get_attribute('aria-label'))
            target_id.append(i)
        except:
            break
    mute_stat = 0
    for target in target_id:
        driver.find_element(By.XPATH, f'//*[@id="DashboardCard_Container"]/div/div[{target}]').click()
        driver.implicitly_wait(3)
        # XPath로 요소 찾기
        elements = driver.find_elements(By.XPATH, '//*[@id="section-tabs"]/li[@class="section"]')
        # 요소들 중 href 속성에 '140'이 포함된 것을 찾기
        for element in elements:
            # li 요소 내부의 a 태그를 찾기
            a_tag = element.find_element(By.TAG_NAME, 'a')
            href_value = a_tag.get_attribute('href')
            print(href_value)
            # href 속성에 '140'이 포함된 경우 클릭
            if href_value and '140' in href_value:
                a_tag.click()
                break
 
        xpaths = []
        iframe = driver.find_element(By.ID, 'tool_content')
        driver.switch_to.frame(iframe)
 
        mp4_elements = driver.find_elements(By.XPATH,
                                            '//*[contains(@class, "xnmb-module_item-icon mp4") or contains(@class, "xnmb-module_item-icon movie")]/ancestor::div[contains(@class, "xnmb-module_item-wrapper") and not(.//div[@class="xnmb-module_item-right-wrapper"]//span[contains(text(), "완료") or contains(text(), "예정") or contains(text(), "마감됨")])]/div[@class="xnmb-module_item-left-wrapper"]//a[@target="_parent"]')
 
        print(f"{len(mp4_elements)}개의 영상을 찾았습니다.")
        if len(mp4_elements) == 0:
            driver.switch_to.default_content()
            driver.implicitly_wait(3)
            driver.find_element(By.XPATH, '//*[@id="global_nav_dashboard_link"]').click()
 
            continue
 
        mp4_xpaths = []
        for element in mp4_elements:
            xpath = driver.execute_script("""
                var element = arguments[0];
                var paths = [];
                for (; element && element.nodeType == 1; element = element.parentNode)
                {
                    var index = 0;
                    for (var sibling = element.previousSibling; sibling; sibling = sibling.previousSibling)
                    {
                        if (sibling.nodeType == Node.DOCUMENT_TYPE_NODE)
                            continue;
                        if (sibling.nodeName == element.nodeName)
                            ++index;
                    }
                    var tagName = element.nodeName.toLowerCase();
                    var pathIndex = (index ? "[" + (index+1) + "]" : "");
                    paths.splice(0, 0, tagName + pathIndex);
                }
                return paths.length ? "/" + paths.join("/") : null;
                """, element)
 
            mp4_xpaths.append(xpath)
 
        for xpath in mp4_xpaths:
 
            print(driver.find_element(By.XPATH, xpath).text)
            driver.find_element(By.XPATH, xpath).click()
            driver.switch_to.default_content()
            driver.implicitly_wait(5)
            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()
                print("팝업 무시 완료")
            except:
                print("팝업 없음")
            driver.implicitly_wait(5)
            time.sleep(2)
            first_iframe = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'tool_content'))
            )
            driver.switch_to.frame(first_iframe)
 
            second_iframe = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.xnlailvc-commons-frame'))
            )
            driver.switch_to.frame(second_iframe)
 
            driver.find_element(By.XPATH, '//*[@id="front-screen"]/div/div[2]/div[1]/div').click()
            time.sleep(4)
            try:
                driver.find_element(By.XPATH, '//*[@id="confirm-dialog"]/div/div/div[2]/div[1]').click()
            except:
                print("최초 재생으로 감지되었습니다.")
 
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, '//*[@id="confirm-dialog"]/div/div/div[2]/div[1]').click()
            except:
                print("다른 곳에서 재생중이지 않군요")
 
 
            while True:
                check = driver.find_element(By.XPATH, '//*[@id="player-center-control"]/div/div')
                style_attribute = check.get_attribute('style')
 
                if style_attribute:
                    break
                else:
                    time.sleep(1)
 
            print("\r 비디오 재생이 멈췄습니다.")
            driver.switch_to.default_content()
            elements = driver.find_elements(By.XPATH, '//*[@id="section-tabs"]/li[@class="section"]')
            # 요소들 중 href 속성에 '140'이 포함된 것을 찾기
            for element in elements:
                # li 요소 내부의 a 태그를 찾기
                a_tag = element.find_element(By.TAG_NAME, 'a')
                href_value = a_tag.get_attribute('href')
                print(href_value)
                # href 속성에 '140'이 포함된 경우 클릭
                if href_value and '140' in href_value:
                    a_tag.click()
                    break
            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()
                print("팝업 무시 완료")
            except:
                print("팝업 없음")
            driver.implicitly_wait(5)
            iframe = driver.find_element(By.ID, 'tool_content')
            driver.switch_to.frame(iframe)
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            print("팝업 무시 완료")
        except:
            print("팝업 없음")
        driver.switch_to.default_content()
        driver.implicitly_wait(3)
        driver.find_element(By.XPATH, '//*[@id="global_nav_dashboard_link"]').click()
 
    print("완료!")
 
finally:
    # Close the browser
    time.sleep(1)
    driver.quit()
    time.sleep(10)
