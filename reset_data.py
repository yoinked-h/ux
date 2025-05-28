#!/usr/bin/env python3
"""
Data management scripts for AI Model Hub
Use these scripts to reset or wipe the database files
"""

import orjson as json
from pathlib import Path
import time
import uuid
import hashlib

# JSON Database paths
MODELS_JSON = Path('data/models.json')
USERS_JSON = Path('data/users.json')
COMMENTS_JSON = Path('data/comments.json')

def wipe_all_data():
    """Completely wipe all data - removes all users, models, and comments"""
    print("🗑️  Wiping all data...")
    
    # Create empty data files
    MODELS_JSON.parent.mkdir(exist_ok=True)
    
    with MODELS_JSON.open('wb') as f:
        f.write(json.dumps([], option=json.OPT_INDENT_2))
    
    with USERS_JSON.open('wb') as f:
        f.write(json.dumps([], option=json.OPT_INDENT_2))
    
    with COMMENTS_JSON.open('wb') as f:
        f.write(json.dumps([], option=json.OPT_INDENT_2))
    
    print("✅ All data wiped successfully!")

def reset_to_sample_data():
    """Reset database with sample data for testing"""
    print("🔄 Resetting to sample data...")
    
    # Create sample users
    sample_users = [
        {
            "id": str(uuid.uuid4()),
            "username": "alice_ai",
            "email": "alice@example.com",
            "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
            "join_date": int(time.time()) - 86400 * 30,  # 30 days ago
            "bio": "AI researcher focused on computer vision models",
            "avatar_url": "https://picsum.photos/100/100?random=1"
        },
        {
            "id": str(uuid.uuid4()),
            "username": "bob_ml",
            "email": "bob@example.com", 
            "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
            "join_date": int(time.time()) - 86400 * 15,  # 15 days ago
            "bio": "Machine learning engineer specializing in NLP",
            "avatar_url": "https://picsum.photos/100/100?random=2"
        },
        {
            "id": str(uuid.uuid4()),
            "username": "carol_dev",
            "email": "carol@example.com",
            "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
            "join_date": int(time.time()) - 86400 * 7,  # 7 days ago
            "bio": "Full-stack developer exploring AI integration",
            "avatar_url": "https://picsum.photos/100/100?random=3"
        }
    ]
    
    # Create sample models
    sample_models = [
        {
            "id": str(uuid.uuid4()),
            "title": "Advanced Vision Transformer",
            "description": "# Advanced Vision Transformer\n\nA state-of-the-art vision transformer model for image classification.\n\n## Features\n- High accuracy on ImageNet\n- Efficient attention mechanism\n- Transfer learning ready\n\n## Usage\n```python\nimport torch\nmodel = load_model('advanced_vit')\n```",
            "model_link": "https://huggingface.co/models/advanced-vit",
            "image_url": "https://picsum.photos/400/300?random=10",
            "type": "A",
            "subtype": "A.1",
            "uploader_id": sample_users[0]["id"],
            "upload_date": int(time.time()) - 86400 * 5,  # 5 days ago
            "views": 156,
            "downloads": 23,
            "rating": 4.8,
            "tags": ["vision", "transformer", "classification"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Neural Language Model",
            "description": "# Neural Language Model\n\nA powerful language model trained on diverse text data.\n\n## Capabilities\n- Text generation\n- Question answering\n- Summarization\n\n**Note**: Requires GPU for optimal performance.",
            "model_link": "https://huggingface.co/models/neural-lm",
            "image_url": "https://picsum.photos/400/300?random=11",
            "type": "B",
            "subtype": "B.1",
            "uploader_id": sample_users[1]["id"],
            "upload_date": int(time.time()) - 86400 * 3,  # 3 days ago
            "views": 89,
            "downloads": 12,
            "rating": 4.2,
            "tags": ["nlp", "language-model", "generation"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Efficient Object Detection",
            "description": "# Efficient Object Detection\n\nLightweight object detection model optimized for mobile deployment.\n\n## Performance\n- Real-time inference\n- Low memory footprint\n- High accuracy\n\n## Supported Objects\n- Person, car, bicycle, dog, cat\n- And 75+ other common objects",
            "model_link": "https://github.com/models/efficient-detection",
            "image_url": "https://picsum.photos/400/300?random=12",
            "type": "A",
            "subtype": "A.2",
            "uploader_id": sample_users[2]["id"],
            "upload_date": int(time.time()) - 86400 * 1,  # 1 day ago
            "views": 234,
            "downloads": 45,
            "rating": 4.9,
            "tags": ["detection", "mobile", "real-time"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Final Recommendation System",
            "description": "# Final Recommendation System\n\nComplete recommendation system using collaborative filtering.\n\n## Features\n- User-based recommendations\n- Item similarity analysis\n- Cold start handling\n\n```python\nrecommender = FinalRecommender()\nrecommendations = recommender.get_recommendations(user_id)\n```",
            "model_link": "https://kaggle.com/models/final-recommender",
            "image_url": "https://picsum.photos/400/300?random=13",
            "type": "B",
            "subtype": "B.final",
            "uploader_id": sample_users[0]["id"],
            "upload_date": int(time.time()) - 86400 * 10,  # 10 days ago
            "views": 67,
            "downloads": 8,
            "rating": 3.8,
            "tags": ["recommendation", "collaborative-filtering", "ml"]
        }
    ]
    
    # Create sample comments
    sample_comments = [
        {
            "id": str(uuid.uuid4()),
            "model_id": sample_models[0]["id"],
            "user_id": sample_users[1]["id"],
            "comment": "Excellent model! Very accurate and easy to use.",
            "rating": 5,
            "date": int(time.time()) - 86400 * 2
        },
        {
            "id": str(uuid.uuid4()),
            "model_id": sample_models[0]["id"],
            "user_id": sample_users[2]["id"],
            "comment": "Good performance but could use better documentation.",
            "rating": 4,
            "date": int(time.time()) - 86400 * 1
        },
        {
            "id": str(uuid.uuid4()),
            "model_id": sample_models[1]["id"],
            "user_id": sample_users[0]["id"],
            "comment": "Works well for my NLP tasks. Recommended!",
            "rating": 4,
            "date": int(time.time()) - 86400 * 1
        }
    ]
    
    # Save sample data
    MODELS_JSON.parent.mkdir(exist_ok=True)
    
    with MODELS_JSON.open('wb') as f:
        f.write(json.dumps(sample_models, option=json.OPT_INDENT_2))
    
    with USERS_JSON.open('wb') as f:
        f.write(json.dumps(sample_users, option=json.OPT_INDENT_2))
    
    with COMMENTS_JSON.open('wb') as f:
        f.write(json.dumps(sample_comments, option=json.OPT_INDENT_2))
    
    print("✅ Sample data created successfully!")
    print("\n📋 Sample user accounts:")
    for user in sample_users:
        print(f"  Username: {user['username']}, Password: password123")

def wipe_models_only():
    """Wipe only models and comments, keep users"""
    print("🗑️  Wiping models and comments...")
    
    MODELS_JSON.parent.mkdir(exist_ok=True)
    
    with MODELS_JSON.open('wb') as f:
        f.write(json.dumps([], option=json.OPT_INDENT_2))
    
    with COMMENTS_JSON.open('wb') as f:
        f.write(json.dumps([], option=json.OPT_INDENT_2))
    
    print("✅ Models and comments wiped successfully!")

def show_stats():
    """Show current database statistics"""
    print("📊 Current Database Statistics:")
    
    try:
        with USERS_JSON.open('rb') as f:
            users = json.loads(f.read())
        print(f"  👥 Users: {len(users)}")
    except:
        print("  👥 Users: 0 (file not found)")
    
    try:
        with MODELS_JSON.open('rb') as f:
            models = json.loads(f.read())
        print(f"  🤖 Models: {len(models)}")
    except:
        print("  🤖 Models: 0 (file not found)")
    
    try:
        with COMMENTS_JSON.open('rb') as f:
            comments = json.loads(f.read())
        print(f"  💬 Comments: {len(comments)}")
    except:
        print("  💬 Comments: 0 (file not found)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🔧 AI Model Hub Data Management")
        print("\nUsage:")
        print("  python reset_data.py wipe        # Wipe all data")
        print("  python reset_data.py reset       # Reset to sample data")
        print("  python reset_data.py wipe-models # Wipe only models/comments")
        print("  python reset_data.py stats       # Show current statistics")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "wipe":
        confirm = input("⚠️  This will delete ALL data. Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            wipe_all_data()
        else:
            print("❌ Operation cancelled")
    elif command == "reset":
        confirm = input("⚠️  This will replace all data with samples. Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            reset_to_sample_data()
        else:
            print("❌ Operation cancelled")
    elif command == "wipe-models":
        confirm = input("⚠️  This will delete all models and comments. Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            wipe_models_only()
        else:
            print("❌ Operation cancelled")
    elif command == "stats":
        show_stats()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
