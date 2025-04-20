import os
import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# 用戶配置
ACCOUNT_PAIRS = [
    {
        "account1": {
            "phone": "+85296689941",
            "name": "圓圓",
            "profile_dir": "Profile_1",
            "active": True,
            "partner": "小璃",  # 對話夥伴
            "channels": ["WhatsApp", "TVB"]  # 新增：訂閱的頻道列表
        },
        "account2": {
            "phone": None,
            "name": "小璃😊",
            "profile_dir": "Profile_2",
            "active": True,
            "partner": "圓圓",  # 對話夥伴
            "channels":  ["WhatsApp", "TVB"]  # 新增：訂閱的頻道列表
        }
    },
    {
        "account1": {
            "phone": None,
            "name": "機8",
            "profile_dir": "Profile_3",
            "active": True,
            "partner": "挪威",  # 對話夥伴
            "channels":  ["WhatsApp", "TVB"]   # 新增：訂閱的頻道列表
        },
        "account2": {
            "phone": None,
            "name": "機6",
            "profile_dir": "Profile_4",
            "active": True,
            "partner": "芭蕉",  # 對話夥伴
            "channels":  ["WhatsApp", "TVB"]  # 新增：訂閱的頻道列表
        }}
]


# 對話內容庫 (按場景分類)
CONVERSATIONS = {
    "日常問候": [
        ("早安！今天天氣真好", "對啊，陽光很舒服，你準備出門嗎？"),
        ("晚安，今天過得怎麼樣？", "還不錯，剛追完一部劇，你呢？"),
        ("午安，吃過飯了嗎？", "剛吃完，今天吃了牛肉麵，你呢？"),
        ("週末愉快！有什麼計劃嗎？", "可能在家休息，最近太累了，你呢？"),
        ("好久不見！最近忙什麼？", "工作有點忙，不過還算充實，你呢？")
    ],
    "工作學習": [
        ("今天開了一整天的會，好累", "辛苦了！我們今天也是會議馬拉松"),
        ("專案終於告一段落了", "恭喜啊！要不要慶祝一下？"),
        ("最近在學做簡報，好難", "推薦你看一些TED演講，很有幫助"),
        ("明天要報告，好緊張", "加油！你準備得很充分了"),
        ("公司來了新同事，感覺不錯", "是嗎？是什麼部門的？")
    ],
    "興趣愛好": [
        ("我最近迷上露營", "真的嗎？有沒有推薦的營地？"),
        ("你看過最近很火的那部韓劇嗎？", "有啊！最喜歡裡面的男主角"),
        ("我開始學彈吉他了", "好厲害！學了多久了？"),
        ("週末去看了美術展", "是什麼主題的展覽？"),
        ("我收集了很多咖啡豆", "你最喜歡哪個產地的？")
    ],
    "生活分享": [
        ("我家狗狗學會新把戲了", "好可愛！是什麼把戲？"),
        ("今天煮的咖哩大成功", "聽起來很棒！用的什麼秘方？"),
        ("手機摔壞了，好鬱悶", "啊...資料有備份嗎？"),
        ("發現一家超好吃的早午餐", "在哪裡？求推薦！"),
        ("颱風要來了，記得做好防颱", "謝謝提醒，你也小心")
    ],
    "美食話題": [
        ("你吃過最近很紅的舒芙蕾鬆餅嗎？", "還沒，聽說要排隊很久？"),
        ("推薦你一家超道地的日本拉麵", "在哪裡？我超愛吃拉麵的！"),
        ("自己嘗試做蛋糕失敗了", "烘焙真的需要多練習呢"),
        ("不敢吃香菜，覺得味道好奇怪", "真的嗎？我覺得很提味耶"),
        ("最喜歡哪種異國料理？", "泰國菜，尤其是酸辣湯")
    ],
    "旅遊經歷": [
        ("下個月要去日本玩", "好羨慕！打算去哪些地方？"),
        ("上次去澎湖玩超開心", "最推薦哪個景點？"),
        ("你有推薦的旅行背包嗎？", "我用的這個牌子很不錯，容量大又輕"),
        ("出差去上海，有什麼必吃？", "小籠包絕對不能錯過"),
        ("最難忘的旅行是哪次？", "去年在冰島看極光，美到哭")
    ],
    "科技3C": [
        ("換了新手機，還在適應系統", "什麼型號的？用起來順嗎？"),
        ("我的筆電又當機了", "要不要試試重灌系統？"),
        ("你用哪款無線耳機？", "我用AirPods Pro，降噪效果不錯"),
        ("怎麼備份照片最方便？", "我都用Google相簿，自動備份"),
        ("有沒有推薦的平板？", "看需求，iPad還是最穩定")
    ],
    "健康生活": [
        ("開始健身一個月了", "感覺如何？有看到效果嗎？"),
        ("最近睡不太好", "試試喝溫牛奶或聽輕音樂"),
        ("感冒了，喉嚨好痛", "多休息，喝點蜂蜜水"),
        ("你平常都怎麼減壓？", "我會做瑜伽或去散步"),
        ("飲食控制好難堅持", "慢慢來，偶爾放鬆一下沒關係")
    ],
    "時事新聞": [
        ("看到昨天那則新聞了嗎？", "你說的是哪一則？"),
        ("油價又要漲了", "唉...什麼都漲就是薪水不漲"),
        ("選舉快到了，好熱鬧", "希望這次能有些改變"),
        ("那個新政策你怎麼看？", "我覺得立意不錯但執行有難度"),
        ("奧運看了嗎？超精彩的", "有！那個體操選手太強了")
    ],
    "幽默搞笑": [
        ("我剛剛把鹽和糖搞混了", "哈哈哈，那杯咖啡還好嗎？"),
        ("你知道為什麼電腦很笨嗎？", "為什麼？因為它只有二進位思考"),
        ("我養的植物又死了", "你是植物殺手嗎？這是第幾盆了？"),
        ("今天穿兩隻不同顏色的襪子", "這是新潮流嗎？我也要試試"),
        ("我以為今天星期五...", "我也常這樣，然後發現才星期三超崩潰")
    ]
}

