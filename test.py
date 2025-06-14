from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

# 初始化 Chrome 瀏覽器，設置 headless 模式以適應 GitHub Actions
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 無頭模式
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 初始化瀏覽器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
try:
    driver.get("https://auth.mayohr.com/HRM/Account/Login")

    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "userName"))
    )
    username.send_keys(USERNAME)
    password = driver.find_element(By.NAME, "password")
    password.send_keys(PASSWORD)
    driver.find_element(By.CLASS_NAME, "submit-btn").click()

    
    attendance_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Attendance"))
    )
    attendance_link.click()

    print("已點擊 Attendance 連結")
    
    punch_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Check in/out']/ancestor::div[@class='ta-link-btn']"))
    )

    punch_button.click()
    print("已點擊打卡按鈕")
    
    # 抓取第一個 class 包含 ta_btn 的 button
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'on duty') or contains(., 'clock out')]"))
    )
    if button.is_enabled():
        button.click()
        print("第一個按鈕已點擊")
    else:
        print("第一個按鈕處於禁用狀態，無法點擊")
        
except Exception as e:
    print(f"發生錯誤：{e}")


finally:
    driver.quit() 
