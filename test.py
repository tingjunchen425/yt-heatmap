from scrabber import Scrabber
from svgGenerate import svgGenerate

browser = Scrabber("https://www.youtube.com/watch?v=97-JY6KEoQs")
svg_data = browser.scrab()
elements = svg_data['path_elements']
chapter_widths = svg_data['chapter_widths']
print("SVG 資料:", elements)
generate = svgGenerate()
d = generate.route(svg_data)



