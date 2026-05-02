"""
AI Mantraas Student Portal - Backend API
=========================================
Flask-based REST API for the student learning portal.
Handles user management, join requests, lectures, and live classes.
Integrates with Google Sheets for data storage.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from google_sheets import get_sheets_manager, initialize_sheets

# Try to import whitenoise for static file serving
try:
    from whitenoise import WhiteNoise
    WHITENOISE_AVAILABLE = True
except ImportError:
    WHITENOISE_AVAILABLE = False
    print("Warning: whitenoise not installed. Static files won't be served efficiently.")

# Load environment variables - look in multiple locations
possible_env_paths = [
    os.path.join(os.path.dirname(__file__), '.env'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
]

for env_path in possible_env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loading .env from: {env_path}")
        break

# Get debug mode from environment
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
# Note: index.html is in the project root (two levels up from backend)
app = Flask(__name__, static_folder=None)
CORS(app)

# Get the project root directory (two levels up from backend)
# app.py is at: project-root/student-learning-portal/backend/app.py
# index.html is at: project-root/index.html
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BACKEND_DIR))
print(f"PROJECT_ROOT: {PROJECT_ROOT}")

# Configure whitenoise for static file serving
if WHITENOISE_AVAILABLE:
    # Find the static files directory
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=static_dir, prefix='static/')
    print(f"Static files will be served from: {static_dir}")

# Configuration
app.config['JSON_SORT_KEYS'] = False
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DATA_DIR = os.path.join(BASE_DIR, 'local-data')

# Ensure local-data directory exists
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)

# Google Sheets Manager
sheets_manager = None


def load_json_file(filename, default=None):
    """Load data from a JSON file."""
    filepath = os.path.join(LOCAL_DATA_DIR, filename)
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return default


def save_json_file(filename, data):
    """Save data to a JSON file."""
    filepath = os.path.join(LOCAL_DATA_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False


def save_to_google_sheets(sheet_name, data, is_list=False):
    """
    Save data to Google Sheets.
    
    Args:
        sheet_name: Name of the sheet
        data: Data to save (dict or list of dicts)
        is_list: Whether data is a list of records
        
    Returns:
        True if successful, False otherwise
    """
    global sheets_manager
    
    if sheets_manager is None or not sheets_manager.is_connected():
        logger.warning("Google Sheets not connected, skipping sheet update")
        return False
    
    try:
        # Ensure the sheet exists
        sheets_manager.get_or_create_sheet(sheet_name)
        
        if is_list and isinstance(data, list) and len(data) > 0:
            # Convert list of dicts to rows
            # Get headers from first item
            headers = list(data[0].keys())
            rows = [headers]
            
            for item in data:
                row = [str(item.get(header, '')) for header in headers]
                rows.append(row)
            
            return sheets_manager.write_to_sheet(f"{sheet_name}!A1", rows)
            
        elif isinstance(data, dict):
            # For single row, we need to check if sheet has headers
            # First read to see if there are any existing rows
            existing_data = sheets_manager.read_sheet(f"{sheet_name}!A1:Z1")
            
            if not existing_data or len(existing_data) == 0:
                # No headers, write the dict keys as headers first
                headers = list(data.keys())
                rows = [headers]
                sheets_manager.write_to_sheet(f"{sheet_name}!A1", rows)
            
            # Now append the values
            values = [str(v) for v in data.values()]
            return sheets_manager.append_to_sheet(sheet_name, values)
        
        return False
        
    except Exception as e:
        logger.error(f"Error saving to Google Sheets: {e}")
        return False


# ==================== Static Files & Health ====================

@app.route('/')
def root():
    """Serve index.html for root URL."""
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/index.html')
def index_html():
    """Serve index.html explicitly."""
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/saarthi.html')
def saarthi():
    """Serve saarthi.html."""
    return send_from_directory(PROJECT_ROOT, 'saarthi.html')

@app.route('/for-business.html')
def for_business():
    """Serve for-business.html."""
    return send_from_directory(PROJECT_ROOT, 'for-business.html')

@app.route('/health')
def health():
    """Health check endpoint for deployment platforms."""
    return jsonify({
        'status': 'healthy',
        'google_sheets_connected': sheets_manager is not None and sheets_manager.is_connected()
    })

# ==================== API Routes ====================

@app.route('/api')
def api_index():
    """API root endpoint."""
    return jsonify({
        'name': 'AI Mantraas Student Portal API',
        'version': '1.0.0',
        'status': 'running',
        'google_sheets_connected': sheets_manager is not None and sheets_manager.is_connected()
    })


# ==================== Business Contact ====================

@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle business contact forms."""
    if request.method == 'POST':
        contact_data = request.get_json()
        
        # Add timestamp and type
        contact_data['id'] = str(datetime.now().timestamp())
        contact_data['created_at'] = datetime.now().isoformat()
        contact_data['status'] = 'new'
        
        # Load existing data
        contacts_list = load_json_file('business_inquiries.json', [])
        contacts_list.append(contact_data)
        
        # Save to local file
        save_json_file('business_inquiries.json', contacts_list)
        
        # Try to save to Google Sheets
        save_to_google_sheets('BusinessInquiries', contact_data)
        
        return jsonify({'success': True, 'message': 'Contact form submitted successfully', 'data': contact_data})


