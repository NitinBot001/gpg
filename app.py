from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import urllib3
import scrapy
from mechanicalsoup import StatefulBrowser
from scrapy import Selector

app = Flask(__name__)

# Disable SSL warnings from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to fetch audio URL using BeautifulSoup and requests
def fetch_audio_url(video_id):
    video_url = f"https://video.genyt.net/{video_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        # Request the video page
        response = requests.get(video_url, headers=headers, verify=False)
        response.raise_for_status()  # Raise error if request failed
        html_content = response.content

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'lxml')
        download_links = soup.find_all('a', attrs={'download': True})
        
        # Filter and return a valid audio URL (e.g., mp3 or m4a)
        for link in download_links:
            if 'mp3' in link['download'] or 'm4a' in link['download']:
                return link['href']
        
    except requests.RequestException as e:
        print(f"Error fetching audio URL: {e}")
        return None

    return None


# Function to fetch related songs using Scrapy and lxml
def fetch_related_songs(video_id):
    api_url = f"https://deep-dulcine-nitinbhujwa-16d0b380.koyeb.app/related_songs?video_id={video_id}"
    try:
        response = requests.get(api_url, verify=False)
        response.raise_for_status()  # Check for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching related songs: {e}")
        return None


@app.route('/get_audio_url', methods=['GET'])
def get_audio_url():
    video_id = request.args.get('videoId')
    if video_id:
        audio_url = fetch_audio_url(video_id)
        if audio_url:
            return jsonify({'audioUrl': audio_url})
        else:
            return jsonify({'error': 'Failed to fetch audio URL'}), 500
    return jsonify({'error': 'No videoId provided'}), 400


@app.route('/get_related_songs', methods=['GET'])
def get_related_songs():
    video_id = request.args.get('videoId')
    if video_id:
        related_songs = fetch_related_songs(video_id)
        if related_songs:
            return jsonify({'relatedSongs': related_songs})
        else:
            return jsonify({'error': 'Failed to fetch related songs'}), 500
    return jsonify({'error': 'No videoId provided'}), 400


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