CHANNEL_CONFIG = {
    "browse_time_range": (20, 60),  # 適度延長瀏覽時間
    "like_probability": 0.8,
    "scroll_probability": 0.7,
    "max_posts_to_view": 2,  # 減少貼文數量
    "min_time_between_actions": 2,
    "max_time_between_actions": 5
}

# 模擬打錯字和修正
def make_typos(text):
    if random.random() < 0.3:  # 30%機率打錯字
        typo_pos = random.randint(0, len(text)-1)
        typo_char = chr(ord(text[typo_pos]) + random.randint(1, 3))
        text = text[:typo_pos] + typo_char + text[typo_pos+1:]
        
        # 模擬刪除錯誤字
        backspaces = random.randint(1, 3)
        return (text, backspaces)
    return (text, 0)

# 高度模擬人類輸入
def human_type(element, text):
    # 隨機決定輸入速度 (字元間隔0.1-0.5秒)
    speed = random.uniform(0.1, 0.5)
    
    # 模擬打錯字
    text_with_typo, backspaces = make_typos(text)
    
    # 先輸入可能包含錯字的文本
    for i, char in enumerate(text_with_typo):
        element.send_keys(char)
        
        # 隨機加入不規則停頓 (10%機率)
        if random.random() < 0.1:
            time.sleep(random.uniform(0.2, 1.0))
        
        time.sleep(speed)
    
    # 模擬發現錯字並修正
    if backspaces > 0:
        time.sleep(random.uniform(0.5, 1.5))  # 發現錯字前的停頓
        
        for _ in range(backspaces):
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.1, 0.3))
        
        # 重新輸入正確字元
        correct_part = text[-backspaces:] if backspaces > 0 else ""
        for char in correct_part:
            element.send_keys(char)
            time.sleep(speed * 0.8)  # 修正時輸入稍快
    
    # 發送前的思考時間
    time.sleep(random.uniform(0.5, 2.0))

# 模擬人類滾動行為
def human_scroll(driver, scroll_distance=None):
    if scroll_distance is None:
        scroll_distance = random.randint(200, 800)
    
    # 模擬人類滾動方式 (非一次性滾動)
    steps = random.randint(3, 8)
    step_size = scroll_distance // steps
    
    for i in range(steps):
        # 每次滾動的距離稍有不同
        current_step = step_size + random.randint(-50, 50)
        driver.execute_script(f"window.scrollBy(0, {current_step})")
        
        # 滾動間隔時間
        time.sleep(random.uniform(0.2, 1.0))
    
    # 滾動後隨機停留時間
    time.sleep(random.uniform(1.0, 3.0))