# ==================== Join Requests ====================

@app.route('/api/join-requests', methods=['GET', 'POST'])
def join_requests():
    """Handle join requests."""
    if request.method == 'GET':
        data = load_json_file('join_requests.json', [])
        return jsonify(data)
    
    elif request.method == 'POST':
        new_request = request.get_json()
        
        # Add timestamp
        new_request['id'] = str(datetime.now().timestamp())
        new_request['created_at'] = datetime.now().isoformat()
        new_request['status'] = 'pending'
        
        # Load existing data
        requests_list = load_json_file('join_requests.json', [])
        requests_list.append(new_request)
        
        # Save to local file
        save_json_file('join_requests.json', requests_list)
        
        # Try to save to Google Sheets
        save_to_google_sheets('JoinRequests', new_request)
        
        return jsonify({'success': True, 'message': 'Join request submitted', 'data': new_request})


@app.route('/api/join-requests/<request_id>', methods=['GET', 'PUT', 'DELETE'])
def join_request_detail(request_id):
    """Handle individual join request."""
    requests_list = load_json_file('join_requests.json', [])
    
    # Find the request
    index = next((i for i, r in enumerate(requests_list) if r.get('id') == request_id), None)
    
    if index is None:
        return jsonify({'error': 'Request not found'}), 404
    
    if request.method == 'GET':
        return jsonify(requests_list[index])
    
    elif request.method == 'PUT':
        updated_data = request.get_json()
        requests_list[index].update(updated_data)
        save_json_file('join_requests.json', requests_list)
        return jsonify({'success': True, 'data': requests_list[index]})
    
    elif request.method == 'DELETE':
        requests_list.pop(index)
        save_json_file('join_requests.json', requests_list)
        return jsonify({'success': True, 'message': 'Request deleted'})


# ==================== Users ====================

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    """Handle users."""
    if request.method == 'GET':
        data = load_json_file('users.json', [])
        return jsonify(data)
    
    elif request.method == 'POST':
        new_user = request.get_json()
        
        # Add timestamp
        new_user['id'] = str(datetime.now().timestamp())
        new_user['created_at'] = datetime.now().isoformat()
        
        # Load existing data
        users_list = load_json_file('users.json', [])
        users_list.append(new_user)
        
        # Save to local file
        save_json_file('users.json', users_list)
        
        # Try to save to Google Sheets
        save_to_google_sheets('Users', users_list, is_list=True)
        
        return jsonify({'success': True, 'message': 'User created', 'data': new_user})


@app.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_detail(user_id):
    """Handle individual user."""
    users_list = load_json_file('users.json', [])
    
    # Find the user
    index = next((i for i, u in enumerate(users_list) if u.get('id') == user_id), None)
    
    if index is None:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'GET':
        return jsonify(users_list[index])
    
    elif request.method == 'PUT':
        updated_data = request.get_json()
        users_list[index].update(updated_data)
        save_json_file('users.json', users_list)
        
        # Update Google Sheets
        save_to_google_sheets('Users', users_list, is_list=True)
        
        return jsonify({'success': True, 'data': users_list[index]})
    
    elif request.method == 'DELETE':
        users_list.pop(index)
        save_json_file('users.json', users_list)
        
        # Update Google Sheets
        save_to_google_sheets('Users', users_list, is_list=True)
        
        return jsonify({'success': True, 'message': 'User deleted'})


# ==================== Lectures ====================

