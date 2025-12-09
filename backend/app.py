from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta
from functools import wraps
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
# JWT token location defaults to headers with 'Authorization: Bearer <token>' format

CORS(app, 
     origins=["http://localhost:4200", "http://localhost:4201"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Invalid token error: {str(error)}")
    error_msg = str(error)
    if 'Not enough segments' in error_msg:
        return jsonify({'error': 'Token format is invalid. Please log out and log back in.'}), 422
    elif 'Signature verification failed' in error_msg:
        return jsonify({'error': 'Token signature is invalid. The secret key may have changed. Please log out and log back in.'}), 422
    else:
        return jsonify({'error': f'Invalid token: {error_msg}. Please log out and log back in.'}), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is missing'}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token is not fresh'}), 401

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'sequencing_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    """Create and return database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Initialize database and create tables if they don't exist"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create default admin user if not exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@example.com'")
            if cursor.fetchone()[0] == 0:
                hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
                cursor.execute("""
                    INSERT INTO users (email, password, role) 
                    VALUES ('admin@example.com', %s, 'admin')
                """, (hashed_password,))
            
            # Create default user
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'user@example.com'")
            if cursor.fetchone()[0] == 0:
                hashed_password = bcrypt.generate_password_hash('user123').decode('utf-8')
                cursor.execute("""
                    INSERT INTO users (email, password, role) 
                    VALUES ('user@example.com', %s, 'user')
                """, (hashed_password,))
            
            connection.commit()
            print("Database initialized successfully")
        except Error as e:
            print(f"Error initializing database: {e}")
        finally:
            cursor.close()
            connection.close()

def admin_required(fn):
    """Decorator to enforce admin-only access"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        try:
            # Get the JWT identity (user ID as string) and additional claims
            user_id = get_jwt_identity()
            jwt_data = get_jwt()
            
            # Extract user data from claims
            current_user = {
                'id': int(user_id) if user_id else None,
                'email': jwt_data.get('email'),
                'role': jwt_data.get('role')
            }
            
            print(f"Admin check - user_id: {user_id}, role: {current_user.get('role')}")
            
            if not current_user.get('role'):
                print("No role found in token")
                return jsonify({'error': 'User role not found in token'}), 403
            
            if current_user.get('role') != 'admin':
                print(f"User role is not admin: {current_user.get('role')}")
                return jsonify({'error': 'Admin access required'}), 403
            
            return fn(current_user, *args, **kwargs)
        except Exception as e:
            print(f"Error in admin_required: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Authentication error: {str(e)}'}), 403
    return wrapper

def sanitize_user(user_row):
    """Return user dict without password field"""
    created_at = user_row.get('created_at')
    if created_at and hasattr(created_at, 'isoformat'):
        created_at = created_at.isoformat()
    elif created_at:
        created_at = str(created_at)
    
    return {
        'id': user_row['id'],
        'email': user_row['email'],
        'role': user_row['role'],
        'created_at': created_at
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            # Use user ID as string identity, store additional data in additional_claims
            access_token = create_access_token(
                identity=str(user['id']),
                additional_claims={
                    'email': user['email'],
                    'role': user['role']
                }
            )
            print(f"Login successful - Created token for user ID: {user['id']}, role: {user['role']}")
            return jsonify({
                'token': access_token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'role': user['role']
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        current_user = {
            'id': int(user_id) if user_id else None,
            'email': jwt_data.get('email'),
            'role': jwt_data.get('role')
        }
        return jsonify({'user': current_user}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    """Protected endpoint example"""
    user_id = get_jwt_identity()
    jwt_data = get_jwt()
    current_user = {
        'id': int(user_id) if user_id else None,
        'email': jwt_data.get('email'),
        'role': jwt_data.get('role')
    }
    return jsonify({
        'message': 'This is a protected route',
        'user': current_user
    }), 200

@app.before_request
def log_request_info():
    """Log request information for debugging"""
    if request.path.startswith('/api/') and request.path != '/api/health':
        auth_header = request.headers.get('Authorization', 'Not provided')
        print(f"Request: {request.method} {request.path}")
        if auth_header != 'Not provided':
            print(f"Authorization header present: {auth_header[:30]}...")
        else:
            print("Authorization header: Not provided")

@app.route('/api/users', methods=['GET'])
@admin_required
def list_users(current_user):
    """List all users (admin only)"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, email, role, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        connection.close()

        sanitized_users = [sanitize_user(u) for u in users]
        return jsonify({'users': sanitized_users}), 200
    except Exception as e:
        print(f"Error in list_users: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user(current_user):
    """Create a new user (admin only)"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Validate role
        if role not in ['user', 'admin']:
            return jsonify({'error': 'Invalid role. Must be "user" or "admin"'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
            (email, hashed_password, role)
        )
        connection.commit()
        new_user_id = cursor.lastrowid

        cursor.execute("SELECT id, email, role, created_at FROM users WHERE id = %s", (new_user_id,))
        new_user = cursor.fetchone()

        cursor.close()
        connection.close()

        if not new_user:
            return jsonify({'error': 'Failed to retrieve created user'}), 500

        return jsonify({'user': sanitize_user(new_user)}), 201
    except mysql.connector.IntegrityError as e:
        print(f"IntegrityError in create_user: {str(e)}")
        return jsonify({'error': 'Email already exists'}), 409
    except Exception as e:
        print(f"Error in create_user: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(current_user, user_id):
    """Update user email, password, or role (admin only)"""
    try:
        data = request.get_json() or {}
        updates = []
        values = []

        if 'email' in data and data.get('email'):
            updates.append("email = %s")
            values.append(data['email'])
        if 'password' in data and data.get('password'):
            hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            updates.append("password = %s")
            values.append(hashed_password)
        if 'role' in data and data.get('role'):
            updates.append("role = %s")
            values.append(data['role'])

        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400

        values.append(user_id)

        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", tuple(values))
        connection.commit()

        cursor.execute("SELECT id, email, role, created_at FROM users WHERE id = %s", (user_id,))
        updated_user = cursor.fetchone()

        cursor.close()
        connection.close()

        if not updated_user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': sanitize_user(updated_user)}), 200
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    """Delete a user (admin only)"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': 'User not found'}), 404

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)


