from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import urllib3
import mechanicalsoup
from lxml import html
import scrapy
from scrapy.crawler import CrawlerProcess
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Scrapy spider for scraping video page
class AudioScraper(scrapy.Spider):
    name = "audio_scraper"
    
    def __init__(self, url, *args, **kwargs):
        super(AudioScraper, self).__init__(*args, **kwargs)
        self.start_urls = [url]
    
    def parse(self, response):
        audio_url = None
        # Logic for extracting audio URLs, e.g., using BeautifulSoup or XPath
        soup = BeautifulSoup(response.text, 'lxml')
        for link in soup.find_all('a', href=True):
            if link['href'].endswith(('m4a', 'mp3')):
                audio_url = link['href']
                break
        return {'audio_url': audio_url}

# Start Scrapy process to run spiders
def run_scraper(video_url):
    process = CrawlerProcess({
        'LOG_LEVEL': 'ERROR'
    })
    scraper = AudioScraper(url=video_url)
    process.crawl(scraper)
    process.start()
    return scraper.crawled_data

# Playwright scraping
def playwright_scrape(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        audio_url = None
        for link in soup.find_all('a', href=True):
            if link['href'].endswith(('m4a', 'mp3')):
                audio_url = link['href']
                break
        browser.close()
        return audio_url

@app.route('/audio_url', methods=['GET'])
def get_audio_url():
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"error": "video_id is required"}), 400
    
    # Create the video URL
    video_url = f"https://video.genyt.net/{video_id}"

    # Scrape the video page for the audio URL
    try:
        # Try to fetch audio using Scrapy
        scraped_audio_url = run_scraper(video_url)
        if scraped_audio_url:
            return jsonify({"audio_url": scraped_audio_url}), 200

        # Fallback to Playwright scraping
        audio_url = playwright_scrape(video_url)
        if audio_url:
            return jsonify({"audio_url": audio_url}), 200
        
        # Fallback using requests and bs4
        http = urllib3.PoolManager()
        response = http.request('GET', video_url)
        if response.status == 200:
            soup = BeautifulSoup(response.data, 'html.parser')
            for link in soup.find_all('a', href=True):
                if link['href'].endswith(('m4a', 'mp3')):
                    return jsonify({"audio_url": link['href']}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"error": "No valid audio URL found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