@app.route('/api/lectures', methods=['GET', 'POST'])
def lectures():
    """Handle lectures."""
    if request.method == 'GET':
        data = load_json_file('lectures.json', [])
        return jsonify(data)
    
    elif request.method == 'POST':
        new_lecture = request.get_json()
        
        # Add timestamp
        new_lecture['id'] = str(datetime.now().timestamp())
        new_lecture['created_at'] = datetime.now().isoformat()
        
        # Load existing data
        lectures_list = load_json_file('lectures.json', [])
        lectures_list.append(new_lecture)
        
        # Save to local file
        save_json_file('lectures.json', lectures_list)
        
        return jsonify({'success': True, 'message': 'Lecture created', 'data': new_lecture})


@app.route('/api/lectures/<lecture_id>', methods=['GET', 'PUT', 'DELETE'])
def lecture_detail(lecture_id):
    """Handle individual lecture."""
    lectures_list = load_json_file('lectures.json', [])
    
    # Find the lecture
    index = next((i for i, l in enumerate(lectures_list) if l.get('id') == lecture_id), None)
    
    if index is None:
        return jsonify({'error': 'Lecture not found'}), 404
    
    if request.method == 'GET':
        return jsonify(lectures_list[index])
    
    elif request.method == 'PUT':
        updated_data = request.get_json()
        lectures_list[index].update(updated_data)
        save_json_file('lectures.json', lectures_list)
        return jsonify({'success': True, 'data': lectures_list[index]})
    
    elif request.method == 'DELETE':
        lectures_list.pop(index)
        save_json_file('lectures.json', lectures_list)
        return jsonify({'success': True, 'message': 'Lecture deleted'})


# ==================== Live Classes ====================

@app.route('/api/live-classes', methods=['GET', 'POST'])
def live_classes():
    """Handle live classes."""
    if request.method == 'GET':
        data = load_json_file('live_classes.json', [])
        return jsonify(data)
    
    elif request.method == 'POST':
        new_class = request.get_json()
        
        # Add timestamp
        new_class['id'] = str(datetime.now().timestamp())
        new_class['created_at'] = datetime.now().isoformat()
        
        # Load existing data
        classes_list = load_json_file('live_classes.json', [])
        classes_list.append(new_class)
        
        # Save to local file
        save_json_file('live_classes.json', classes_list)
        
        return jsonify({'success': True, 'message': 'Live class created', 'data': new_class})


@app.route('/api/live-classes/<class_id>', methods=['GET', 'PUT', 'DELETE'])
def live_class_detail(class_id):
    """Handle individual live class."""
    classes_list = load_json_file('live_classes.json', [])
    
    # Find the class
    index = next((i for i, c in enumerate(classes_list) if c.get('id') == class_id), None)
    
    if index is None:
        return jsonify({'error': 'Live class not found'}), 404
    
    if request.method == 'GET':
        return jsonify(classes_list[index])
    
    elif request.method == 'PUT':
        updated_data = request.get_json()
        classes_list[index].update(updated_data)
        save_json_file('live_classes.json', classes_list)
        return jsonify({'success': True, 'data': classes_list[index]})
    
    elif request.method == 'DELETE':
        classes_list.pop(index)
        save_json_file('live_classes.json', classes_list)
        return jsonify({'success': True, 'message': 'Live class deleted'})


# ==================== Plans ====================

@app.route('/api/plans', methods=['GET', 'POST'])
def plans():
    """Handle plans."""
    if request.method == 'GET':
        data = load_json_file('plans.json', [])
        return jsonify(data)
    
    elif request.method == 'POST':
        new_plan = request.get_json()
        
        # Add timestamp
        new_plan['id'] = str(datetime.now().timestamp())
        new_plan['created_at'] = datetime.now().isoformat()
        
        # Load existing data
        plans_list = load_json_file('plans.json', [])
        plans_list.append(new_plan)
        
        # Save to local file
        save_json_file('plans.json', plans_list)
        
        return jsonify({'success': True, 'message': 'Plan created', 'data': new_plan})


@app.route('/api/plans/<plan_id>', methods=['GET', 'PUT', 'DELETE'])
def plan_detail(plan_id):
    """Handle individual plan."""
    plans_list = load_json_file('plans.json', [])
    
    # Find the plan
    index = next((i for i, p in enumerate(plans_list) if p.get('id') == plan_id), None)
    
    if index is None:
        return jsonify({'error': 'Plan not found'}), 404
    
    if request.method == 'GET':
        return jsonify(plans_list[index])
    
    elif request.method == 'PUT':
        updated_data = request.get_json()
        plans_list[index].update(updated_data)
        save_json_file('plans.json', plans_list)
        return jsonify({'success': True, 'data': plans_list[index]})
    
    elif request.method == 'DELETE':
        plans_list.pop(index)
        save_json_file('plans.json', plans_list)
        return jsonify({'success': True, 'message': 'Plan deleted'})


