from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
import config

class MongoDB:
    def __init__(self):
        self.client = MongoClient(config.Config.MONGO_URI)
        self.db = self.client.igspyglass
    
    # Profile Collections
    def get_profiles_collection(self):
        return self.db.profiles
    
    def get_stories_collection(self):
        return self.db.stories
    
    def get_posts_collection(self):
        return self.db.posts
    
    def get_downloads_collection(self):
        return self.db.downloads
    
    def get_analytics_collection(self):
        return self.db.analytics
    
    def get_users_collection(self):
        return self.db.users

class ProfileManager:
    def __init__(self):
        self.db = MongoDB()
    
    def save_profile(self, profile_data):
        """Save or update profile information"""
        profiles = self.db.get_profiles_collection()
        
        # Add timestamp
        profile_data['last_updated'] = datetime.utcnow()
        profile_data['is_active'] = True
        
        return profiles.update_one(
            {'username': profile_data['username']},
            {'$set': profile_data},
            upsert=True
        )
    
    def get_profile(self, username):
        """Get profile by username"""
        profiles = self.db.get_profiles_collection()
        return profiles.find_one({'username': username})
    
    def search_profiles(self, query, limit=50):
        """Search profiles by username or bio"""
        profiles = self.db.get_profiles_collection()
        return list(profiles.find({
            '$or': [
                {'username': {'$regex': query, '$options': 'i'}},
                {'bio': {'$regex': query, '$options': 'i'}}
            ],
            'is_active': True
        }).limit(limit))

class StoryManager:
    def __init__(self):
        self.db = MongoDB()
    
    def save_stories(self, username, stories):
        """Save stories for a user"""
        stories_collection = self.db.get_stories_collection()
        
        for story in stories:
            story['username'] = username
            story['fetched_at'] = datetime.utcnow()
            story['expires_at'] = datetime.utcnow() + timedelta(hours=24)
            
            stories_collection.update_one(
                {'id': story['id'], 'username': username},
                {'$set': story},
                upsert=True
            )
    
    def get_active_stories(self, username):
        """Get active stories for a user"""
        stories_collection = self.db.get_stories_collection()
        return list(stories_collection.find({
            'username': username,
            'expires_at': {'$gt': datetime.utcnow()}
        }).sort('timestamp', DESCENDING))

class DownloadManager:
    def __init__(self):
        self.db = MongoDB()
    
    def log_download(self, download_data):
        """Log download activity"""
        downloads = self.db.get_downloads_collection()
        
        download_data['downloaded_at'] = datetime.utcnow()
        download_data['status'] = 'completed'
        
        return downloads.insert_one(download_data)
    
    def get_download_history(self, limit=100):
        """Get download history"""
        downloads = self.db.get_downloads_collection()
        return list(downloads.find().sort('downloaded_at', DESCENDING).limit(limit))
    
    def get_download_stats(self):
        """Get download statistics"""
        downloads = self.db.get_downloads_collection()
        
        total_downloads = downloads.count_documents({})
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_downloads = downloads.count_documents({'downloaded_at': {'$gte': today}})
        
        return {
            'total_downloads': total_downloads,
            'today_downloads': today_downloads
        }

class AnalyticsManager:
    def __init__(self):
        self.db = MongoDB()
    
    def save_analytics(self, username, analytics_data):
        """Save analytics data for a profile"""
        analytics = self.db.get_analytics_collection()
        
        analytics_data['username'] = username
        analytics_data['analyzed_at'] = datetime.utcnow()
        
        return analytics.update_one(
            {'username': username},
            {'$set': analytics_data},
            upsert=True
        )
    
    def get_profile_analytics(self, username):
        """Get analytics for a profile"""
        analytics = self.db.get_analytics_collection()
        return analytics.find_one({'username': username})