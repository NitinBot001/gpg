from flask_cors import CORS
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

@app.route('/extract_html', methods=['GET'])
def extract_html():
    yt_videoId = request.args.get('yt_videoId')

    if not yt_videoId:
        return jsonify({"error": "yt_videoId parameter is required"}), 400

    url = f"https://video.genyt.net/{yt_videoId}"
    
    try:
        # Fetch the HTML content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML content to a file
        file_name = f"ws_{yt_videoId}.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())  # Save formatted HTML
        
        # Read the content of the saved file
        with open(file_name, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Search for URLs starting with "https://r" and ending with ".mp3" or ".m4a"
        pattern = r'https://r.*?\.(mp3|m4a)'
        found_urls = re.findall(pattern, html_content)
        
        if found_urls:
            return jsonify({"found_urls": found_urls}), 200
        else:
            return jsonify({"message": "No URLs found"}), 404
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True , port=8000)
