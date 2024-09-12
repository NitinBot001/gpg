import http.server
import socketserver
import urllib.parse
import http.client
import re
import os
import threading
import time

PORT = 8000
FILE_LIFETIME = 120  # File lifetime in seconds (2 minutes)

# Function to extract links from the saved text file
def extract_links(file_path):
    # Regular expression pattern for matching URLs starting with 'https://rr' and ending with '.m4a' or '.mp3'
    pattern = r'https://rr.*?\.(m4a|mp3)'
    
    # Open the file and read its content
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find all matching links using the regular expression
        links = re.findall(pattern, content)
        return links
    except FileNotFoundError:
        return None

# Function to delete the file after 5 minutes
def delete_file_after_delay(file_path, delay):
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} deleted after {delay / 60} minutes.")

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Extract yt_videoId from URL path
        parsed_path = urllib.parse.urlparse(self.path)
        yt_videoId = parsed_path.path.split('/')[-1]

        if yt_videoId:
            try:
                # File path for the saved HTML content
                file_path = f'ws_{yt_videoId}.txt'
                
                # Check if the file already exists
                links = extract_links(file_path)
                
                if links is None:  # If the file doesn't exist, fetch the content and save it
                    conn = http.client.HTTPSConnection("video.genyt.net")
                    conn.request("GET", f"/{yt_videoId}")
                    response = conn.getresponse()
                    
                    if response.status == 200:
                        html_content = response.read().decode('utf-8')
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        # Start a thread to delete the file after 5 minutes
                        threading.Thread(target=delete_file_after_delay, args=(file_path, FILE_LIFETIME), daemon=True).start()

                        # Now search for the links in the saved file
                        links = extract_links(file_path)
                    else:
                        self.send_response(response.status)
                        self.end_headers()
                        self.wfile.write(b"Failed to retrieve the content.")
                        return

                    conn.close()
                
                # Respond with the first matching link or an error if none are found
                if links:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"Extracted link: {links[0]}".encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"No matching links found in the file.")
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
