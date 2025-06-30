from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class Scrabber:
    def __init__(self, path):
        # 設定 Chrome 選項
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--mute-audio")  # 靜音所有音訊
        chrome_options.add_argument("--disable-audio")  # 停用音訊
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # 停用音訊相關功能
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # 設定媒體播放偏好
        prefs = {
            "profile.default_content_setting_values": {
                "media_stream": 2,  # 禁用媒體流
            },
            "profile.content_settings.exceptions.media_stream": {}
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 使用 webdriver-manager 自動管理 ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.url = path
        self.svg_xpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div[2]/div/div[2]/ytd-player/div/div/div[31]/div[1]/div[1]/div[2]"

    def get_svg(self):
        """
        Get the SVG data from the YouTube video page.
        Returns:
            dict: A dictionary containing path_elements and chapter_widths.
        """
        # 多種可能的選擇器
        selectors = [
            ".ytp-heat-map-path",
            ".ytp-heat-map-svg path",
            "svg.ytp-heat-map-svg path",
            ".ytp-progress-bar-container .ytp-heat-map-path",
            ".ytp-progress-bar .ytp-heat-map-path"
        ]
        
        for selector in selectors:
            try:
                print(f"🔍 嘗試選擇器: {selector}")
                
                # 等待元素出現
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # 獲取所有匹配的元素
                path_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if path_elements:
                    print(f"✅ 找到 {len(path_elements)} 個元素")
                    print(f"元素內容: {path_elements}")
                    
                    svg_data = {
                        'path_elements': path_elements,
                        'chapter_widths': []
                    }
                    
                    if len(path_elements) > 1:
                        svg_data['chapter_widths'] = self.get_chapter_widths()
                    
                    return svg_data  # 找到元素後立即返回，停止繼續尋找
                    
            except TimeoutException:
                print(f"⏰ 選擇器 {selector} 超時")
                continue
            except Exception as e:
                print(f"❌ 選擇器 {selector} 出錯: {str(e)}")
                continue
    
        # 如果所有選擇器都失敗，返回空的結果
        print("❌ 所有選擇器都無法找到元素")
        return {
            'path_elements': [],
            'chapter_widths': []
        }
        
    def get_chapter_widths(self):
        """
        Get the widths of the chapters from the YouTube video page.
        Returns:
            list: A list of chapter widths.
        """
        try:
            print("🔍 尋找章節容器元素...")
            
            # 等待元素出現
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-chapter-hover-container"))
            )
            
            # 獲取所有章節容器元素
            chapter_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-chapter-hover-container")
            
            if not chapter_elements:
                print("❌ 沒有找到章節容器元素")
                return []
            
            print(f"✅ 找到 {len(chapter_elements)} 個章節容器")
            
            chapter_widths = []
            for i, element in enumerate(chapter_elements):
                try:
                    # 方法1: 從 style 屬性中解析 width
                    style_attr = element.get_attribute("style")
                    width_value = None
                    
                    if style_attr and "width:" in style_attr:
                        import re
                        width_match = re.search(r'width:\s*(\d+(?:\.\d+)?)px', style_attr)
                        if width_match:
                            width_value = float(width_match.group(1))
                            print(f"📏 第 {i+1} 個容器 (style): {width_value}px")
                    
                    # 方法2: 如果 style 中沒有，使用 Selenium 的 size 屬性
                    if width_value is None:
                        selenium_width = element.size['width']
                        if selenium_width > 0:
                            width_value = selenium_width
                            print(f"📏 第 {i+1} 個容器 (size): {width_value}px")
                    
                    # 方法3: 使用 JavaScript 獲取計算樣式
                    if width_value is None:
                        js_width = self.driver.execute_script(
                            "return window.getComputedStyle(arguments[0]).width;", 
                            element
                        )
                        if js_width and js_width != 'auto':
                            width_value = float(js_width.replace('px', ''))
                            print(f"📏 第 {i+1} 個容器 (computed): {width_value}px")
                    
                    if width_value is not None:
                        chapter_widths.append(width_value)
                    else:
                        print(f"⚠️ 無法獲取第 {i+1} 個容器的 width")
                        
                except Exception as e:
                    print(f"❌ 處理第 {i+1} 個容器時出錯: {str(e)}")
                    continue
            
            print(f"🎯 成功獲取 {len(chapter_widths)} 個 width 值: {chapter_widths}")
            return chapter_widths
            
        except TimeoutException:
            print("⏰ 等待章節容器元素超時")
            return []
        except NoSuchElementException:
            print("❌ 沒有找到章節元素")
            return []
        except Exception as e:
            print(f"❌ 獲取章節 width 時出錯: {str(e)}")
            return []

    def scrab(self):
        """
        Scrape the SVG data from the YouTube video page.
        Returns:
            dict: A dictionary containing SVG path elements and chapter widths.
        """
        try:
            print("🚀 開始抓取 YouTube 影片數據...")
            
            # 1. 載入影片頁面
            print("📄 載入影片頁面...")
            self.driver.get(self.url)
            
            # 2. 等待頁面載入
            print("⏳ 等待頁面載入...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "html5-video-player"))
            )
            print("✅ 頁面載入完成")
            
            # 3. 嘗試開始播放影片
            print("▶️ 嘗試開始播放影片...")
            self._try_start_video()
            
            # 4. 等待 SVG 元素出現
            print("🎨 等待熱度圖元素出現...")
            time.sleep(10)  # 給足夠時間讓熱度圖載入
            
            # 5. 獲取 SVG 數據
            print("🔍 搜尋熱度圖數據...")
            svg_data = self.get_svg()
            
            # 6. 返回結果
            if svg_data and svg_data.get('path_elements'):
                print(f"✅ 成功獲取 SVG 數據，包含 {len(svg_data['path_elements'])} 個元素")
                return svg_data
            else:
                print("❌ 未找到有效的 SVG 數據")
                return {
                    'path_elements': [],
                    'chapter_widths': []
                }
                
        except Exception as e:
            print(f"❌ 抓取數據時發生錯誤: {e}")
            return {
                'path_elements': [],
                'chapter_widths': []
            }

    def _try_start_video(self):
        """
        嘗試開始播放影片（只會執行一次）
        """
        if hasattr(self, 'video_started') and self.video_started:
            print("影片已經開始播放，跳過")
            return
            
        try:
            play_button = self.driver.find_element(By.CLASS_NAME, "ytp-large-play-button")
            play_button.click()
            print("✅ 影片開始播放")
            self.video_started = True
        except Exception as e:
            print(f"⚠️ 無法點擊播放按鈕: {e}")
            print("繼續執行（可能影片已經在播放）")
            self.video_started = True