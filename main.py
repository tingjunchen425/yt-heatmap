from scrabber import Scrabber
from svgGenerate import svgGenerate

def main(url):
    # Initialize the Scrabber with a YouTube video URL
    browser = Scrabber(url)
    
    # Scrape the SVG data from the video
    svg_data = browser.scrab()
    
    # Create an instance of svgGenerate and route the SVG data
    generate = svgGenerate()
    generate.route(svg_data)

'''
urls:
- https://www.youtube.com/watch?v=97-JY6KEoQs
- https://www.youtube.com/watch?v=KMEwqTYlEiY
'''

if __name__ == "__main__":
    # Example YouTube video URL
    video_url = "https://www.youtube.com/watch?v=KMEwqTYlEiY"
    
    # Call the main function with the video URL
    main(video_url)