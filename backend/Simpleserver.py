import http.server
import socketserver
import json
import sqlite3

# Create/connect to the SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')
conn.commit()

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if self.path == '/signup':
            self.handle_signup(data)

    def handle_signup(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if username or email already exists
        cursor.execute('SELECT * FROM users WHERE username=? OR email=?', (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'message': 'Username or email already exists.'}).encode('utf-8'))
            return

        # Add user to the database
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        self.end_headers()
        self.wfile.write(json.dumps({'success': True, 'redirect': '/login.html'}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    PORT = 8080
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print("Server started at localhost:" + str(PORT))
        httpd.serve_forever()
