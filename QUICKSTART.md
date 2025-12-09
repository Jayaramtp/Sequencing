# Quick Start Guide

Follow these steps to get the application running quickly.

## Prerequisites Check

Make sure you have installed:
- ✅ Python 3.8+ (`python --version`)
- ✅ Node.js 18+ (`node --version`)
- ✅ MySQL 8.0+ (running and accessible)
- ✅ npm (`npm --version`)

## Step 1: Database Setup

1. Open MySQL command line or MySQL Workbench
2. Run the initialization script:
   ```bash
   mysql -u root -p < database/init.sql
   ```
   Or manually create the database:
   ```sql
   CREATE DATABASE sequencing_db;
   ```

## Step 2: Backend Setup

### Option A: Using Setup Script (Windows)
```bash
setup_backend.bat
```

### Option B: Manual Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. Create `.env` file:
   ```bash
   cd backend
   copy env.example .env
   ```

4. Edit `.env` with your MySQL credentials:
   ```
   DB_HOST=localhost
   DB_NAME=sequencing_db
   DB_USER=root
   DB_PASSWORD=your_password
   DB_PORT=3306
   JWT_SECRET_KEY=your-secret-key-change-in-production
   ```

5. Start the backend:
   ```bash
   python app.py
   ```
   Backend will run on `http://localhost:5000`

## Step 3: Frontend Setup

### Option A: Using Setup Script (Windows)
```bash
setup_frontend.bat
```

### Option B: Manual Setup
```bash
cd frontend
npm install
```

2. Install Angular CLI (if not already installed):
   ```bash
   npm install -g @angular/cli
   ```

3. Start the frontend:
   ```bash
   ng serve
   ```
   Or:
   ```bash
   npm start
   ```
   Frontend will run on `http://localhost:4200`

## Step 4: Access the Application

1. Open your browser and go to: `http://localhost:4200`
2. Use the demo credentials to login:
   - **Admin**: `admin@example.com` / `admin123`
   - **User**: `user@example.com` / `user123`

## Troubleshooting

### Backend won't start
- Check if MySQL is running
- Verify database credentials in `.env`
- Ensure port 5000 is not in use

### Frontend won't start
- Make sure Node.js and npm are installed
- Try deleting `node_modules` and running `npm install` again
- Check if port 4200 is not in use

### Database connection error
- Verify MySQL is running: `mysql -u root -p`
- Check database exists: `SHOW DATABASES;`
- Verify credentials in `.env` file

## Default Credentials

- **Admin User**: admin@example.com / admin123
- **Regular User**: user@example.com / user123

## Need Help?

Refer to the main [README.md](README.md) for detailed documentation.


