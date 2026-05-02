# AI Mantraas - Student Learning Portal

A modern landing page website and student learning portal for AI Mantraas - Transform Your Career with AI Agents. Built with HTML, Tailwind CSS, JavaScript, and a Flask backend API.

## ✅ Quick Start (Frontend + Backend Together)

The Flask backend now serves both the frontend and API. Run this from the backend folder:

```bash
cd student-learning-portal/backend
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 - everything works together!

## 🚀 Project Structure

```
ai-mantraas-student/
├── index.html                    # Main landing page
├── for-business.html             # Business landing page
├── bglogo.png                    # Background logo image
├── .env                          # Environment variables (DO NOT COMMIT)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
│
├── student-learning-portal/
│   ├── backend/
│   │   ├── app.py                # Flask API application
│   │   ├── wsgi.py               # WSGI entry point
│   │   ├── google_sheets.py      # Google Sheets integration
│   │   ├── requirements.txt      # Python dependencies
│   │   ├── Procfile              # Heroku/Render deployment
│   │   ├── runtime.txt           # Python runtime version
│   │   ├── app.yaml              # Google App Engine config
│   │   ├── Dockerfile            # Docker container image
│   │   ├── docker-compose.yml    # Docker Compose setup
│   │   ├── .dockerignore         # Docker ignore rules
│   │   ├── local-data/           # Local JSON data storage
│   │   ├── service-account-sample.json  # Service account template
│   │   └── SHEETS_SETUP.md       # Google Sheets setup guide
│   │
│   └── frontend/                 # Student portal frontend
│       └── index.html
```

## 📋 Prerequisites

### For Development
- **Python 3.11+** - Backend runtime
- **Node.js** (optional) - For frontend development
- **Web browser** - Chrome, Firefox, Edge, or Safari
- **Text editor** - VS Code recommended

### For Deployment
- **Git** - Version control
- **Python 3.11+** - For production servers
- **Docker** (optional) - For containerized deployment
- **Google Cloud Platform account** - For Google Sheets API

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-mantraas-student
```

### 2. Backend Setup

```bash
cd student-learning-portal/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
# Copy the template
copy .env.example .env

# Edit .env with your credentials (see .env.example for reference)
```

### 4. Run the Backend

```bash
# Development mode (with auto-reload)
python app.py

# Or using Flask CLI
set FLASK_APP=app.py
flask run
```

The backend will run at http://localhost:5000

### 5. Run the Frontend

```bash
# Using Python
python -m http.server 8000

# Or using VS Code Live Server
# Right-click index.html > Open with Live Server
```

The frontend will run at http://localhost:8000

## ☁️ Deployment Options

### Option 1: Render.com (Recommended - Free Tier)

1. **Push code to GitHub**

2. **Create account on [Render](https://render.com)**

3. **Create new Web Service**
   - Connect your GitHub repository
   - Select the `student-learning-portal/backend` directory
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:application`

4. **Set Environment Variables**
   - Add all variables from `.env.example`
   -特别注意: Set `DEBUG_MODE=False` for production

5. **Deploy!**

### Option 2: Heroku

1. **Install Heroku CLI**

2. **Create Heroku app**
   ```bash
   cd student-learning-portal/backend
   heroku create ai-mantraas-backend
   ```

3. **Set environment variables**
   ```bash
   heroku config:set GOOGLE_SERVICE_ACCOUNT_EMAIL=your-email
   heroku config:set GOOGLE_PRIVATE_KEY="your-private-key"
   # ... other variables
   ```

4. **Deploy**
   ```bash
   git subtree push --prefix student-learning-portal/backend heroku main
   ```

### Option 3: Google App Engine

1. **Install Google Cloud SDK**

2. **Configure app.yaml** (already provided)

3. **Deploy**
   ```bash
   cd student-learning-portal/backend
   gcloud app deploy
   ```

### Option 4: Docker Container

1. **Build the image**
   ```bash
   cd student-learning-portal/backend
   docker build -t ai-mantraas-backend .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 \
     --env-file ../../.env \
     ai-mantraas-backend
   ```

3. **Using Docker Compose**
   ```bash
   cd student-learning-portal/backend
   docker-compose up -d
   ```

### Option 5: VPS/Server (DigitalOcean, Linode, etc.)

1. **Server setup**
   ```bash
   # Install Python 3.11
   sudo apt update
   sudo apt install python3.11 python3.11-venv
   
   # Install Nginx
   sudo apt install nginx
   ```

2. **Deploy with Gunicorn**
   ```bash
   cd student-learning-portal/backend
   pip install -r requirements.txt
   gunicorn --bind 0.0.0.0:5000 wsgi:application
   ```

3. **Configure Nginx reverse proxy**
   ```nginx
   # /etc/nginx/sites-available/ai-mantraas
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | Service account email | Yes |
| `GOOGLE_PRIVATE_KEY` | Private key from service account | Yes |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | ID of your Google Sheet | Yes |
| `GOOGLE_SHEETS_API_KEY` | Google Sheets API key | No |
| `GOOGLE_CLIENT_ID` | OAuth client ID | No |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret | No |
| `JOIN_REQUESTS_SHEET` | Sheet name for join requests | Yes |
| `USERS_SHEET` | Sheet name for users | Yes |
| `APP_NAME` | Application name | No |
| `APP_URL` | Application URL | No |
| `DEBUG_MODE` | Set to False for production | Yes |

## 🔐 Security Notes

- **NEVER commit `.env` file** to version control
- Always use **HTTPS** in production
- Keep your **Google service account credentials** secure
- Set `DEBUG_MODE=False` in production
- Use **strong secrets** for production deployments

## 🐛 Troubleshooting

### Google Sheets Connection Issues

1. Verify Google Sheets API is enabled in Google Cloud Console
2. Check service account has access to the spreadsheet
3. Verify private key format (use `\n` for newlines)

### Port Already in Use

```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (Windows)
taskkill /PID <process-id> /F

# Or use a different port
python app.py --port 5001
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or upgrade pip
pip install --upgrade pip
```

## 📄 License

This project is for educational purposes.

## 👏 Support

For issues or questions, please contact the development team.

## 🔗 API Endpoints

The backend serves both frontend and API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main landing page (index.html) |
| `/for-business.html` | GET | Business page |
| `/health` | GET | Health check |
| `/api` | GET | API info |
| `/api/join-requests` | GET/POST | Submit join requests |
| `/api/users` | GET/POST | User management |
| `/api/lectures` | GET/POST | Lecture management |
| `/api/live-classes` | GET/POST | Live class management |
| `/api/plans` | GET/POST | Plan management |
| `/api/progress` | GET/POST | Progress tracking |
| `/api/sync` | POST | Sync data to Google Sheets |

## 🔗 Useful Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Render Deployment Docs](https://render.com/docs)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Docker Getting Started](https://docs.docker.com/get-started/)
