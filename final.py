from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_m4a_links(html_content):
    # Regular expression pattern to match links starting with 'https://rr' and ending with '.m4a'
    pattern = r'https://rr.*?\.m4a'

    # Find all matches using the regex pattern
    links = re.findall(pattern, html_content)

    return links

@app.route('/extract_links', methods=['GET'])
def extract_links():
    yt_videoId = request.args.get('yt_videoId')

    if not yt_videoId:
        return jsonify({"error": "yt_videoId parameter is required"}), 400

    url = f"https://video.genyt.net/{yt_videoId}"
    
    try:
        # Fetch the HTML content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the prettified HTML content as a string
        html_content = soup.prettify()

        # Extract links from the HTML content directly
        links = extract_m4a_links(html_content)

        if links:
            return jsonify({"m4a_links": links}), 200
        else:
            return jsonify({"message": "No matching links found"}), 404

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 504

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=8000)