# ==================== Progress ====================

@app.route('/api/progress', methods=['GET', 'POST'])
def progress():
    """Handle progress tracking."""
    if request.method == 'GET':
        data = load_json_file('progress.json', [])
        return jsonify(data)
    
    elif request.method == 'POST':
        new_progress = request.get_json()
        
        # Add timestamp
        new_progress['id'] = str(datetime.now().timestamp())
        new_progress['created_at'] = datetime.now().isoformat()
        
        # Load existing data
        progress_list = load_json_file('progress.json', [])
        progress_list.append(new_progress)
        
        # Save to local file
        save_json_file('progress.json', progress_list)
        
        return jsonify({'success': True, 'message': 'Progress recorded', 'data': new_progress})


@app.route('/api/progress/<user_id>', methods=['GET'])
def user_progress(user_id):
    """Get progress for a specific user."""
    progress_list = load_json_file('progress.json', [])
    user_progress = [p for p in progress_list if p.get('user_id') == user_id]
    return jsonify(user_progress)


# ==================== Status ====================

@app.route('/api/status', methods=['GET'])
def status():
    """Get API status."""
    return jsonify({
        'status': 'running',
        'google_sheets_connected': sheets_manager is not None and sheets_manager.is_connected(),
        'local_data_dir': LOCAL_DATA_DIR,
        'files': os.listdir(LOCAL_DATA_DIR) if os.path.exists(LOCAL_DATA_DIR) else []
    })


# ==================== Sync ====================

@app.route('/api/sync', methods=['POST'])
def sync_to_google_sheets():
    """Sync all local data to Google Sheets."""
    global sheets_manager
    
    if sheets_manager is None or not sheets_manager.is_connected():
        return jsonify({
            'success': False, 
            'message': 'Google Sheets not connected'
        }), 500
    
    results = {}
    
    # Sync each data type
    data_files = [
        ('JoinRequests', 'join_requests.json'),
        ('Users', 'users.json'),
        ('Lectures', 'lectures.json'),
        ('LiveClasses', 'live_classes.json'),
        ('Plans', 'plans.json'),
        ('Progress', 'progress.json')
    ]
    
    for sheet_name, filename in data_files:
        data = load_json_file(filename, [])
        if len(data) > 0:
            success = save_to_google_sheets(sheet_name, data, is_list=True)
            results[sheet_name] = 'synced' if success else 'failed'
        else:
            results[sheet_name] = 'empty'
    
    return jsonify({
        'success': True,
        'message': 'Data synced to Google Sheets',
        'results': results
    })


# ==================== Initialize ====================

def initialize_app():
    """Initialize the application."""
    global sheets_manager
    
    # Try to initialize Google Sheets
    try:
        sheets_manager = initialize_sheets()
        if sheets_manager and sheets_manager.is_connected():
            logger.info("Google Sheets connection established")
        else:
            logger.warning("Could not connect to Google Sheets - will use local storage only")
    except Exception as e:
        logger.error(f"Error initializing Google Sheets: {e}")
        sheets_manager = None
    
    # Create default data files if they don't exist
    default_files = {
        'join_requests.json': [],
        'business_inquiries.json': [],
        'users.json': [],
        'lectures.json': [],
        'live_classes.json': [],
        'plans.json': [],
        'progress.json': []
    }
    
    for filename, default_data in default_files.items():
        filepath = os.path.join(LOCAL_DATA_DIR, filename)
        if not os.path.exists(filepath):
            save_json_file(filename, default_data)
    
    logger.info("Application initialized")


# Serve favicon and logo from root directory
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(PROJECT_ROOT, 'bglogo.png', mimetype='image/png')

@app.route('/bglogo.png')
def logo():
    return send_from_directory(PROJECT_ROOT, 'bglogo.png', mimetype='image/png')

# Serve static images
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(PROJECT_ROOT, filename)


def create_app():
    """Create and configure the Flask application."""
    initialize_app()
    return app


if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=DEBUG_MODE)
