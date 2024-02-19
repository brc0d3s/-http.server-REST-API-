import http.server
import socketserver
import json
import sqlite3

# Create/connect to the SQLite database
try:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create the users table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')
    conn.commit()
except sqlite3.Error as e:
    print("Error connecting to SQLite database:", e)

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers.get('Content-Type')
        if content_type != 'application/json':
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid Content-Type, JSON expected')
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError as e:
            print("Error decoding JSON data:", e)
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'message': 'Invalid JSON data'}).encode('utf-8'))
            return

        if self.path == '/signup':
            self.handle_signup(data)
        elif self.path == '/login':
            self.handle_login(data)

    def handle_signup(self, data):
        try:
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
            self.wfile.write(json.dumps({'success': True, 'redirect': '../frontend/login.html'}).encode('utf-8'))
        except sqlite3.Error as e:
            print("Error handling signup:", e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'message': 'Internal server error'}).encode('utf-8'))

    def handle_login(self, data):
        try:
            username = data.get('username')
            password = data.get('password')

            # Check if username and password match a user in the database
            cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
            user = cursor.fetchone()
            if user:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'redirect': '../frontend/home.html'}).encode('utf-8'))
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': 'Incorrect username or password.'}).encode('utf-8'))
        except sqlite3.Error as e:
            print("Error handling login:", e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'message': 'Internal server error'}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    PORT = 8080
    try:
        with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
            print("Server started at localhost:" + str(PORT))
            httpd.serve_forever()
    except OSError as e:
        print("Error starting the server:", e)
    finally:
        conn.close()
