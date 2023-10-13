import http.server
import socketserver
import psycopg2
import hashlib

# Set your PostgreSQL database connection details
db_config = {
    'dbname': 'Loginpy',
    'user': 'postgres',
    'password': 'Npassword@456',
    'host': '216.230.74.17',
    'port': '5432'
}

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Welcome to the registration and login system!')
        elif self.path == '/register':
            # Display the registration form
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            registration_form = """
                <form method="POST" action="/register">
                    Username: <input type="text" name="username"><br>
                    Password: <input type="password" name="password"><br>
                    <input type="submit" value="Register">
                </form>
            """
            self.wfile.write(registration_form.encode('utf-8'))
        elif self.path == '/login':
            # Display the login form
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            login_form = """
                <form method="POST" action="/login">
                    Username: <input type="text" name="username"><br>
                    Password: <input type="password" name="password"><br>
                    <input type="submit" value="Login">
                </form>
            """
            self.wfile.write(login_form.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        if self.path == '/register':
            # Handle registration logic
            form_data = parse_post_data(post_data)
            username = form_data.get('username')
            password = form_data.get('password')
            if username and password:
                conn = psycopg2.connect(**db_config)
                cursor = conn.cursor()
                # Check if the username already exists
                cursor.execute("SELECT username FROM users1 WHERE username = %s", (username,))
                if cursor.fetchone():
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Username already exists. Please choose another username.')
                else:
                    # Hash the password before storing it
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute("INSERT INTO users1 (username, password) VALUES (%s, %s)", (username, hashed_password))
                    conn.commit()
                    conn.close()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Registration successful. You can now <a href="/login">login</a>.')
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Invalid username or password.')

        elif self.path == '/login':
            # Handle login logic
            form_data = parse_post_data(post_data)
            username = form_data.get('username')
            password = form_data.get('password')
            if username and password:
                conn = psycopg2.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute("SELECT username, password FROM users1 WHERE username = %s", (username,))
                user_data = cursor.fetchone()
                if user_data:
                    stored_password = user_data[1]
                    # Hash the entered password and compare with the stored password
                    if hashlib.sha256(password.encode()).hexdigest() == stored_password:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b'Login successful!')
                    else:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b'Invalid username or password.')
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Invalid username or password.')

def parse_post_data(post_data):
    data = {}
    parts = post_data.split('&')
    for part in parts:
        key, value = part.split('=')
        data[key] = value
    return data

if __name__ == '__main__':
    httpd = socketserver.TCPServer(('', 8000), MyHandler)
    print('Listening on port 8000...')
    httpd.serve_forever()
