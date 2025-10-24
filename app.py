from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from utils.instagram_api import InstagramAPI
from utils.download_manager import DownloadService
from utils.analytics import AnalyticsService
import config
import os
from datetime import datetime, timedelta
import traceback

app = Flask(__name__)
app.config.from_object(config.config['default'])

# Initialize managers - without MongoDB
instagram_api = InstagramAPI()
download_service = DownloadService()
analytics_service = AnalyticsService()

# Jinja2 Filters
@app.template_filter('format_number')
def format_number_filter(num):
    """Format large numbers with K/M suffixes"""
    if not num:
        return '0'
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    return str(num)

@app.template_filter('format_time_ago')
def format_time_ago_filter(dt):
    """Format datetime as time ago"""
    if not dt:
        return "Unknown"
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

@app.template_filter('tojson')
def tojson_filter(obj):
    """Convert object to JSON string"""
    import json
    return json.dumps(obj, default=str)

@app.template_filter('is_limited_data')
def is_limited_data_filter(profile):
    """Check if profile data is limited"""
    return profile.get('is_limited_data', False)

@app.route('/')
def index():
    """Home page with search"""
    return render_template('index.html')

@app.route('/search')
def search_profiles():
    """Search for Instagram profiles"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    try:
        print(f"🔍 Searching for: {query}")
        profiles = instagram_api.search_profiles(query)
        return render_template('index.html', profiles=profiles, search_query=query)
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f"Search failed: {str(e)}")

@app.route('/profile/<username>')
def view_profile(username):
    """View profile details with enhanced private account support"""
    try:
        print(f"👤 Loading profile: {username}")
        
        # First try to get full profile data
        profile_data = instagram_api.get_profile_data(username)
        
        if not profile_data:
            # Try limited data as fallback
            profile_data = instagram_api.get_limited_profile_data(username)
            if not profile_data:
                return render_template('error.html', 
                                    message=f"Profile '@{username}' not found or cannot be accessed.")
        
        # Handle different profile states
        if profile_data.get('is_limited_data'):
            # Limited data profile (basic info only)
            return render_template('profile_limited.html', 
                                profile=profile_data,
                                username=username)
        
        elif profile_data.get('is_private'):
            # Private account with some data
            if profile_data.get('has_preview_content'):
                # Private account with preview content
                return render_template('profile_private_preview.html',
                                    profile=profile_data,
                                    username=username)
            else:
                # Private account without preview content
                return render_template('profile_private.html', 
                                    profile=profile_data,
                                    username=username)
        else:
            # Public account - get full data
            # Removed: profile_manager.save_profile(profile_data)
            posts = instagram_api.get_user_posts(username)
            analytics = analytics_service.analyze_profile(profile_data, posts)
            
            return render_template('profile.html', 
                                 profile=profile_data, 
                                 posts=posts, 
                                 analytics=analytics)
                                 
    except Exception as e:
        print(f"❌ Profile loading error: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f"Error loading profile: {str(e)}")

@app.route('/profile/<username>/limited')
def view_limited_profile(username):
    """View limited profile data for private accounts"""
    try:
        print(f"👤 Loading limited profile: {username}")
        profile_data = instagram_api.get_limited_profile_data(username)
        
        if not profile_data:
            return render_template('error.html', 
                                message=f"Cannot access profile '@{username}'")
        
        return render_template('profile_limited.html',
                             profile=profile_data,
                             username=username)
    except Exception as e:
        print(f"❌ Limited profile loading error: {str(e)}")
        return render_template('error.html', message=f"Error loading limited profile: {str(e)}")

@app.route('/profile/<username>/stories')
def view_stories(username):
    """View user stories"""
    try:
        profile_data = instagram_api.get_profile_data(username)
        
        if not profile_data:
            return render_template('error.html', message="Profile not found")
        
        if profile_data.get('is_private'):
            return render_template('error.html', message="Cannot view stories from private accounts")
        
        stories = instagram_api.get_user_stories(username)
        
        return render_template('stories.html', 
                             profile=profile_data, 
                             stories=stories)
    except Exception as e:
        print(f"❌ Stories loading error: {str(e)}")
        return render_template('error.html', message=f"Error loading stories: {str(e)}")

@app.route('/profile/<username>/posts')
def view_posts(username):
    """View all posts"""
    try:
        profile_data = instagram_api.get_profile_data(username)
        
        if not profile_data:
            return render_template('error.html', message="Profile not found")
        
        if profile_data.get('is_private'):
            return render_template('error.html', message="Cannot view posts from private accounts")
        
        posts = instagram_api.get_user_posts(username, limit=50)
        
        return render_template('posts.html', 
                             profile=profile_data, 
                             posts=posts)
    except Exception as e:
        print(f"❌ Posts loading error: {str(e)}")
        return render_template('error.html', message=f"Error loading posts: {str(e)}")

@app.route('/downloads')
def view_downloads():
    """View download history"""
    try:
        download_stats = download_service.get_download_stats()
        download_history = download_service.get_download_history(limit=50)
        
        return render_template('downloads.html', 
                             stats=download_stats, 
                             downloads=download_history)
    except Exception as e:
        print(f"❌ Downloads loading error: {str(e)}")
        return render_template('error.html', message=f"Error loading downloads: {str(e)}")

@app.route('/analytics/<username>')
def view_analytics(username):
    """View profile analytics"""
    try:
        profile_data = instagram_api.get_profile_data(username)
        
        if not profile_data:
            return render_template('error.html', message="Profile not found")
        
        posts = instagram_api.get_user_posts(username, limit=50)
        analytics = analytics_service.analyze_profile(profile_data, posts)
        
        return render_template('analytics.html', 
                             profile=profile_data, 
                             analytics=analytics)
    except Exception as e:
        print(f"❌ Analytics loading error: {str(e)}")
        return render_template('error.html', message=f"Error loading analytics: {str(e)}")

# Download API Routes
@app.route('/download/story', methods=['POST'])
def download_story():
    """Download a story"""
    try:
        data = request.get_json()
        story_url = data.get('url')
        username = data.get('username')
        story_id = data.get('story_id')
        
        if not all([story_url, username, story_id]):
            return jsonify({'success': False, 'error': 'Missing parameters'})
        
        result = download_service.download_story(story_url, username, story_id)
        
        return jsonify(result)
    except Exception as e:
        print(f"❌ Story download error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/post', methods=['POST'])
def download_post():
    """Download a post"""
    try:
        data = request.get_json()
        post_data = data.get('post_data')
        username = data.get('username')
        
        if not all([post_data, username]):
            return jsonify({'success': False, 'error': 'Missing parameters'})
        
        result = download_service.download_post(post_data, username)
        
        return jsonify(result)
    except Exception as e:
        print(f"❌ Post download error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/profile-pic', methods=['POST'])
def download_profile_pic():
    """Download profile picture"""
    try:
        data = request.get_json()
        profile_data = data.get('profile_data')
        
        if not profile_data:
            return jsonify({'success': False, 'error': 'Missing profile data'})
        
        result = download_service.download_profile_picture(profile_data)
        
        return jsonify(result)
    except Exception as e:
        print(f"❌ Profile pic download error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# API Routes
@app.route('/api/profile/<username>')
def api_profile(username):
    """API endpoint for profile data"""
    try:
        profile_data = instagram_api.get_profile_data(username)
        
        if profile_data:
            return jsonify({'success': True, 'profile': profile_data})
        else:
            return jsonify({'success': False, 'error': 'Profile not found'})
    except Exception as e:
        print(f"❌ API profile error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/posts/<username>')
def api_posts(username):
    """API endpoint for posts data"""
    try:
        posts = instagram_api.get_user_posts(username)
        return jsonify({'success': True, 'posts': posts})
    except Exception as e:
        print(f"❌ API posts error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Debug Routes
@app.route('/debug/profile/<username>')
def debug_profile(username):
    """Debug endpoint to see what's happening with profile fetching"""
    try:
        print(f"🐛 Debug profile: {username}")
        
        # Test all methods
        print("1. Testing public data method...")
        public_data = instagram_api._get_profile_public_data(username)
        
        print("2. Testing GraphQL method...")
        graphql_data = instagram_api._get_profile_graphql(username)
        
        print("3. Testing HTML parsing method...")
        html_data = instagram_api.get_enhanced_private_profile(username)
        
        print("4. Testing main get_profile_data method...")
        main_data = instagram_api.get_profile_data(username)
        
        return jsonify({
            'username': username,
            'public_data': public_data,
            'graphql': graphql_data,
            'html_parsing': html_data,
            'main_method': main_data,
            'success': main_data is not None
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()})

