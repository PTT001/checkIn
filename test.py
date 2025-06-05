from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
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
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

# 初始化瀏覽器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("開始執行打卡程序...")
    
    # 1. 前往登入頁面
    driver.get("https://auth.mayohr.com/HRM/Account/Login")
    print("已導航到登入頁面")
    
    # 2. 登入
    username = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "userName"))
    )
    username.send_keys(USERNAME)
    print("已輸入用戶名")
    
    password = driver.find_element(By.NAME, "password")
    password.send_keys(PASSWORD)
    print("已輸入密碼")
    
    driver.find_element(By.CLASS_NAME, "submit-btn").click()
    print("已點擊登入按鈕")
    
    # 3. 等待登入完成
    WebDriverWait(driver, 15).until(
        lambda driver: "Login" not in driver.current_url
    )
    print(f"登入成功，當前頁面: {driver.current_url}")
    
    # 4. 點擊 Attendance 連結
    attendance_link = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Attendance"))
    )
    attendance_link.click()
    print("已點擊 Attendance 連結")
    
    # 5. 等待頁面載入
    time.sleep(3)
    print(f"Attendance 頁面 URL: {driver.current_url}")
    
    # 6. 嘗試找到打卡按鈕 - 使用多種選擇器
    punch_card_element = None
    
    # 嘗試不同的選擇器
    selectors = [
        (By.XPATH, "//span[text()='我要打卡']"),
        (By.XPATH, "//*[contains(text(), '我要打卡')]"),
        (By.XPATH, "//button[contains(text(), '我要打卡')]"),
        (By.XPATH, "//a[contains(text(), '我要打卡')]"),
        (By.XPATH, "//*[contains(text(), '打卡')]"),
    ]
    
    for selector_type, selector_value in selectors:
        try:
            punch_card_element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((selector_type, selector_value))
            )
            print(f"找到打卡元素，使用選擇器: {selector_value}")
            break
        except TimeoutException:
            continue
    
    if punch_card_element is None:
        # 如果都找不到，印出除錯資訊
        print("找不到打卡按鈕，開始除錯...")
        print(f"當前頁面標題: {driver.title}")
        
        # 尋找所有包含 '打卡' 的元素
        punch_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '打卡')]")
        print(f"找到 {len(punch_elements)} 個包含'打卡'的元素:")
        for i, elem in enumerate(punch_elements):
            try:
                print(f"  {i+1}. 標籤: {elem.tag_name}, 文字: '{elem.text}', 可見: {elem.is_displayed()}")
            except:
                print(f"  {i+1}. 無法讀取元素資訊")
        
        # 截圖除錯
        driver.save_screenshot("debug_attendance_page.png")
        print("已保存除錯截圖: debug_attendance_page.png")
        
        # 印出部分 HTML 內容
        print("頁面 HTML 片段:")
        print(driver.page_source[:2000])
        
        raise Exception("找不到打卡按鈕")
    
    # 7. 點擊打卡按鈕
    punch_card_element.click()
    print("已點擊打卡按鈕")
    
    # 8. 等待並點擊上班/下班按鈕
    time.sleep(2)
    
    work_button_selectors = [
        (By.XPATH, "//button[span[text()='上班' or text()='下班']]"),
        (By.XPATH, "//button[contains(text(), '上班')]"),
        (By.XPATH, "//button[contains(text(), '下班')]"),
        (By.XPATH, "//*[contains(text(), '上班') or contains(text(), '下班')]"),
    ]
    
    work_button = None
    for selector_type, selector_value in work_button_selectors:
        try:
            work_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((selector_type, selector_value))
            )
            print(f"找到上班/下班按鈕，使用選擇器: {selector_value}")
            break
        except TimeoutException:
            continue
    
    if work_button is None:
        print("找不到上班/下班按鈕，查看可用按鈕...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"頁面上共有 {len(buttons)} 個按鈕:")
        for i, btn in enumerate(buttons):
            try:
                print(f"  {i+1}. 按鈕文字: '{btn.text}', 可見: {btn.is_displayed()}")
            except:
                print(f"  {i+1}. 無法讀取按鈕資訊")
        
        driver.save_screenshot("debug_punch_buttons.png")
        raise Exception("找不到上班/下班按鈕")
    
    work_button.click()
    print("已點擊上班/下班按鈕")
    
    # 9. 等待操作完成
    time.sleep(2)
    print("打卡操作完成！")
    
except Exception as e:
    print(f"發生錯誤: {str(e)}")
    print(f"當前頁面 URL: {driver.current_url}")
    
    # 最終除錯截圖
    try:
        driver.save_screenshot("final_error_screenshot.png")
        print("已保存錯誤截圖: final_error_screenshot.png")
    except:
        pass
    
    raise

finally:
    driver.quit()
    print("瀏覽器已關閉")

finally:
    driver.quit()
