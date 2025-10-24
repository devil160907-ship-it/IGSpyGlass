import requests
import json
import re
from bs4 import BeautifulSoup
import config
from datetime import datetime
import time
import random
import base64
import urllib.parse

class InstagramAPI:
    def __init__(self):
        self.base_url = "https://www.instagram.com"
        self.api_url = "https://www.instagram.com/api/v1"
        self.session = requests.Session()
        
        # PythonAnywhere compatible headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459',
        })
        
        # Get initial cookies by visiting the main page
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session with PythonAnywhere compatibility"""
        try:
            print("🔄 Initializing Instagram session...")
            # Use a longer timeout for PythonAnywhere
            response = self.session.get(self.base_url, timeout=30)
            
            if response.status_code == 200:
                print("✅ Session initialized successfully")
                
                # Extract CSRF token from cookies
                csrf_token = self.session.cookies.get('csrftoken')
                if csrf_token:
                    self.session.headers['X-CSRFToken'] = csrf_token
                    print(f"🔑 CSRF Token: {csrf_token}")
                    
            else:
                print(f"❌ Failed to initialize session: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Session initialization error: {e}")
            # Continue anyway - some features might still work
    
    def _make_request(self, url, method='GET', **kwargs):
        """Safe request method for PythonAnywhere"""
        try:
            # Add longer timeout for PythonAnywhere
            kwargs['timeout'] = kwargs.get('timeout', 30)
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout: {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error: {url}")
            return None
        except Exception as e:
            print(f"❌ Request error {url}: {e}")
            return None

    def _get_common_headers(self):
        """Get common headers required for Instagram API requests"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': self.session.cookies.get('csrftoken', ''),
            'Referer': f'{self.base_url}/',
        }

    def search_profiles(self, query):
        """Search for Instagram profiles with multiple fallback methods"""
        try:
            print(f"🔍 Searching for: {query}")
            
            # Method 1: Try the official search API
            profiles = self._search_official_api(query)
            if profiles:
                return profiles
            
            # Method 2: Try web search as fallback
            profiles = self._search_web_api(query)
            if profiles:
                return profiles
                
            # Method 3: Try basic search as last resort
            profiles = self._search_basic(query)
            if profiles:
                return profiles
                
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        return []

    def _search_official_api(self, query):
        """Search using official Instagram API"""
        try:
            url = f"{self.base_url}/api/v1/web/search/topsearch/"
            params = {
                'context': 'blended',
                'query': query,
                'include_reel': 'true'
            }
            
            headers = {**self._get_common_headers()}
            
            print(f"🌐 Trying official search API: {url}")
            response = self._make_request(url, params=params, headers=headers, timeout=15)
            
            if not response:
                return []
                
            print(f"📊 Official search response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                
                profiles = []
                for user_data in users[:15]:  # Limit to 15 results
                    user = user_data.get('user', {})
                    if user.get('username'):
                        profile = {
                            'username': user.get('username'),
                            'full_name': user.get('full_name', ''),
                            'profile_pic_url': user.get('profile_pic_url', ''),
                            'is_verified': user.get('is_verified', False),
                            'is_private': user.get('is_private', False),
                            'follower_count': user.get('follower_count', 0),
                            'mutual_followers_count': user.get('mutual_followers_count', 0),
                        }
                        profiles.append(profile)
                
                print(f"✅ Official search found {len(profiles)} profiles")
                return profiles
            else:
                print(f"❌ Official search failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Official search error: {e}")
        
        return []

    def _search_web_api(self, query):
        """Search using web API"""
        try:
            url = f"{self.base_url}/web/search/topsearch/"
            params = {
                'context': 'blended',
                'query': query
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            print(f"🌐 Trying web search API: {url}")
            response = self._make_request(url, params=params, headers=headers, timeout=15)
            
            if not response:
                return []
                
            print(f"📊 Web search response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                
                profiles = []
                for user_data in users[:15]:
                    user = user_data.get('user', {})
                    if user.get('username'):
                        profile = {
                            'username': user.get('username'),
                            'full_name': user.get('full_name', ''),
                            'profile_pic_url': user.get('profile_pic_url', ''),
                            'is_verified': user.get('is_verified', False),
                            'is_private': user.get('is_private', False),
                            'follower_count': user.get('follower_count', 0)
                        }
                        profiles.append(profile)
                
                print(f"✅ Web search found {len(profiles)} profiles")
                return profiles
            else:
                print(f"❌ Web search failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Web search error: {e}")
        
        return []

    def _search_basic(self, query):
        """Basic search fallback - try to find profiles by testing common patterns"""
        try:
            print("🔄 Trying basic search fallback...")
            
            # Test if the query itself is a valid username
            test_profile = self.get_profile_data(query)
            if test_profile:
                return [{
                    'username': test_profile['username'],
                    'full_name': test_profile['full_name'],
                    'profile_pic_url': test_profile['profile_pic_url'],
                    'is_verified': test_profile['is_verified'],
                    'is_private': test_profile['is_private'],
                    'follower_count': test_profile.get('followers', 0)
                }]
                
        except Exception as e:
            print(f"❌ Basic search error: {e}")
        
        return []

    def get_profile_data(self, username, force_public=False):
        """Get profile data with enhanced private account support"""
        print(f"🔍 Fetching profile data for: {username}")
        
        # Method 1: Try the public data endpoint
        profile_data = self._get_profile_public_data(username)
        if profile_data:
            print(f"✅ Successfully fetched profile via public data: {profile_data['username']}")
            return profile_data
        
        # Method 2: Try enhanced private profile extraction
        profile_data = self.get_enhanced_private_profile(username)
        if profile_data:
            print(f"✅ Successfully fetched profile via enhanced private method: {username}")
            return profile_data
        
        # Method 3: Try GraphQL as fallback
        profile_data = self._get_profile_graphql(username)
        if profile_data:
            print(f"✅ Successfully fetched profile via GraphQL: {profile_data['username']}")
            return profile_data
        
        print(f"❌ All methods failed for username: {username}")
        return None

    def _get_profile_public_data(self, username):
        """Public data endpoint with better error handling"""
        try:
            url = f"{self.base_url}/api/v1/users/web_profile_info/"
            params = {'username': username}
            headers = self._get_common_headers()
            
            print(f"🌐 Trying public data endpoint: {url}")
            response = self._make_request(url, params=params, headers=headers)
            
            if not response:
                return None
                
            print(f"📊 Public data response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {}).get('user', {})
                
                if user_data and user_data.get('username'):
                    profile = {
                        'username': user_data.get('username'),
                        'full_name': user_data.get('full_name', ''),
                        'bio': user_data.get('biography', ''),
                        'followers': user_data.get('edge_followed_by', {}).get('count', 0),
                        'following': user_data.get('edge_follow', {}).get('count', 0),
                        'posts_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'profile_pic_url': user_data.get('profile_pic_url_hd') or user_data.get('profile_pic_url', ''),
                        'is_private': user_data.get('is_private', False),
                        'is_verified': user_data.get('is_verified', False),
                        'external_url': user_data.get('external_url', ''),
                        'user_id': user_data.get('id', ''),
                        'is_limited_data': False,
                        'has_preview_content': False,
                        'limited_posts': []
                    }
                    print(f"🎯 Public data SUCCESS for: {profile['username']}")
                    return profile
            elif response.status_code == 404:
                print(f"❌ Profile not found: {username}")
            else:
                print(f"⚠️ Public data returned: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Public data error: {e}")
        
        return None

    def get_enhanced_private_profile(self, username):
        """Enhanced method for private profile data extraction"""
        try:
            url = f"{self.base_url}/{username}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            print(f"🔍 Enhanced private profile fetch: {url}")
            response = self._make_request(url, headers=headers, timeout=15)
            
            if not response:
                return None
                
            if response.status_code == 404:
                print(f"❌ Profile not found: {username}")
                return None
                
            if response.status_code != 200:
                print(f"⚠️ Non-200 response: {response.status_code}")
                # Continue anyway to try parsing
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Enhanced private account detection
            is_private = self._detect_private_account(response.text, soup)
            
            # Extract all available data
            profile_data = self._extract_all_available_data(soup, username, response.text)
            profile_data['is_private'] = is_private
            profile_data['is_limited_data'] = is_private
            profile_data['username'] = username
            
            # Enhanced preview content extraction
            if is_private:
                profile_data['limited_posts'] = self._get_enhanced_private_preview(soup, username, response.text)
                profile_data['has_preview_content'] = len(profile_data['limited_posts']) > 0
                
            print(f"✅ Enhanced private data extracted for: {username}")
            return profile_data
            
        except Exception as e:
            print(f"❌ Enhanced private profile error: {e}")
            return None

    def _detect_private_account(self, html, soup):
        """Enhanced private account detection"""
        private_indicators = [
            "This Account is Private",
            "This account is private", 
            "is_private\":true",
            "Account is private",
            "This profile is private",
            "private_profile\":true",
            '"is_private":true'
        ]
        
        # Check HTML content
        if any(indicator in html for indicator in private_indicators):
            return True
            
        # Check meta tags
        meta_description = soup.find('meta', property='og:description')
        if meta_description and 'private' in meta_description.get('content', '').lower():
            return True
            
        # Check for private account messages in text
        text_elements = soup.find_all(text=True)
        private_texts = [text for text in text_elements if 'private' in text.lower() and 'account' in text.lower()]
        if private_texts:
            return True
            
        return False

    def _extract_all_available_data(self, soup, username, html):
        """Extract all possible data from private profile"""
        profile = {
            'username': username,
            'full_name': '',
            'bio': '',
            'profile_pic_url': '',
            'is_verified': False,
            'followers': 0,
            'following': 0,
            'posts_count': 0,
            'external_url': '',
            'user_id': ''
        }
        
        try:
            # Extract from meta tags
            meta_title = soup.find('meta', property='og:title')
            if meta_title and meta_title.get('content'):
                title_content = meta_title['content']
                # Extract name from title (e.g., "Name (@username) • Instagram")
                if '(' in title_content and ')' in title_content:
                    name_part = title_content.split('(')[0].strip()
                    if name_part and name_part != 'Instagram':
                        profile['full_name'] = name_part
            
            # Profile picture from meta
            meta_image = soup.find('meta', property='og:image')
            if meta_image and meta_image.get('content'):
                profile['profile_pic_url'] = meta_image['content']
            else:
                profile['profile_pic_url'] = self._generate_default_avatar(username)
            
            # Bio from meta description
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc and meta_desc.get('content'):
                profile['bio'] = meta_desc['content']
            
            # Try to extract from JSON data in scripts
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    # Look for user data in various JSON structures
                    json_patterns = [
                        r'window\._sharedData\s*=\s*({.*?});',
                        r'{\s*"config".*?"viewer".*?}',
                        r'{"user":{.*?}}'
                    ]
                    
                    for pattern in json_patterns:
                        matches = re.findall(pattern, script_content, re.DOTALL)
                        for match in matches:
                            try:
                                data = json.loads(match)
                                # Try different data structures
                                user_data = (data.get('entry_data', {})
                                            .get('ProfilePage', [{}])[0]
                                            .get('graphql', {})
                                            .get('user'))
                                
                                if user_data:
                                    profile.update({
                                        'full_name': user_data.get('full_name', profile['full_name']),
                                        'bio': user_data.get('biography', profile['bio']),
                                        'profile_pic_url': user_data.get('profile_pic_url_hd') or 
                                                         user_data.get('profile_pic_url', profile['profile_pic_url']),
                                        'is_verified': user_data.get('is_verified', False),
                                        'user_id': user_data.get('id', '')
                                    })
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
            
        except Exception as e:
            print(f"❌ Data extraction error: {e}")
        
        return profile

    def _get_enhanced_private_preview(self, soup, username, html):
        """Get enhanced preview content for private accounts"""
        preview_posts = []
        
        try:
            # Extract from JSON data
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'window._sharedData' in script.string:
                    try:
                        json_text = script.string.split('window._sharedData = ')[1].split(';</script>')[0]
                        data = json.loads(json_text)
                        
                        user_data = (data.get('entry_data', {})
                                    .get('ProfilePage', [{}])[0]
                                    .get('graphql', {})
                                    .get('user', {}))
                        
                        # Get preview posts from user data
                        posts_edges = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
                        
                        for i, post in enumerate(posts_edges[:9]):  # Limit to 9 previews
                            node = post.get('node', {})
                            
                            post_data = {
                                'id': node.get('id', f'preview_{i}'),
                                'type': 'video' if node.get('is_video') else 'image',
                                'preview_url': node.get('display_url') or node.get('thumbnail_src', ''),
                                'display_url': node.get('display_url', ''),
                                'thumbnail_url': node.get('thumbnail_src', ''),
                                'is_video': node.get('is_video', False),
                                'video_url': node.get('video_url', ''),
                                'is_preview': True,
                                'timestamp': datetime.fromtimestamp(node.get('taken_at_timestamp')) if node.get('taken_at_timestamp') else datetime.now(),
                                'caption': 'Preview content from private account',
                                'likes': 0,
                                'comments': 0,
                                'shortcode': node.get('shortcode', f'preview_{i}')
                            }
                            
                            if not post_data['preview_url']:
                                post_data['preview_url'] = self._generate_default_avatar(f"{username}_post_{i}")
                                post_data['thumbnail_url'] = post_data['preview_url']
                            
                            preview_posts.append(post_data)
                        
                        if preview_posts:
                            break
                            
                    except Exception as e:
                        continue
            
            # Fallback: Extract from HTML images
            if not preview_posts:
                img_tags = soup.find_all('img', src=True)
                for i, img in enumerate(img_tags[:9]):
                    src = img.get('src', '')
                    if src and any(pattern in src for pattern in ['/vp/', 'scontent', 'cdninstagram', 'instagram']):
                        post_data = {
                            'id': f'html_preview_{i}',
                            'type': 'image',
                            'preview_url': src,
                            'display_url': src,
                            'thumbnail_url': src,
                            'is_video': False,
                            'is_preview': True,
                            'timestamp': datetime.now(),
                            'caption': 'Preview image from private account',
                            'likes': 0,
                            'comments': 0,
                            'shortcode': f'html_preview_{i}'
                        }
                        preview_posts.append(post_data)
            
        except Exception as e:
            print(f"❌ Enhanced preview extraction error: {e}")
        
        return preview_posts

    def _get_profile_graphql(self, username):
        """Method 3: GraphQL endpoint"""
        try:
            url = f"{self.base_url}/{username}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            print(f"🌐 Trying GraphQL endpoint: {url}")
            response = self._make_request(url, headers=headers, timeout=15)
            
            if not response or response.status_code != 200:
                return None
                
            print(f"📊 GraphQL response status: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tags = soup.find_all('script', type='text/javascript')
            
            for script in script_tags:
                if script.string and 'window._sharedData' in script.string:
                    try:
                        json_text = script.string.split('window._sharedData = ')[1].split(';</script>')[0]
                        data = json.loads(json_text)
                        
                        user_data = data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user')
                        
                        if user_data and user_data.get('username'):
                            profile = {
                                'username': user_data.get('username'),
                                'full_name': user_data.get('full_name', ''),
                                'bio': user_data.get('biography', ''),
                                'followers': user_data.get('edge_followed_by', {}).get('count', 0),
                                'following': user_data.get('edge_follow', {}).get('count', 0),
                                'posts_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                                'profile_pic_url': user_data.get('profile_pic_url_hd') or user_data.get('profile_pic_url', ''),
                                'is_private': user_data.get('is_private', False),
                                'is_verified': user_data.get('is_verified', False),
                                'external_url': user_data.get('external_url', ''),
                                'user_id': user_data.get('id', ''),
                                'is_limited_data': False,
                                'has_preview_content': False,
                                'limited_posts': []
                            }
                            print(f"🎯 GraphQL SUCCESS for: {profile['username']}")
                            return profile
                    except Exception as e:
                        print(f"❌ GraphQL JSON parsing error: {e}")
                        continue
             
        except Exception as e:
            print(f"❌ GraphQL error: {e}")
        
        return None

    def get_limited_profile_data(self, username):
        """Get enhanced limited profile data for private accounts"""
        return self.get_enhanced_private_profile(username)

    def get_user_posts(self, username, limit=12):
        """Get user posts with PythonAnywhere optimizations"""
        try:
            print(f"📷 Fetching posts for: {username}")
            
            # First get profile to check if private
            profile_data = self.get_profile_data(username)
            if not profile_data:
                print(f"❌ Cannot fetch posts: No profile data for {username}")
                return []
            
            if profile_data.get('is_private'):
                print(f"🔒 Private account detected, returning preview posts: {username}")
                return profile_data.get('limited_posts', [])
            
            # Try public data method for posts
            posts = self._get_posts_public_data(username, limit)
            if posts:
                print(f"✅ Successfully fetched {len(posts)} posts for {username}")
                return posts
            
            # Fallback to basic HTML parsing
            posts = self._get_posts_basic_html(username, limit)
            if posts:
                print(f"✅ Successfully fetched {len(posts)} posts via HTML for {username}")
                return posts
                
        except Exception as e:
            print(f"❌ Error fetching posts: {e}")
        
        return []

    def _get_posts_public_data(self, username, limit):
        """Get posts via public data endpoint"""
        try:
            url = f"{self.base_url}/api/v1/users/web_profile_info/"
            params = {'username': username}
            headers = self._get_common_headers()
            
            response = self._make_request(url, params=params, headers=headers, timeout=15)
            
            if not response or response.status_code != 200:
                return []
                
            data = response.json()
            user_data = data.get('data', {}).get('user', {})
            posts_edges = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
            
            formatted_posts = []
            for post in posts_edges[:limit]:
                node = post.get('node', {})
                
                # Get caption
                caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                caption = caption_edges[0].get('node', {}).get('text', '') if caption_edges else ''
                
                post_data = {
                    'id': node.get('id', ''),
                    'shortcode': node.get('shortcode', ''),
                    'thumbnail_url': node.get('thumbnail_src', ''),
                    'display_url': node.get('display_url', ''),
                    'is_video': node.get('is_video', False),
                    'video_url': node.get('video_url', ''),
                    'caption': caption,
                    'likes': node.get('edge_media_preview_like', {}).get('count', 0),
                    'comments': node.get('edge_media_to_comment', {}).get('count', 0),
                    'timestamp': datetime.fromtimestamp(node.get('taken_at_timestamp')) if node.get('taken_at_timestamp') else None,
                    'dimensions': node.get('dimensions', {}),
                    'is_preview': False
                }
                formatted_posts.append(post_data)
            
            print(f"📊 Fetched {len(formatted_posts)} posts via public data")
            return formatted_posts
            
        except Exception as e:
            print(f"❌ Error in public data posts method: {e}")
        
        return []

    def _get_posts_basic_html(self, username, limit):
        """Basic HTML parsing fallback for posts"""
        try:
            url = f"{self.base_url}/{username}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            response = self._make_request(url, headers=headers)
            if not response or response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tags = soup.find_all('script', type='text/javascript')
            
            for script in script_tags:
                if script.string and 'window._sharedData' in script.string:
                    try:
                        json_text = script.string.split('window._sharedData = ')[1].split(';</script>')[0]
                        data = json.loads(json_text)
                        
                        user_data = data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user')
                        posts_edges = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
                        
                        formatted_posts = []
                        for post in posts_edges[:limit]:
                            node = post.get('node', {})
                            
                            # Get caption
                            caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                            caption = caption_edges[0].get('node', {}).get('text', '') if caption_edges else ''
                            
                            post_data = {
                                'id': node.get('id', ''),
                                'shortcode': node.get('shortcode', ''),
                                'thumbnail_url': node.get('thumbnail_src', ''),
                                'display_url': node.get('display_url', ''),
                                'is_video': node.get('is_video', False),
                                'video_url': node.get('video_url', ''),
                                'caption': caption,
                                'likes': node.get('edge_media_preview_like', {}).get('count', 0),
                                'comments': node.get('edge_media_to_comment', {}).get('count', 0),
                                'timestamp': datetime.fromtimestamp(node.get('taken_at_timestamp')) if node.get('taken_at_timestamp') else None,
                                'dimensions': node.get('dimensions', {}),
                                'is_preview': False
                            }
                            formatted_posts.append(post_data)
                        
                        print(f"📊 Fetched {len(formatted_posts)} posts via HTML")
                        return formatted_posts
                        
                    except Exception as e:
                        print(f"❌ HTML posts parsing error: {e}")
                        continue
            
        except Exception as e:
            print(f"❌ Error in HTML posts method: {e}")
        
        return []

    def get_user_stories(self, username):
        """Get user stories - simplified for PythonAnywhere"""
        try:
            profile_data = self.get_profile_data(username)
            if not profile_data:
                return []
            
            if profile_data.get('is_private'):
                print(f"🔒 Private account stories preview for: {username}")
                return self._get_private_stories_preview(username)
            
            # For PythonAnywhere, return empty or basic preview
            # Actual story API might be blocked
            return self._get_basic_stories_preview(username)
            
        except Exception as e:
            print(f"❌ Error fetching stories: {e}")
        
        return []

    def _get_private_stories_preview(self, username):
        """Get limited story preview for private accounts"""
        try:
            # This would typically show that stories exist but can't be accessed
            # For demo purposes, we'll return placeholder data
            return [{
                'id': f'private_story_{username}',
                'type': 'image',
                'preview_url': self._generate_default_avatar(username),
                'display_url': self._generate_default_avatar(username),
                'is_video': False,
                'is_preview': True,
                'timestamp': datetime.now(),
                'duration': 10,
                'caption': 'Stories available but account is private',
                'message': 'This story is from a private account and cannot be viewed without following.'
            }]
        except Exception as e:
            print(f"❌ Private stories preview error: {e}")
            return []

    def _get_basic_stories_preview(self, username):
        """Basic stories preview that works on PythonAnywhere"""
        try:
            # Return placeholder data since story API is often blocked
            return [{
                'id': f'story_preview_{username}',
                'type': 'image',
                'preview_url': self._generate_default_avatar(username),
                'display_url': self._generate_default_avatar(username),
                'is_video': False,
                'is_preview': True,
                'timestamp': datetime.now(),
                'duration': 10,
                'caption': 'Stories preview',
                'message': 'Story functionality may be limited on this hosting platform.'
            }]
        except Exception as e:
            print(f"❌ Basic stories preview error: {e}")
            return []

    def get_media_preview(self, media_url, media_type='post'):
        """Get enhanced preview data for media"""
        try:
            preview_data = {
                'url': media_url,
                'type': media_type,
                'can_preview': True,
                'preview_available': True,
                'is_video': media_type == 'video'
            }
            
            if media_type == 'video':
                preview_data.update({
                    'video_url': media_url,
                    'thumbnail_url': media_url.replace('.mp4', '.jpg') if '.mp4' in media_url else self._generate_default_avatar('video'),
                    'duration': 0,  # Would need actual video analysis
                    'has_audio': True
                })
            elif media_type == 'image':
                preview_data.update({
                    'image_url': media_url,
                    'display_url': media_url,
                    'dimensions': {'width': 1080, 'height': 1080}  # Default
                })
            
            return preview_data
            
        except Exception as e:
            print(f"❌ Media preview error: {e}")
            return None

    def get_profile_insights(self, username):
        """Get basic profile insights (for public accounts)"""
        try:
            profile_data = self.get_profile_data(username)
            if not profile_data or profile_data.get('is_private'):
                return None
            
            posts = self.get_user_posts(username, limit=50)
            
            insights = {
                'engagement_rate': 0,
                'average_likes': 0,
                'average_comments': 0,
                'post_frequency': 'Unknown',
                'most_engaged_post': None
            }
            
            if posts:
                total_likes = sum(post.get('likes', 0) for post in posts)
                total_comments = sum(post.get('comments', 0) for post in posts)
                
                insights['average_likes'] = total_likes // len(posts)
                insights['average_comments'] = total_comments // len(posts)
                
                if profile_data.get('followers', 0) > 0:
                    insights['engagement_rate'] = round(
                        ((total_likes + total_comments) / len(posts)) / profile_data['followers'] * 100, 2
                    )
                
                # Find most engaged post
                if posts:
                    most_engaged = max(posts, key=lambda x: x.get('likes', 0) + x.get('comments', 0))
                    insights['most_engaged_post'] = most_engaged
            
            return insights
            
        except Exception as e:
            print(f"❌ Profile insights error: {e}")
            return None

    def _generate_default_avatar(self, username):
        """Generate a default avatar when profile picture is not available"""
        styles = ['identicon', 'avataaars', 'bottts', 'micah']
        style = random.choice(styles)
        return f"https://api.dicebear.com/7.x/{style}/svg?seed={username}"

class MediaDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def download_media(self, url, filename):
        """Download media from URL with improved error handling"""
        try:
            print(f"📥 Downloading media from: {url}")
            response = self.session.get(url, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"✅ Successfully downloaded: {filename}")
                return True
            else:
                print(f"❌ Download failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error downloading media: {e}")
        
        return False

    def download_profile_picture(self, profile_data, filename=None):
        """Download profile picture"""
        try:
            if not profile_data.get('profile_pic_url'):
                return False
                
            if not filename:
                filename = f"{profile_data['username']}_profile_pic.jpg"
                
            return self.download_media(profile_data['profile_pic_url'], filename)
            
        except Exception as e:
            print(f"❌ Error downloading profile picture: {e}")
            return False