@app.route('/test/instagram')
def test_instagram():
    """Test endpoint for Instagram profile"""
    try:
        profile_data = instagram_api.get_profile_data('instagram')
        return jsonify({
            'success': profile_data is not None,
            'profile': profile_data
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# Serve downloaded files
@app.route('/static/downloads/<filename>')
def serve_downloaded_file(filename):
    """Serve downloaded files"""
    try:
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message="Internal server error"), 500

@app.route('/profile', methods=['POST'])
def profile():
    username = request.form.get('username', '').strip()
    if not username:
        return render_template('error.html', message="Please enter a username.")

    try:
        instagram_api_local = InstagramAPI()
        profile_data = instagram_api_local.get_profile_data(username)

        # ✅ Improved checks
        if not profile_data:
            return render_template('error.html', message=f"Profile '{username}' not found or cannot be accessed.")

        if profile_data.get('is_private', False):
            return render_template('error.html', message=f"'{username}' is a private account. Data cannot be viewed.")

        # ✅ If data is found, show profile
        return render_template('profile.html', profile=profile_data)

    except Exception as e:
        print(f"❌ Exception in profile route: {e}")
        return render_template('error.html', message=f"Error fetching profile: {e}")


@app.route('/api/search/<query>')
def api_search(query):
    """API endpoint for search"""
    try:
        profiles = instagram_api.search_profiles(query)
        return jsonify({
            'success': True,
            'query': query,
            'profiles': profiles,
            'count': len(profiles)
        })
    except Exception as e:
        print(f"❌ API search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Add these new routes to your existing app.py

@app.route('/preview/media/<username>')
def preview_media(username):
    """Preview media for a user (posts, stories, videos)"""
    try:
        profile_data = instagram_api.get_profile_data(username)
        
        if not profile_data:
            return render_template('error.html', message="Profile not found")
        
        # Get all media types
        posts = instagram_api.get_user_posts(username, limit=20)
        stories = instagram_api.get_user_stories(username)
        
        # Separate videos from images
        videos = [post for post in posts if post.get('is_video')]
        images = [post for post in posts if not post.get('is_video')]
        
        return render_template('media_preview.html',
                             profile=profile_data,
                             posts=posts,
                             stories=stories,
                             videos=videos,
                             images=images)
    except Exception as e:
        print(f"❌ Media preview error: {str(e)}")
        return render_template('error.html', message=f"Error loading media preview: {str(e)}")

@app.route('/preview/video/<username>')
def preview_videos(username):
    """Preview only videos"""
    try:
        profile_data = instagram_api.get_profile_data(username)
        
        if not profile_data:
            return render_template('error.html', message="Profile not found")
        
        posts = instagram_api.get_user_posts(username, limit=50)
        videos = [post for post in posts if post.get('is_video')]
        
        return render_template('video_preview.html',
                             profile=profile_data,
                             videos=videos)
    except Exception as e:
        print(f"❌ Video preview error: {str(e)}")
        return render_template('error.html', message=f"Error loading videos: {str(e)}")

@app.route('/preview/stories/<username>')
def preview_stories(username):
    """Preview stories"""
    try:
        profile_data = instagram_api.get_profile_data(username)
        
        if not profile_data:
            return render_template('error.html', message="Profile not found")
        
        stories = instagram_api.get_user_stories(username)
        
        return render_template('stories_preview.html',
                             profile=profile_data,
                             stories=stories)
    except Exception as e:
        print(f"❌ Stories preview error: {str(e)}")
        return render_template('error.html', message=f"Error loading stories: {str(e)}")

@app.route('/api/preview/media/<username>')
def api_media_preview(username):
    """API endpoint for media preview"""
    try:
        profile_data = instagram_api.get_profile_data(username)
        
        if not profile_data:
            return jsonify({'success': False, 'error': 'Profile not found'})
        
        posts = instagram_api.get_user_posts(username, limit=20)
        stories = instagram_api.get_user_stories(username)
        
        # Enhance posts with preview data
        enhanced_posts = []
        for post in posts:
            if post.get('video_url'):
                preview_data = instagram_api.get_media_preview(post['video_url'], 'video')
                post['preview_data'] = preview_data
            elif post.get('display_url'):
                preview_data = instagram_api.get_media_preview(post['display_url'], 'image')
                post['preview_data'] = preview_data
            enhanced_posts.append(post)
        
        return jsonify({
            'success': True,
            'profile': profile_data,
            'posts': enhanced_posts,
            'stories': stories,
            'has_private_content': profile_data.get('is_private', False)
        })
        
    except Exception as e:
        print(f"❌ API media preview error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Create download directory if it doesn't exist
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
    
    print("🚀 Starting IGSpyGlass Server...")
    print("🔧 Debug mode: ON")
    print("🌐 Test the app at: http://localhost:5000")
    print("🔍 Search test: http://localhost:5000/search?q=instagram")
    print("💾 Downloads page: http://localhost:5000/downloads")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
