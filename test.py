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
options.add_argument('--lang=zh-TW')

# 初始化瀏覽器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
try:
    driver.get("https://auth.mayohr.com/HRM/Account/Login")

    username = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "userName"))
    )
    username.send_keys(USERNAME)
    password = driver.find_element(By.NAME, "password")
    password.send_keys(PASSWORD)
    driver.find_element(By.CLASS_NAME, "submit-btn").click()

    WebDriverWait(driver, 15).until(
        lambda driver: "Login" not in driver.current_url
    )
    print("登入成功，當前頁面: {driver.current_url}")
    
    attendance_link = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Attendance"))
    )
    attendance_link.click()

    print("已點擊 Attendance 連結")
    
    # 5. 等待頁面載入
    time.sleep(3)
    print(f"Attendance 頁面 URL: {driver.current_url}")
    
    punch_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ta-link-btn:nth-of-type(2)"))
    )
    punch_button.click()
    print("已點擊打卡按鈕")
    
    # 抓取第一個 class 包含 ta_btn 的 button
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ta_btn:nth-of-type(1)"))
    )
    if button.is_enabled():
        button.click()
        print("第一個按鈕已點擊")
    else:
        print("第一個按鈕處於禁用狀態，無法點擊")
        
except Exception as e:
    print("發生錯誤：{e}")


finally:
    driver.quit() 
