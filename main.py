import flask
from flask import Flask, request, jsonify, session
import orjson as json
import time
import uuid
import hashlib
from pathlib import Path
import markdown

# JSON Database paths
MODELS_JSON = Path('data/models.json')
USERS_JSON = Path('data/users.json')
COMMENTS_JSON = Path('data/comments.json')

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
# Routes
@app.route('/', methods=['GET'])
def index():
    return flask.send_from_directory('static', 'home.html')

@app.route('/search', methods=['GET'])
def search():
    return flask.send_from_directory('static', 'search.html')

@app.route('/model/<model_id>', methods=['GET'])
def model_page(model_id):
    return flask.send_from_directory('static', 'model.html')

# User Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400
    
    users = load_json_data(USERS_JSON)
    
    # Check if user already exists
    if any(user['username'] == username or user['email'] == email for user in users):
        return jsonify({"error": "User already exists"}), 400
    
    # Create new user
    new_user = {
        "id": generate_id(),
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "join_date": int(time.time()),
        "bio": "",
        "avatar_url": f"https://picsum.photos/100/100?random={len(users) + 100}"
    }
    
    users.append(new_user)
    save_json_data(USERS_JSON, users)
    
    session['user_id'] = new_user['id']
    
    return jsonify({"message": "User registered successfully", "user": {
        "id": new_user['id'],
        "username": new_user['username'],
        "email": new_user['email']
    }})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({"error": "Missing username or password"}), 400
    
    users = load_json_data(USERS_JSON)
    user = next((user for user in users if user['username'] == username), None)
    
    if not user or user['password_hash'] != hash_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    session['user_id'] = user['id']
    
    return jsonify({"message": "Login successful", "user": {
        "id": user['id'],
        "username": user['username'],
        "email": user['email']
    }})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"})

@app.route('/api/current-user', methods=['GET'])
def current_user():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401
    
    return jsonify({
        "id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "bio": user.get('bio', ''),
        "avatar_url": user.get('avatar_url', '')
    })

# Model Routes
@app.route('/api/models', methods=['GET'])
def get_models():
    models = load_json_data(MODELS_JSON)
    users = load_json_data(USERS_JSON)
    
    # Add uploader information and convert markdown for preview
    for model in models:
        uploader = next((user for user in users if user['id'] == model['uploader_id']), None)
        if uploader:
            model['uploader_username'] = uploader['username']
            model['uploader_avatar'] = uploader.get('avatar_url', '')
        
        # Convert markdown description to HTML for preview (first 100 chars)
        if model.get('description'):
            # Create a brief HTML preview (strip markdown formatting for card view)
            description_text = model['description'][:100] + ('...' if len(model['description']) > 100 else '')
            model['description_preview'] = description_text
    
    # Filter by type/subtype if provided
    model_type = request.args.get('type')
    subtype = request.args.get('subtype')
    search = request.args.get('search', '').lower()
    
    if model_type:
        models = [m for m in models if m['type'] == model_type]
    
    if subtype:
        models = [m for m in models if m['subtype'] == subtype]
    
    if search:
        models = [m for m in models if search in m['title'].lower() or 
                 search in m['description'].lower() or
                 any(search in tag.lower() for tag in m.get('tags', []))]
    
    return jsonify(models)

@app.route('/api/models/<model_id>', methods=['GET'])
def get_model(model_id):
    models = load_json_data(MODELS_JSON)
    users = load_json_data(USERS_JSON)
    comments = load_json_data(COMMENTS_JSON)
    
    model = next((model for model in models if model['id'] == model_id), None)
    if not model:
        return jsonify({"error": "Model not found"}), 404
    
    # Convert markdown description to HTML
    if model.get('description'):
        model['description_html'] = markdown.markdown(
            model['description'], 
            extensions=['fenced_code', 'tables', 'nl2br']
        )
    
    # Add uploader information
    uploader = next((user for user in users if user['id'] == model['uploader_id']), None)
    if uploader:
        model['uploader_username'] = uploader['username']
        model['uploader_avatar'] = uploader.get('avatar_url', '')
    
    # Add comments with markdown conversion
    model_comments = [c for c in comments if c['model_id'] == model_id]
    for comment in model_comments:
        user = next((user for user in users if user['id'] == comment['user_id']), None)
        if user:
            comment['username'] = user['username']
            comment['avatar_url'] = user.get('avatar_url', '')
        # Convert comment markdown to HTML
        if comment.get('comment'):
            comment['comment_html'] = markdown.markdown(
                comment['comment'], 
                extensions=['fenced_code', 'tables', 'nl2br']
            )
    
    model['comments'] = model_comments
    
    # Increment view count
    for i, m in enumerate(models):
        if m['id'] == model_id:
            models[i]['views'] = models[i].get('views', 0) + 1
            break
    save_json_data(MODELS_JSON, models)
    
    return jsonify(model)

