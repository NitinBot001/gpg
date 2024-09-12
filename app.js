const http = require('http');
const httpProxy = require('http-proxy');

// Create a proxy server
const proxy = httpProxy.createProxyServer({});

// Define the target for your proxy (e.g., YouTube)
const targetUrl = 'https://www.youtube.com';

// Create the HTTP server
const server = http.createServer((req, res) => {
  // Proxy the request to the target URL
  proxy.web(req, res, { target: targetUrl });
});

// Start the server
const PORT = process.env.PORT || 10000;
server.listen(PORT, () => {
  console.log(`Proxy server running on port ${PORT}`);
});
