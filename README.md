# Sequencing Application

A full-stack web application built with Angular frontend, Flask backend, and MySQL database. Features role-based authentication with responsive design.

## Features

- **Role-based Authentication**: Login system with admin and user roles
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **JWT Authentication**: Secure token-based authentication
- **MySQL Database**: Persistent data storage
- **Modern UI**: Beautiful and intuitive user interface

## Project Structure

```
Sequencing/
├── backend/              # Flask backend application
│   ├── app.py           # Main Flask application
│   ├── requirements.txt # Python dependencies
│   └── .env.example     # Environment variables template
├── frontend/            # Angular frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── login/
│   │   │   │   └── dashboard/
│   │   │   ├── services/
│   │   │   ├── guards/
│   │   │   └── app.module.ts
│   │   └── main.ts
│   ├── package.json
│   └── angular.json
├── database/
│   └── init.sql        # Database initialization script
└── README.md
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (with pip)
- **Node.js 18+** (with npm)
- **MySQL 8.0+**
- **Angular CLI** (will be installed via npm)

## Setup Instructions

### 1. Database Setup

1. Start your MySQL server
2. Create the database and tables:

```bash
mysql -u root -p < database/init.sql
```

Or manually:
```sql
CREATE DATABASE sequencing_db;
USE sequencing_db;
-- Then run the SQL from database/init.sql
```

### 2. Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

5. Edit `.env` file with your database credentials:
```
DB_HOST=localhost
DB_NAME=sequencing_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_PORT=3306
JWT_SECRET_KEY=your-secret-key-change-in-production
```

6. Run the Flask application:
```bash
python app.py
```

The backend will be running on `http://localhost:5000`

### 3. Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Install Angular CLI globally (if not already installed):
```bash
npm install -g @angular/cli
```

4. Start the development server:
```bash
ng serve
```

Or using npm:
```bash
npm start
```

The frontend will be running on `http://localhost:4200`

## Default Login Credentials

The application comes with two default users:

**Admin User:**
- Email: `admin@example.com`
- Password: `admin123`
- Role: `admin`

**Regular User:**
- Email: `user@example.com`
- Password: `user123`
- Role: `user`

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/login` - User login
  - Body: `{ "email": "user@example.com", "password": "password123" }`
- `GET /api/profile` - Get current user profile (requires authentication)
- `GET /api/protected` - Protected endpoint example (requires authentication)

## Development

### Backend Development

The Flask backend uses:
- Flask for the web framework
- Flask-CORS for cross-origin requests
- Flask-Bcrypt for password hashing
- Flask-JWT-Extended for JWT authentication
- mysql-connector-python for database connectivity

### Frontend Development

The Angular frontend uses:
- Angular 17
- Reactive Forms for form handling
- HTTP Client for API calls
- Route Guards for authentication
- HTTP Interceptors for token management

## Production Deployment

### Backend

1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Use environment variables for sensitive data
4. Set a strong `JWT_SECRET_KEY`

### Frontend

1. Build for production:
```bash
ng build --configuration production
```

2. Serve the `dist/sequencing-frontend` folder using a web server like Nginx or Apache

## Troubleshooting

### Database Connection Issues

- Ensure MySQL server is running
- Verify database credentials in `.env` file
- Check if the database `sequencing_db` exists

### CORS Issues

- Ensure the backend CORS configuration allows your frontend URL
- Check that both servers are running on the correct ports

### Port Already in Use

- Backend: Change port in `app.py` (default: 5000)
- Frontend: Use `ng serve --port 4201` to use a different port

## License

This project is open source and available for educational purposes.


