from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

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
        
        return jsonify({"message": f"HTML content saved to {file_name}"}), 200
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
v
