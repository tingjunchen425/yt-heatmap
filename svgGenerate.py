import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d, CubicSpline

class svgGenerate:
    def route(self, svg_data):
        elements = svg_data['path_elements']
        chapter_widths = svg_data['chapter_widths']
        if len(elements) == 0:
            print("No SVG elements found.")
            return []
        elif len(elements) == 1:
            element = elements[0]
            self.single_d_attribute(element)
        elif len(elements) > 1:
            self.multiple_d_attributes(elements, chapter_widths)
        plt.savefig('video_heatmap.png')
        plt.show()
            

    def single_d_attribute(self, element):
        """
        Extract the 'd' attribute from SVG path elements.
        Args:
            elements (list): A list of SVG path elements.
        Returns:
            list: A list of 'd' attributes from the SVG path elements.
        """
        d_attribute = element.get_attribute('d')
        if d_attribute:
            print(d_attribute)
            self.analyze_d_attribute(d_attribute)
        else:
            print("No 'd' attribute found in the SVG element.")
            return 
    
    def multiple_d_attributes(self, elements, chapter_widths):
        """
        Extract the 'd' attributes from multiple SVG path elements.
        Args:
            elements (list): A list of SVG path elements.
        Returns:
            list: A list of 'd' attributes from the SVG path elements.
        """
        d_attributes = []
        for element in elements:
            d_attribute = element.get_attribute('d')
            if d_attribute:
                d_attributes.append(d_attribute)
        if d_attributes:
            print("Found multiple 'd' attributes:", d_attributes)
            print("Chapter widths:", chapter_widths)
            self.generate_multiple_d_svg(d_attributes, chapter_widths)    
    
    def generate_svg(self, timestamps, heats):
        """
        Generate SVG content from a list of 'd' attributes with Bezier curve interpolation.
        Args:
            timestamps (list): List of timestamps (x values)
            heats (list): List of heat values (y values)
        """
        if len(timestamps) < 2:
            print("需要至少2個數據點來生成曲線")
            return
        
        # 將列表轉換為numpy數組以便處理
        timestamps = np.array(timestamps)
        heats = np.array(heats)
        
        # 處理負數熱度值 - 轉換為絕對值
        negative_count = np.sum(heats < 0)
        if negative_count > 0:
            print(f"發現 {negative_count} 個負數熱度值，將轉換為絕對值")
            heats = np.abs(heats)
        
        # 處理重複的時間戳 - 保留唯一值並對應平均熱度
        unique_timestamps = []
        unique_heats = []
        
        i = 0
        while i < len(timestamps):
            current_timestamp = timestamps[i]
            current_heats = [heats[i]]
            
            # 收集相同時間戳的所有熱度值
            j = i + 1
            while j < len(timestamps) and abs(timestamps[j] - current_timestamp) < 1e-10:
                current_heats.append(heats[j])
                j += 1
            
            # 使用平均值或最大值
            unique_timestamps.append(current_timestamp)
            unique_heats.append(np.mean(current_heats))  # 可以改為 np.max(current_heats)
            
            i = j
        
        # 轉換為numpy數組
        timestamps = np.array(unique_timestamps)
        heats = np.array(unique_heats)
        
        # 確保時間戳嚴格遞增
        if len(timestamps) > 1:
            for i in range(1, len(timestamps)):
                if timestamps[i] <= timestamps[i-1]:
                    timestamps[i] = timestamps[i-1] + 1e-10
        
        print(f"處理後的數據點: {len(timestamps)} 個")
        print(f"時間戳範圍: {timestamps.min():.6f} - {timestamps.max():.6f}")
        print(f"熱度範圍: {heats.min():.3f} - {heats.max():.3f}")
        
        if len(timestamps) < 2:
            print("處理後數據點不足，無法生成曲線")
            return
        
        # 創建更密集的插值點
        num_points = max(len(timestamps) * 10, 100)  # 至少100個點
        timestamps_interp = np.linspace(timestamps.min(), timestamps.max(), num_points)
        
        # 使用三次樣條插值創建平滑曲線
        try:
            cs = CubicSpline(timestamps, heats, bc_type='natural')
            heats_interp = cs(timestamps_interp)
            # 插值後也可能產生負值，再次處理
            heats_interp = np.abs(heats_interp)
        except ValueError as e:
            print(f"插值失敗: {e}")
            # 回退到線性插值
            interp_func = interp1d(timestamps, heats, kind='linear', fill_value='extrapolate')
            heats_interp = interp_func(timestamps_interp)
            # 線性插值後也處理負值
            heats_interp = np.abs(heats_interp)
        
        # 繪製波型 heatmap
        plt.figure(figsize=(30, 6))
        
        # 繪製原始數據點
        scatter = plt.scatter(timestamps, heats, c=heats, s=50, cmap='hot', alpha=0.8, 
                             edgecolors='black', linewidth=1, label='raw data points', zorder=3)
        
        # 繪製插值後的平滑曲線
        line = plt.plot(timestamps_interp, heats_interp, linewidth=2, color='darkred', 
                       alpha=0.7, label='Bezier interpolation curve')
        
        # 使用漸層填充創建更好的視覺效果
        plt.fill_between(timestamps_interp, heats_interp, alpha=0.3, color='red')
        
        # 添加熱力圖效果 - 使用scatter的顏色映射
        scatter_interp = plt.scatter(timestamps_interp, heats_interp, c=heats_interp, 
                                    s=5, cmap='hot', alpha=0.6, zorder=2)
        
        # 設置標籤和標題
        plt.xlabel('Video progress (ratio)', fontsize=12)
        plt.ylabel('heat', fontsize=12)
        plt.title('yt-heatmap', fontsize=14)
        
        
        # 添加圖例
        plt.legend()
        
        # 設置網格
        plt.grid(True, alpha=0.3)
        
        # 調整佈局
        plt.tight_layout()
        
        # 可選：輸出插值後的數據統計
        print(f"原始數據點: {len(timestamps)} 個")
        print(f"插值後數據點: {len(timestamps_interp)} 個")
        print(f"最終熱度範圍: {heats_interp.min():.3f} - {heats_interp.max():.3f}")

    def analyze_d_attribute(self, d_attribute):
        """
        Analyze the 'd' attribute of an SVG path element.
        Args:
            d_attribute (str): The 'd' attribute of an SVG path element.
        Returns:
            list: A list of points extracted from the 'd' attribute.
        """
        # 原始 SVG path 資料
        path_data = d_attribute

        # 分析可用點
        segments = re.split(r'\s*C\s*', path_data.strip())[1:]
        timestamps = []
        heats = []
        for seg in segments:
            nums = list(map(float, re.findall(r'[-]?\d+\.?\d+', seg)))
            if len(nums) >= 6:
                x3, y3 = nums[4], nums[5]
                if x3 % 10 == 5:
                    timestamps.append((x3 - 5) / 1000)
                    heats.append((100 - y3) / 100)
        self.generate_svg(timestamps, heats)
        return timestamps, heats

    def analyze_multiple_d_attributes(self, d_attributes, chapter_widths):
        """
        Analyze multiple 'd' attributes of SVG path elements.
        Args:
            d_attributes (list): A list of 'd' attributes.
            chapter_widths (list): A list of chapter widths.
        Returns:
            list: A list of points extracted from the 'd' attributes.
        """
        total_width = sum(chapter_widths)
        timestamps = []
        heats = []
        
        print(f"Processing {len(d_attributes)} d_attributes")
        print(f"Chapter widths: {chapter_widths}")
        print(f"Total width: {total_width}")
        
        for i, d in enumerate(d_attributes):
            print(f"Processing d_attribute {i}: {d[:100]}...")  # 只顯示前100字符
            segments = re.split(r'\s*C\s*', d.strip())[1:]
            print(f"Found {len(segments)} segments")
            
            for j, seg in enumerate(segments):
                nums = list(map(float, re.findall(r'[-]?\d+\.?\d+', seg)))
                print(f"Segment {j}: found {len(nums)} numbers")
                if len(timestamps) != 0:
                    last_timestamp = timestamps[-1]
                    print(f"Last timestamp: {last_timestamp}")
                else:
                    last_timestamp = 0
                
                if len(nums) >= 6:
                    x3, y3 = nums[4], nums[5]
                    x3_mod = x3 % 10
                    print(f"x3: {x3}, y3: {y3}, x3 % 10: {x3_mod}")
                    
                    # 修正浮點數精度問題，檢查是否接近 5 或 0
                    if abs(x3_mod - 5) < 0.1 or abs(x3_mod) < 0.1:
                        # 修正索引計算
                        chapter_index = i if i < len(chapter_widths) else i % len(chapter_widths)
                        width = chapter_widths[chapter_index]
                        
                        # 修正時間戳計算
                        timestamp = last_timestamp + (x3 / 1000) * (width / total_width)
                        heat = (100 - y3) / 100
                        
                        timestamps.append(timestamp)
                        heats.append(heat)
                        print(f"Added: timestamp={timestamp}, heat={heat}")

        print(f"Final results: {len(timestamps)} timestamps, {len(heats)} heats")
        return timestamps, heats
    

    def generate_multiple_d_svg(self, d_attributes, chapter_widths):
        """
        Generate SVG content from multiple 'd' attributes.
        Args:
            d_attributes (list): A list of 'd' attributes.
            chapter_widths (list): A list of chapter widths.
        """
        # 這裡可以根據需要實現多個 'd' 屬性的處理邏輯
        print("Processing multiple 'd' attributes...")
        timestamps, heats = self.analyze_multiple_d_attributes(d_attributes, chapter_widths)
        print("Timestamps:", timestamps)
        print("Heats:", heats)
        # 繪製波型 heatmap
        self.generate_svg(timestamps, heats)

