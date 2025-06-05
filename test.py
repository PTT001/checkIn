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
    
    # 5. 等待 SPA 頁面內容載入
    print("等待頁面內容載入...")
    time.sleep(5)  # 增加等待時間
    print(f"Attendance 頁面 URL: {driver.current_url}")
    
    # 等待 JavaScript 執行完成，查找任何可點擊的元素
    WebDriverWait(driver, 20).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )
    
    # 額外等待動態內容載入
    time.sleep(3)
    
    # 6. 檢查是否有 iframe
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print(f"發現 {len(iframes)} 個 iframe")
        for i, iframe in enumerate(iframes):
            try:
                driver.switch_to.frame(iframe)
                print(f"切換到 iframe {i}")
                break
            except:
                continue
    
    # 7. 嘗試找到打卡相關元素 - 擴大搜尋範圍
    punch_card_element = None
    
    # 更廣泛的選擇器，包括英文和中文
    selectors = [
        # 中文打卡相關
        (By.XPATH, "//*[contains(text(), '我要打卡')]"),
        (By.XPATH, "//*[contains(text(), '打卡')]"),
        (By.XPATH, "//*[contains(text(), '上班')]"),
        (By.XPATH, "//*[contains(text(), '下班')]"),
        (By.XPATH, "//*[contains(text(), '出勤')]"),
        # 英文 punch/clock 相關
        (By.XPATH, "//*[contains(text(), 'Punch')]"),
        (By.XPATH, "//*[contains(text(), 'Clock')]"),
        (By.XPATH, "//*[contains(text(), 'Check')]"),
        (By.XPATH, "//*[contains(text(), 'Time')]"),
        # 按鈕類型
        (By.XPATH, "//button[contains(@class, 'punch')]"),
        (By.XPATH, "//button[contains(@class, 'clock')]"),
        (By.XPATH, "//a[contains(@class, 'punch')]"),
        (By.XPATH, "//a[contains(@class, 'clock')]"),
    ]
    
    for selector_type, selector_value in selectors:
        try:
            punch_card_element = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((selector_type, selector_value))
            )
            print(f"找到打卡元素，使用選擇器: {selector_value}")
            break
        except TimeoutException:
            continue
    
    if punch_card_element is None:
        # 如果都找不到，印出更詳細的除錯資訊
        print("找不到打卡按鈕，開始詳細除錯...")
        print(f"當前頁面標題: {driver.title}")
        print(f"當前 URL: {driver.current_url}")
        
        # 等待更長時間讓頁面完全載入
        print("等待更長時間讓頁面載入...")
        time.sleep(10)
        
        # 檢查頁面是否有任何文字內容
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"頁面文字內容長度: {len(body_text)}")
        if len(body_text) > 0:
            print(f"頁面部分文字內容: {body_text[:500]}...")
        
        # 尋找所有可點擊的元素
        clickable_elements = driver.find_elements(By.XPATH, "//button | //a | //*[@onclick] | //*[contains(@class, 'btn')] | //*[contains(@class, 'button')]")
        print(f"找到 {len(clickable_elements)} 個可點擊元素:")
        for i, elem in enumerate(clickable_elements[:10]):  # 只顯示前10個
            try:
                tag = elem.tag_name
                text = elem.text.strip()
                classes = elem.get_attribute('class') or ''
                onclick = elem.get_attribute('onclick') or ''
                print(f"  {i+1}. 標籤: {tag}, 文字: '{text}', class: '{classes}', onclick: '{onclick}'")
            except Exception as e:
                print(f"  {i+1}. 無法讀取元素: {str(e)}")
        
        # 尋找所有包含特定關鍵字的元素
        keywords = ['打卡', '上班', '下班', '出勤', 'punch', 'clock', 'check', 'time', 'attendance']
        for keyword in keywords:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
            if elements:
                print(f"包含 '{keyword}' 的元素: {len(elements)} 個")
                for elem in elements[:3]:  # 只顯示前3個
                    try:
                        print(f"  - {elem.tag_name}: '{elem.text}' (可見: {elem.is_displayed()})")
                    except:
                        pass
        
        # 截圖除錯
        driver.save_screenshot("debug_attendance_page.png")
        print("已保存除錯截圖: debug_attendance_page.png")
        
        # 印出更多 HTML 內容
        print("頁面 HTML 內容:")
        page_source = driver.page_source
        print(f"HTML 總長度: {len(page_source)}")
        print("HTML 片段:")
        print(page_source[:3000])
        
        # 嘗試執行 JavaScript 來查找元素
        try:
            js_result = driver.execute_script("""
                var elements = document.querySelectorAll('*');
                var punchElements = [];
                for (var i = 0; i < elements.length; i++) {
                    var elem = elements[i];
                    var text = elem.textContent || elem.innerText || '';
                    if (text.includes('打卡') || text.includes('上班') || text.includes('下班') || 
                        text.includes('punch') || text.includes('clock')) {
                        punchElements.push({
                            tagName: elem.tagName,
                            text: text.substring(0, 100),
                            className: elem.className,
                            id: elem.id
                        });
                    }
                }
                return punchElements;
            """)
            
            if js_result:
                print(f"JavaScript 找到 {len(js_result)} 個相關元素:")
                for elem in js_result:
                    print(f"  - {elem}")
            else:
                print("JavaScript 沒有找到相關元素")
                
        except Exception as e:
            print(f"JavaScript 執行失敗: {str(e)}")
        
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
