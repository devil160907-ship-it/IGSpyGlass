from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self):
        # No database dependency
        pass
    
    def analyze_profile(self, profile_data, posts):
        """Analyze profile engagement and performance"""
        try:
            total_likes = 0
            total_comments = 0
            video_posts = 0
            image_posts = 0
            
            for post in posts:
                total_likes += post.get('likes', 0)
                total_comments += post.get('comments', 0)
                if post.get('is_video'):
                    video_posts += 1
                else:
                    image_posts += 1
            
            total_posts = len(posts)
            avg_likes = total_likes / total_posts if total_posts > 0 else 0
            avg_comments = total_comments / total_posts if total_posts > 0 else 0
            engagement_rate = ((avg_likes + avg_comments) / profile_data.get('followers', 1)) * 100 if profile_data.get('followers', 0) > 0 else 0
            
            analytics_data = {
                'total_posts_analyzed': total_posts,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'average_likes': round(avg_likes, 2),
                'average_comments': round(avg_comments, 2),
                'engagement_rate': round(engagement_rate, 2),
                'video_posts_count': video_posts,
                'image_posts_count': image_posts,
                'video_percentage': round((video_posts / total_posts) * 100, 2) if total_posts > 0 else 0,
                'last_post_date': posts[0].get('timestamp') if posts else None,
                'followers_count': profile_data.get('followers', 0),
                'following_count': profile_data.get('following', 0)
            }
            
            # No database saving
            return analytics_data
            
        except Exception as e:
            print(f"Error analyzing profile: {e}")
            return {}
    
    def get_profile_analytics(self, username):
        """Get saved analytics for a profile - now returns empty"""
        return {}