# 初始化瀏覽器 (增強防偵測)
def init_driver(profile_dir):
    chrome_options = Options()
    
    # 設置用戶數據目錄
    user_data_dir = os.path.join(os.getcwd(), profile_dir)
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    
    # 防偵測設置
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    
    # 隨機用戶代理
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # 隨機視窗大小
    width = random.randint(1000, 1400)
    height = random.randint(700, 900)
    chrome_options.add_argument(f"--window-size={width},{height}")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 修改webdriver屬性
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh']
                });
            """
        })
        
        return driver
    except Exception as e:
        print(f"初始化瀏覽器失敗: {str(e)}")
        return None

# 登入WhatsApp (增加隨機操作)
def login_whatsapp(driver, phone_number):
    try:
        driver.get("https://web.whatsapp.com/")
        
        print("請掃描QR碼登入...")
        
        # 模擬人類等待行為
        for _ in range(random.randint(3, 6)):
            time.sleep(5 + random.random() * 10)
            
            # 隨機移動鼠標
            if random.random() < 0.3:
                driver.execute_script("window.scrollBy(0, %d)" % random.randint(-50, 50))
        
        # 等待登入完成
        try:
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
            )
            print("登入成功！")
            
            # 登入後隨機瀏覽
            time.sleep(random.uniform(2, 5))
            if random.random() < 0.5:
                driver.execute_script("window.scrollBy(0, %d)" % random.randint(100, 300))
            
            return True
        except TimeoutException:
            print("登入超時，請重試")
            return False
    except Exception as e:
        print(f"登入過程中發生錯誤: {str(e)}")
        return False

# 發送消息 (增強模擬)
def send_message(driver, contact_name, message):
    try:
        # 隨機決定是否使用搜索
        if random.random() < 0.8:  # 80%使用搜索
            # 查找聯繫人
            search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            
            # 模擬人類輸入搜索
            human_type(search_box, contact_name)
            time.sleep(random.uniform(0.5, 1.5))
            
            # 點擊聯繫人
            try:
                contact = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]'))
                )
                contact.click()
                time.sleep(random.uniform(0.5, 2.0))
            except:
                print(f"找不到聯繫人: {contact_name}")
                # 清除搜索框
                search_box.send_keys(Keys.CONTROL + "a")
                search_box.send_keys(Keys.BACKSPACE)
                return False
        else:  # 20%直接從聊天列表點擊
            try:
                contacts = driver.find_elements(By.XPATH, '//span[@class="ggj6brxn gfz4du6o r7fjleex g0rxnol2 lhj4utae le5p0ye3 l7jjieqr _11JPr"]')
                for contact in contacts:
                    if contact_name in contact.text:
                        contact.click()
                        time.sleep(random.uniform(0.5, 2.0))
                        break
            except:
                return False
        
        # 發送消息
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        
        human_type(message_box, message)
        
        # 隨機決定是否添加表情
        if random.random() < 0.2:  # 20%機率加表情
            time.sleep(random.uniform(0.5, 1.0))
            emoji_button = driver.find_element(By.XPATH, '//div[@data-testid="conversation-emoji-btn"]')
            emoji_button.click()
            time.sleep(random.uniform(0.3, 0.8))
            
            emojis = driver.find_elements(By.XPATH, '//div[@data-testid="emoji-item"]')
            if emojis:
                random.choice(emojis).click()
                time.sleep(random.uniform(0.2, 0.5))
        
        # 隨機決定是否取消發送
        if random.random() < 0.05:  # 5%機率取消發送
            time.sleep(random.uniform(1.0, 3.0))
            message_box.send_keys(Keys.ESCAPE)
            print(f"取消發送給 {contact_name} 的消息")
            time.sleep(random.uniform(1.0, 2.0))
            return False
        else:
            message_box.send_keys(Keys.RETURN)
            print(f"已發送消息給 {contact_name}: {message}")
        
        # 隨機瀏覽其他聊天
        if random.random() < 0.3:  # 30%機率瀏覽其他聊天
            time.sleep(random.uniform(1.0, 3.0))
            chats = driver.find_elements(By.XPATH, '//div[@class="_21S-L"]')
            if chats:
                random.choice(chats).click()
                time.sleep(random.uniform(2.0, 5.0))
        
        return True
        
    except Exception as e:
        print(f"發送消息時出錯: {str(e)}")
        return False

def browse_channels(driver, account):
    try:
        print(f"{account['name']} 開始瀏覽頻道...")
        
        # 嘗試多種方式定位頻道按鈕
        channel_buttons = []
        possible_channel_buttons = [
            '//span[@data-icon="newsletter-outline"]',  # 根據您提供的SVG圖標
            '//div[@role="button" and .//*[@data-icon="newsletter-outline"]]',  # 包含圖標的按鈕
            '//div[@aria-label="頻道"]',  # 原始定位
            '//div[@role="tab" and contains(@aria-label, "頻道")]'  # 可能的標籤形式
        ]
        
        for xpath in possible_channel_buttons:
            try:
                buttons = driver.find_elements(By.XPATH, xpath)
                if buttons:
                    print(f"找到 {len(buttons)} 個匹配的頻道按鈕 (XPath: {xpath})")
                    channel_buttons.extend(buttons)
            except Exception as e:
                print(f"嘗試定位頻道按鈕時出錯 (XPath: {xpath}): {str(e)}")
        
        if not channel_buttons:
            print("找不到頻道按鈕，嘗試使用搜索功能直接進入頻道")
            return browse_channel_via_search(driver, account)
        
        # 選擇最可能是頻道按鈕的元素
        channel_button = channel_buttons[0]
        
        # 確保按鈕可見並可點擊
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", channel_button)
        time.sleep(1)
        
        # 使用ActionChains模擬更自然的點擊
        ActionChains(driver).move_to_element(channel_button).pause(0.5).click().perform()
        print("已點擊頻道按鈕")
        time.sleep(random.uniform(2.0, 4.0))
        
        # 隨機選擇要瀏覽的頻道
        channels_to_browse = random.sample(account['channels'], min(len(account['channels']), 1))  # 每次只瀏覽1個頻道
        
        for channel in channels_to_browse:
            try:
                print(f"{account['name']} 正在瀏覽頻道: {channel}")
                
                # 搜索並進入頻道
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                )
                search_box.clear()
                human_type(search_box, channel)
                time.sleep(random.uniform(1.5, 3.0))
                
                # 點擊頻道
                try:
                    channel_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'//span[contains(@title, "{channel}")]'))
                    )
                    channel_element.click()
                    time.sleep(random.uniform(2.0, 4.0))
                    
                    # 瀏覽內容
                    browse_time = random.randint(*CHANNEL_CONFIG["browse_time_range"])
                    start_time = time.time()
                    
                    while time.time() - start_time < browse_time:
                        if random.random() < CHANNEL_CONFIG["scroll_probability"]:
                            human_scroll(driver, random.randint(300, 600))
                        
                        # 嘗試按讚
                        if random.random() < CHANNEL_CONFIG["like_probability"]:
                            try:
                                like_buttons = driver.find_elements(By.XPATH, '//div[@role="button" and @aria-label="讚好"]')
                                if like_buttons:
                                    random.choice(like_buttons).click()
                                    print(f"{account['name']} 已按讚")
                                    time.sleep(random.uniform(1.0, 2.0))
                            except:
                                pass
                        
                        time.sleep(random.uniform(
                            CHANNEL_CONFIG["min_time_between_actions"],
                            CHANNEL_CONFIG["max_time_between_actions"]
                        ))
                    
                    print(f"{account['name']} 已完成瀏覽頻道: {channel}")
                    
                except Exception as e:
                    print(f"找不到頻道: {channel} - {str(e)}")
                    # 清除搜索框
                    search_box.send_keys(Keys.CONTROL + "a")
                    search_box.send_keys(Keys.BACKSPACE)
                    continue
                
            except Exception as e:
                print(f"瀏覽頻道 {channel} 時出錯: {str(e)}")
                continue
        
        # 返回主界面
        try:
            main_buttons = driver.find_elements(By.XPATH, '//div[@role="button" and @aria-label="返回"]')
            if main_buttons:
                main_buttons[0].click()
            else:
                driver.back()
            time.sleep(random.uniform(1.0, 3.0))
        except:
            pass
        
        print(f"{account['name']} 完成頻道瀏覽")
        return True
        
    except Exception as e:
        print(f"瀏覽頻道過程中發生錯誤: {str(e)}")
        traceback.print_exc()
        return False

# 獲取對話對
def get_conversation():
    category = random.choice(list(CONVERSATIONS.keys()))
    conversation = random.choice(CONVERSATIONS[category])
    return conversation

import traceback  # 新增導入

# 修改後的帳號線程函數
def account_thread(account):
    print(f"初始化帳號 {account['name']}...")
    
    driver = None
    try:
        driver = init_driver(account["profile_dir"])
        if not driver:
            account["active"] = False
            return
        
        if not login_whatsapp(driver, account["phone"]):
            account["active"] = False
            if driver:
                driver.quit()
            return
        
        time.sleep(random.randint(5, 15))
        
        last_activity = {
            'time': time.time(),
            'type': None  # 'chat' or 'channel'
        }
        
        error_count = 0
        MAX_ERROR_COUNT = 5
        
        while account["active"] and error_count < MAX_ERROR_COUNT:
            try:
                current_time = time.time()
                
                # 決定活動類型 (優先保持對話連貫性)
                if last_activity['type'] is None or \
                   (last_activity['type'] == 'channel' and current_time - last_activity['time'] > 3600):
                    activity_type = 'chat'
                else:
                    activity_type = random.choices(['chat', 'channel'], weights=[70, 30])[0]
                
                if activity_type == 'chat':
                    print(f"\n{account['name']} 開始與 {account['partner']} 對話")
                    
                    try:
                        conversation = get_conversation()
                        my_message = conversation[0] if random.random() < 0.5 else conversation[1]
                        
                        if send_message(driver, account["partner"], my_message):
                            last_activity = {'time': time.time(), 'type': 'chat'}
                            sleep_time = random.randint(180, 600)
                            error_count = 0  # 重置錯誤計數
                        else:
                            sleep_time = random.randint(30, 60)
                            error_count += 1
                    except Exception as e:
                        print(f"{account['name']} 對話時發生錯誤: {str(e)}")
                        traceback.print_exc()
                        sleep_time = random.randint(60, 120)
                        error_count += 1
                        continue
                else:
                    print(f"\n{account['name']} 開始瀏覽頻道")
                    
                    try:
                        if browse_channels(driver, account):
                            last_activity = {'time': time.time(), 'type': 'channel'}
                            sleep_time = random.randint(1200, 2400)
                            error_count = 0  # 重置錯誤計數
                        else:
                            sleep_time = random.randint(60, 120)
                            error_count += 1
                    except Exception as e:
                        print(f"{account['name']} 瀏覽頻道時發生錯誤: {str(e)}")
                        traceback.print_exc()
                        sleep_time = random.randint(60, 120)
                        error_count += 1
                        continue
                
                print(f"{account['name']} 等待 {sleep_time//60} 分 {sleep_time%60} 秒後繼續... (錯誤計數: {error_count})")
                
                # 更安全的等待方式
                end_time = time.time() + sleep_time
                while time.time() < end_time and account["active"]:
                    time.sleep(min(1, end_time - time.time()))
                
            except KeyboardInterrupt:
                account["active"] = False
                print(f"{account['name']} 收到停止信號")
            except Exception as e:
                print(f"{account['name']} 發生未捕獲的錯誤: {str(e)}")
                traceback.print_exc()
                error_count += 1
                time.sleep(10)
        
        if error_count >= MAX_ERROR_COUNT:
            print(f"{account['name']} 達到最大錯誤次數({MAX_ERROR_COUNT})，停止運行")
    
    except Exception as e:
        print(f"{account['name']} 發生嚴重錯誤: {str(e)}")
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        print(f"{account['name']} 線程結束")

# 主程序
def main():
    threads = []
    
    try:
        # 為每個帳號創建線程
        for pair in ACCOUNT_PAIRS:
            for account_key in ["account1", "account2"]:
                account = pair[account_key]
                thread = threading.Thread(target=account_thread, args=(account,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                time.sleep(random.uniform(3, 8))  # 隨機間隔啟動
        
        # 監控線程
        while True:
            time.sleep(1)
            active_accounts = sum(1 for pair in ACCOUNT_PAIRS 
                                for account_key in ["account1", "account2"] 
                                if pair[account_key]["active"])
            
            if active_accounts == 0:
                print("所有帳號都已停止")
                break
                
    except KeyboardInterrupt:
        print("\n收到停止信號，準備退出...")
        for pair in ACCOUNT_PAIRS:
            for account_key in ["account1", "account2"]:
                pair[account_key]["active"] = False
        
        # 等待所有線程結束
        for thread in threads:
            thread.join(timeout=10)
        
    finally:
        print("程序結束")

if __name__ == "__main__":
    main()