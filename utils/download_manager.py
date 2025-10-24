import os
import uuid
import sqlite3
import json
from datetime import datetime
from utils.instagram_api import MediaDownloader
import config

class SQLiteDownloadManager:
    def __init__(self, db_path='downloads.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    username TEXT,
                    media_id TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    media_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            print("✅ SQLite download database initialized")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def log_download(self, download_data):
        """Log download to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO downloads 
                (type, username, media_id, file_path, file_size, media_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                download_data.get('type'),
                download_data.get('username'),
                download_data.get('post_id') or download_data.get('story_id') or download_data.get('username'),
                download_data.get('file_path'),
                download_data.get('file_size', 0),
                download_data.get('media_url'),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Download logging error: {e}")
            return False
    
    def get_download_stats(self):
        """Get download statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_downloads,
                    COUNT(DISTINCT username) as unique_users,
                    SUM(file_size) as total_size
                FROM downloads
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'total_downloads': result[0] or 0,
                    'unique_users': result[1] or 0,
                    'total_size': result[2] or 0
                }
        except Exception as e:
            print(f"❌ Download stats error: {e}")
        
        return {
            'total_downloads': 0,
            'unique_users': 0,
            'total_size': 0
        }
    
    def get_download_history(self, limit=50):
        """Get download history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    type, username, media_id, file_path, file_size, media_url, created_at
                FROM downloads 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            downloads = []
            for row in cursor.fetchall():
                downloads.append({
                    'type': row[0],
                    'username': row[1],
                    'media_id': row[2],
                    'file_path': row[3],
                    'file_size': row[4],
                    'media_url': row[5],
                    'created_at': row[6]
                })
            
            conn.close()
            return downloads
        except Exception as e:
            print(f"❌ Download history error: {e}")
        
        return []

class DownloadService:
    def __init__(self):
        self.download_manager = SQLiteDownloadManager()
        self.media_downloader = MediaDownloader()
        self.download_folder = config.Config.DOWNLOAD_FOLDER
        
        # Create download folder if it doesn't exist
        os.makedirs(self.download_folder, exist_ok=True)
    
    def download_story(self, story_url, username, story_id):
        """Download a single story"""
        try:
            # Generate unique filename
            file_extension = '.mp4' if 'video' in story_url else '.jpg'
            filename = f"{username}_{story_id}_{uuid.uuid4().hex}{file_extension}"
            filepath = os.path.join(self.download_folder, filename)
            
            # Download media
            success = self.media_downloader.download_media(story_url, filepath)
            
            if success:
                # Log download
                download_data = {
                    'type': 'story',
                    'username': username,
                    'story_id': story_id,
                    'file_path': filepath,
                    'file_size': os.path.getsize(filepath),
                    'media_url': story_url
                }
                self.download_manager.log_download(download_data)
                
                return {
                    'success': True,
                    'filepath': filepath,
                    'filename': filename
                }
        
        except Exception as e:
            print(f"Error downloading story: {e}")
        
        return {'success': False}
    
    def download_post(self, post_data, username):
        """Download a post"""
        try:
            media_url = post_data.get('video_url') or post_data.get('display_url')
            if not media_url:
                return {'success': False}
            
            # Generate unique filename
            file_extension = '.mp4' if post_data.get('is_video') else '.jpg'
            filename = f"{username}_post_{post_data['id']}_{uuid.uuid4().hex}{file_extension}"
            filepath = os.path.join(self.download_folder, filename)
            
            # Download media
            success = self.media_downloader.download_media(media_url, filepath)
            
            if success:
                # Log download
                download_data = {
                    'type': 'post',
                    'username': username,
                    'post_id': post_data['id'],
                    'file_path': filepath,
                    'file_size': os.path.getsize(filepath),
                    'media_url': media_url
                }
                self.download_manager.log_download(download_data)
                
                return {
                    'success': True,
                    'filepath': filepath,
                    'filename': filename
                }
        
        except Exception as e:
            print(f"Error downloading post: {e}")
        
        return {'success': False}
    
    def download_profile_picture(self, profile_data):
        """Download profile picture"""
        try:
            profile_pic_url = profile_data.get('profile_pic_url')
            if not profile_pic_url:
                return {'success': False}
            
            username = profile_data['username']
            filename = f"{username}_profile_pic_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(self.download_folder, filename)
            
            # Download media
            success = self.media_downloader.download_media(profile_pic_url, filepath)
            
            if success:
                # Log download
                download_data = {
                    'type': 'profile_pic',
                    'username': username,
                    'file_path': filepath,
                    'file_size': os.path.getsize(filepath),
                    'media_url': profile_pic_url
                }
                self.download_manager.log_download(download_data)
                
                return {
                    'success': True,
                    'filepath': filepath,
                    'filename': filename
                }
        
        except Exception as e:
            print(f"Error downloading profile picture: {e}")
        
        return {'success': False}

    def get_download_stats(self):
        """Get download statistics"""
        return self.download_manager.get_download_stats()
    
    def get_download_history(self, limit=50):
        """Get download history"""
        return self.download_manager.get_download_history(limit)
