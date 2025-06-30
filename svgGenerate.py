import re
import matplotlib.pyplot as plt

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
        plt.savefig('video_heatmap.svg')
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
        Generate SVG content from a list of 'd' attributes.
        Args:
            d_attributes (list): A list of 'd' attributes.
        """
    
        # 繪製波型 heatmap
        plt.figure(figsize=(30, 6))
        plt.plot(timestamps, heats)
        plt.scatter(timestamps, heats, c=heats, s=20)
        plt.xlabel('Video progress (ratio)')
        plt.ylabel('heat')
        plt.title('video heatmap')
        # plt.colorbar(label='heat intensity')
        plt.tight_layout()

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

