from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def extract_m4a_links(file_path):
    # Regular expression pattern to match links starting with 'https://rr' and ending with '.m4a'
    pattern = r'https://rr.*?\.m4a'

    # Open the file and read its contents
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    # Find all matches using the regex pattern
    links = re.findall(pattern, file_contents)

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
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML content to a file
        file_name = f"ws_{yt_videoId}.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())  # Save formatted HTML
        
        # Extract links from the saved HTML file
        links = extract_m4a_links(file_name)

        # Delete the text file after extraction
        os.remove(file_name)

        if links:
            return jsonify({"m4a_links": links}), 200
        else:
            return jsonify({"message": "No matching links found"}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
