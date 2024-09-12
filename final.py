import http.server
import socketserver
import urllib.parse
import http.client
import re

PORT = 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Extract yt_videoId from URL path
        parsed_path = urllib.parse.urlparse(self.path)
        yt_videoId = parsed_path.path.split('/')[-1]

        if yt_videoId:
            try:
                # Connect to video.genyt.net and fetch HTML content
                conn = http.client.HTTPSConnection("video.genyt.net")
                conn.request("GET", f"/{yt_videoId}")
                response = conn.getresponse()
                
                if response.status == 200:
                    html_content = response.read().decode('utf-8')
                    # Save HTML content to ws_{yt_videoId}.txt
                    file_name = f'ws_{yt_videoId}.txt'
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(html_content)

                    # Search for the link in the saved file
                    link_pattern = re.compile(r'https://r[^"]*\.m4a')
                    match = link_pattern.search(html_content)
                    link = match.group(0) if match else "No matching link found."

                    # Respond with the saved content and the found link
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"HTML content saved successfully!<br><br>")
                    self.wfile.write(f"Extracted link: {link}".encode('utf-8'))
                else:
                    # Respond with an error if the fetch failed
                    self.send_response(response.status)
                    self.end_headers()
                    self.wfile.write(b"Failed to retrieve the content.")
                
                conn.close()
            except Exception as e:
                # Respond with an error if something went wrong
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
        else:
            # Respond with a bad request if yt_videoId is missing
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request: Missing yt_videoId in URL.")

# Set up the HTTP server
with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
