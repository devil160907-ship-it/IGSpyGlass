import os
import uuid
from datetime import datetime
from models.models import DownloadManager
from utils.instagram_api import MediaDownloader
import config

class DownloadService:
    def __init__(self):
        self.download_manager = DownloadManager()
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