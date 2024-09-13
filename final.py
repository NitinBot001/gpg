import http.server
import socketserver
import urllib.parse
import requests
from bs4 import BeautifulSoup
import re
import os
import threading
import time

PORT = 8000



class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Extract yt_videoId from URL path
        parsed_path = urllib.parse.urlparse(self.path)
        yt_videoId = parsed_path.path.split('/')[-1]

        if yt_videoId:
            try:
                url = f"https://video.genyt.net/{yt_videoId}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
                }
                
                for attempt in range(3):  # Retry up to 3 times
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        break
                    time.sleep(2)  # Wait 2 seconds before retrying
                
                if response.status_code == 200:
                    html_content = response.text
                    file_name = f'ws_{yt_videoId}.txt'
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(html_content)

                    soup = BeautifulSoup(html_content, 'lxml')
                    link_pattern = re.compile(r'https://r[^"]*\.m4a')
                    links = link_pattern.findall(html_content)
                    link = links[0] if links else "No matching link found."

                    def delete_file():
                        if os.path.exists(file_name):
                            os.remove(file_name)
                            print(f"File {file_name} has been deleted.")

                    threading.Timer(180.0, delete_file).start()

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"HTML content saved successfully!<br><br>")
                    self.wfile.write(f"Extracted link: {link}".encode('utf-8'))
                else:
                    self.send_response(response.status_code)
                    self.end_headers()
                    self.wfile.write(b"Failed to retrieve the content.")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request: Missing yt_videoId in URL.")
# Set up the HTTP server
with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
