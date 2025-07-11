# YouTube 影片熱度圖生成器 (YouTube Video Heatmap Generator)

這是一個用於自動擷取 YouTube 影片觀看熱度數據並生成視覺化熱度圖的 Python 工具。透過 Selenium 自動化技術，本工具能夠從 YouTube 影片頁面抓取熱度條 (progress bar) 的 SVG 數據，並將其轉換為可視化的熱度圖表。

## 🌟 功能特色

- 🔄 自動抓取 YouTube 影片的觀看熱度數據
- 📊 生成 SVG 格式的熱度圖表
- 🎯 支援單一或多段式熱度條分析
- 🖥️ 無頭瀏覽器模式，後台運行不干擾工作
- 📈 使用 matplotlib 進行數據視覺化

## ⚡ 快速開始

### 環境需求

- Python 3.7 或更高版本
- Google Chrome 瀏覽器
- 穩定的網路連線

### 安裝方法

1. **克隆或下載專案**
   ```bash
   git clone https://github.com/tingjunchen425/yt-heatmap.git
   cd yt-heatmap
   ```

2. **建立虛擬環境 (建議)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安裝相依套件**
   ```bash
   pip install -r requirements.txt
   ```

### 相依套件說明

主要套件包括：
- `selenium` - 網頁自動化工具
- `matplotlib` - 圖表生成
- `webdriver-manager` - 自動管理 ChromeDriver
- `requests` - HTTP 請求處理
- `numpy` - 數值計算支援

## 🏗️ 程式框架

專案採用模組化設計，主要包含以下組件：

```
yt-heatmap/
├── main.py              # 主程式入口
├── scrabber.py          # YouTube 數據抓取模組
├── svgGenerate.py       # SVG 圖表生成模組
├── requirements.txt     # 相依套件清單
├── README.md           # 專案說明文件
└── video_heatmap.svg   # 生成的熱度圖輸出
```

### 模組說明

1. **`main.py`** - 程式主入口
   - 協調各模組的運作
   - 處理 YouTube URL 輸入
   - 執行完整的抓取與生成流程

2. **`scrabber.py`** - 數據抓取器
   - `Scrabber` 類別：管理 Selenium WebDriver
   - 自動化瀏覽器操作
   - 擷取 YouTube 影片熱度條的 SVG 元素

3. **`svgGenerate.py`** - 圖表生成器
   - `svgGenerate` 類別：處理 SVG 數據分析
   - 解析熱度條路徑數據
   - 生成 matplotlib 視覺化圖表

## 📖 使用方法

### 基本使用

1. **修改目標影片 URL**
   
   編輯 `main.py` 中的 `video_url` 變數：
   ```python
   video_url = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
   ```

2. **執行程式**
   ```bash
   python main.py
   ```

3. **查看結果**
   - 程式執行完成後會在當前目錄生成 `video_heatmap.svg`
   - 同時會彈出 matplotlib 視窗顯示圖表

### 進階使用

**自定義 URL 輸入：**
```python
from scrabber import Scrabber
from svgGenerate import svgGenerate

def custom_analysis(url):
    browser = Scrabber(url)
    svg_data = browser.scrab()
    generate = svgGenerate()
    generate.route(svg_data)

# 使用自定義函數
custom_analysis("https://www.youtube.com/watch?v=EXAMPLE")
```

**批次處理多個影片：**
```python
urls = [
    "https://www.youtube.com/watch?v=VIDEO1",
    "https://www.youtube.com/watch?v=VIDEO2",
    "https://www.youtube.com/watch?v=VIDEO3"
]

for url in urls:
    print(f"處理影片: {url}")
    main(url)
```

### 輸out 說明

- **控制台輸出**：顯示抓取進度和 SVG 數據分析結果
- **SVG 檔案**：`video_heatmap.svg` - 向量格式的熱度圖
- **視覺化視窗**：matplotlib 生成的互動式圖表

## ❗ 注意事項

- 確保 Google Chrome 瀏覽器已安裝且為最新版本
- 程式需要網路連線來訪問 YouTube
- 部分影片可能因為地區限制或隱私設定無法抓取數據
- 建議在穩定的網路環境下使用，避免連線超時
- 在youtube影片中，需要一定的觀看次數才會有熱度圖資訊

## 🔧 疑難排解

**常見問題：**

1. **ChromeDriver 相關錯誤**
   - 程式會自動下載對應版本的 ChromeDriver
   - 如遇問題請確認 Chrome 瀏覽器版本

2. **網路連線問題**
   - 檢查網路連線狀態
   - 確認能夠正常訪問 YouTube

3. **權限問題**
   - 確保有足夠權限寫入檔案到當前目錄

## 📜 版權聲明

本工具僅供學習和研究用途，請遵守 YouTube 的使用條款和相關法規。