@app.route('/api/models', methods=['POST'])
def upload_model():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Must be logged in to upload models"}), 401
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    model_link = data.get('model_link')
    image_url = data.get('image_url')
    model_type = data.get('type')
    subtype = data.get('subtype')
    tags = data.get('tags', [])
    
    if not all([title, description, model_link, image_url, model_type, subtype]):
        return jsonify({"error": "Missing required fields"}), 400
    
    models = load_json_data(MODELS_JSON)
    
    new_model = {
        "id": generate_id(),
        "title": title,
        "description": description,
        "model_link": model_link,
        "image_url": image_url,
        "type": model_type,
        "subtype": subtype,
        "uploader_id": current_user['id'],
        "upload_date": int(time.time()),
        "views": 0,
        "downloads": 0,
        "rating": 0,
        "tags": tags
    }
    
    models.append(new_model)
    save_json_data(MODELS_JSON, models)
    
    return jsonify({"message": "Model uploaded successfully", "model": new_model})

# Comments and Reviews Routes
@app.route('/api/models/<model_id>/comments', methods=['POST'])
def add_comment(model_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Must be logged in to comment"}), 401
    
    data = request.get_json()
    comment_text = data.get('comment')
    rating = data.get('rating', 0)
    
    if not comment_text:
        return jsonify({"error": "Comment text required"}), 400
    
    comments = load_json_data(COMMENTS_JSON)
    
    new_comment = {
        "id": generate_id(),
        "model_id": model_id,
        "user_id": current_user['id'],
        "comment": comment_text,
        "rating": rating,
        "date": int(time.time())
    }
    
    comments.append(new_comment)
    save_json_data(COMMENTS_JSON, comments)
    
    # Update model rating
    if rating > 0:
        models = load_json_data(MODELS_JSON)
        model_comments = [c for c in comments if c['model_id'] == model_id and c['rating'] > 0]
        avg_rating = sum(c['rating'] for c in model_comments) / len(model_comments)
        
        for i, model in enumerate(models):
            if model['id'] == model_id:
                models[i]['rating'] = round(avg_rating, 1)
                break
        
        save_json_data(MODELS_JSON, models)
    
    return jsonify({"message": "Comment added successfully", "comment": new_comment})

@app.route('/api/model-types', methods=['GET'])
def get_model_types():
    return jsonify({
        "A": ["A.1", "A.2"],
        "B": ["B.1", "B.final"],
        "C": ["C.1"]
    })

@app.route('/api/models/<model_id>/download', methods=['POST'])
def download_model(model_id):
    models = load_json_data(MODELS_JSON)
    
    # Increment download count
    for i, model in enumerate(models):
        if model['id'] == model_id:
            models[i]['downloads'] = models[i].get('downloads', 0) + 1
            break
    
    save_json_data(MODELS_JSON, models)
    return jsonify({"message": "Download counted"})

# ...existing code...

def top_score_calc(mod):
    views = mod.get('views', 0)
    downloads = mod.get('downloads', 0)
    date = mod.get('date', 0)
    rating = mod.get('rating', 0.5)
    if views == 0:
        views = 1
    if downloads == 0:
        downloads = 1
    ratio = views/downloads
    # if in last week, set datefactor to 1.5, else scale smoothly with time
    if date == 0:
        date = time.time()
    else:
        date = float(date)
    datefactor = 1.5 if time.time() - date < 604800 else max((time.time() - date) / 604800, 0)
    score = (rating**2) * ratio + (50 * datefactor)
    score = score * downloads
    return score
    
@app.route('/api/top_models', methods=['GET'])
def get_top_models():
    models = load_json_data(MODELS_JSON)
    if not models:
        return jsonify([])
    
    top_models = sorted(models, key=lambda x: top_score_calc(x), reverse=True)[:10]
    return jsonify(top_models)
@app.route('/<path:path>', methods=['GET'])
def static_files(path):
    return flask.send_from_directory('static', path)

# Utility functions for database operations
def load_json_data(file_path):
    """Load data from JSON file"""
    if not file_path.exists():
        return []
    try:
        with file_path.open('rb') as f:
            return json.loads(f.read())
    except:
        return []

def save_json_data(file_path, data):
    """Save data to JSON file"""
    file_path.parent.mkdir(exist_ok=True)
    with file_path.open('wb') as f:
        f.write(json.dumps(data, option=json.OPT_INDENT_2))

def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())

def get_current_user():
    """Get current logged in user"""
    if 'user_id' not in session:
        return None
    users = load_json_data(USERS_JSON)
    return next((user for user in users if user['id'] == session['user_id']), None)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')