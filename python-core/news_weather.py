"""
News & Weather Module - Stage 5 Phase 3
Provides real-time weather information and news aggregation with offline caching
"""

import os
import time
import json
import requests
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from stage5_base import BaseAnalyzer
from stage5_utils import Logger, ConfigLoader


class NewsWeatherManager(BaseAnalyzer):
    """Real-time information retrieval with weather and news aggregation"""
    
    def __init__(self, mongodb=None, enable_cache: bool = True):
        """Initialize news & weather manager.
        
        Args:
            mongodb: MongoDB connection for caching
            enable_cache: Whether to enable caching
        """
        super().__init__("NewsWeatherManager", mongodb, enable_cache)
        
        # Load API keys from config
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        
        # API endpoints
        self.weather_base_url = "https://api.openweathermap.org/data/2.5"
        self.news_base_url = "https://newsapi.org/v2"
        
        # Request timeout
        self.timeout = 10  # seconds
        
        # Offline fallback data
        self.offline_mode = False
        
        Logger.info(self.name, "Ready for weather and news retrieval")
        
        if not self.weather_api_key:
            Logger.warning(self.name, "No OpenWeather API key found - using mock data")
        if not self.news_api_key:
            Logger.warning(self.name, "No News API key found - using mock data")
    
    def analyze(self, input_data: Any) -> Dict[str, Any]:
        """Generic analysis - redirects to weather or news based on type.
        
        Args:
            input_data: Dict with 'type' ('weather' or 'news') and parameters
            
        Returns:
            Weather or news data
        """
        if not isinstance(input_data, dict):
            return self.format_error("Input must be a dictionary", "INVALID_INPUT")
        
        data_type = input_data.get('type', 'weather')
        
        if data_type == 'weather':
            location = input_data.get('location', 'London')
            return self.get_weather(location)
        elif data_type == 'news':
            query = input_data.get('query', '')
            category = input_data.get('category', 'general')
            country = input_data.get('country', 'us')
            page_size = input_data.get('page_size', 10)
            return self.get_news(query, category, country, page_size)
        else:
            return self.format_error(f"Unknown type: {data_type}", "UNKNOWN_TYPE")
    
    def get_weather(self, location: str, units: str = 'metric') -> Dict[str, Any]:
        """Get current weather for a location.
        
        Args:
            location: City name or coordinates (e.g., "London" or "London,UK")
            units: Temperature units ('metric', 'imperial', 'standard')
            
        Returns:
            Current weather data with temperature, conditions, etc.
        """
        start_time = time.time()
        
        if not location or not location.strip():
            return self.format_error("Location cannot be empty", "EMPTY_LOCATION")
        
        # Check cache first
        cache_key = self.get_cache_key(action='weather', location=location, units=units)
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, f"Returning cached weather for {location}")
            return cached
        
        # Try to fetch from API
        weather_data = None
        
        if self.weather_api_key:
            try:
                url = f"{self.weather_base_url}/weather"
                params = {
                    'q': location,
                    'appid': self.weather_api_key,
                    'units': units
                }
                
                response = requests.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    api_data = response.json()
                    weather_data = self._format_weather_data(api_data, units)
                    Logger.info(self.name, f"Weather fetched for {location}")
                elif response.status_code == 404:
                    return self.format_error(f"Location not found: {location}", "LOCATION_NOT_FOUND")
                else:
                    Logger.error(self.name, f"Weather API error: {response.status_code}")
                    weather_data = self._get_mock_weather(location, units)
                    
            except requests.exceptions.Timeout:
                Logger.error(self.name, "Weather API timeout")
                weather_data = self._get_mock_weather(location, units)
            except Exception as e:
                Logger.error(self.name, f"Weather API error: {e}")
                weather_data = self._get_mock_weather(location, units)
        else:
            # No API key - use mock data
            weather_data = self._get_mock_weather(location, units)
        
        duration_ms = (time.time() - start_time) * 1000
        self.log_analysis(f"Weather for {location}", "Success", duration_ms)
        
        # Cache result for 30 minutes (weather changes slowly)
        result = self.format_success(weather_data, f"Weather data for {location}")
        self.cache_result(cache_key, result, ttl_minutes=30)
        
        return result
    
    def get_weather_forecast(self, location: str, days: int = 5, units: str = 'metric') -> Dict[str, Any]:
        """Get weather forecast for multiple days.
        
        Args:
            location: City name or coordinates
            days: Number of days (1-5)
            units: Temperature units ('metric', 'imperial', 'standard')
            
        Returns:
            Multi-day weather forecast
        """
        start_time = time.time()
        
        if not location or not location.strip():
            return self.format_error("Location cannot be empty", "EMPTY_LOCATION")
        
        if days < 1 or days > 5:
            return self.format_error("Days must be between 1 and 5", "INVALID_DAYS")
        
        # Check cache
        cache_key = self.get_cache_key(action='forecast', location=location, days=days, units=units)
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, f"Returning cached forecast for {location}")
            return cached
        
        # Try to fetch from API
        forecast_data = None
        
        if self.weather_api_key:
            try:
                url = f"{self.weather_base_url}/forecast"
                params = {
                    'q': location,
                    'appid': self.weather_api_key,
                    'units': units,
                    'cnt': days * 8  # API returns 3-hour intervals (8 per day)
                }
                
                response = requests.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    api_data = response.json()
                    forecast_data = self._format_forecast_data(api_data, days, units)
                    Logger.info(self.name, f"Forecast fetched for {location} ({days} days)")
                elif response.status_code == 404:
                    return self.format_error(f"Location not found: {location}", "LOCATION_NOT_FOUND")
                else:
                    Logger.error(self.name, f"Forecast API error: {response.status_code}")
                    forecast_data = self._get_mock_forecast(location, days, units)
                    
            except Exception as e:
                Logger.error(self.name, f"Forecast API error: {e}")
                forecast_data = self._get_mock_forecast(location, days, units)
        else:
            # No API key - use mock data
            forecast_data = self._get_mock_forecast(location, days, units)
        
        duration_ms = (time.time() - start_time) * 1000
        self.log_analysis(f"Forecast for {location}", f"{days} days", duration_ms)
        
        # Cache forecast for 2 hours
        result = self.format_success(forecast_data, f"{days}-day forecast for {location}")
        self.cache_result(cache_key, result, ttl_minutes=120)
        
        return result
    
    def get_news(self, query: str = '', category: str = 'general', 
                 country: str = 'us', page_size: int = 10) -> Dict[str, Any]:
        """Get news headlines.
        
        Args:
            query: Search query (optional)
            category: News category (business, entertainment, general, health, science, sports, technology)
            country: Country code (us, gb, ca, au, etc.)
            page_size: Number of articles (1-100)
            
        Returns:
            News articles with title, description, source, url
        """
        start_time = time.time()
        
        if page_size < 1 or page_size > 100:
            return self.format_error("Page size must be between 1 and 100", "INVALID_PAGE_SIZE")
        
        valid_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
        if category not in valid_categories:
            return self.format_error(
                f"Invalid category. Valid: {', '.join(valid_categories)}", 
                "INVALID_CATEGORY"
            )
        
        # Check cache
        cache_key = self.get_cache_key(
            action='news', query=query, category=category, 
            country=country, page_size=page_size
        )
        cached = self.get_cached_result(cache_key)
        if cached:
            Logger.debug(self.name, "Returning cached news")
            return cached
        
        # Try to fetch from API
        news_data = None
        
        if self.news_api_key:
            try:
                # Use different endpoint based on query
                if query:
                    url = f"{self.news_base_url}/everything"
                    params = {
                        'q': query,
                        'apiKey': self.news_api_key,
                        'pageSize': page_size,
                        'language': 'en',
                        'sortBy': 'publishedAt'
                    }
                else:
                    url = f"{self.news_base_url}/top-headlines"
                    params = {
                        'category': category,
                        'country': country,
                        'apiKey': self.news_api_key,
                        'pageSize': page_size
                    }
                
                response = requests.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    api_data = response.json()
                    news_data = self._format_news_data(api_data)
                    Logger.info(self.name, f"News fetched: {len(news_data.get('articles', []))} articles")
                else:
                    Logger.error(self.name, f"News API error: {response.status_code}")
                    news_data = self._get_mock_news(query, category, page_size)
                    
            except Exception as e:
                Logger.error(self.name, f"News API error: {e}")
                news_data = self._get_mock_news(query, category, page_size)
        else:
            # No API key - use mock data
            news_data = self._get_mock_news(query, category, page_size)
        
        duration_ms = (time.time() - start_time) * 1000
        self.log_analysis(f"News {category}", f"{len(news_data.get('articles', []))} articles", duration_ms)
        
        # Cache news for 15 minutes
        result = self.format_success(news_data, "News retrieved successfully")
        self.cache_result(cache_key, result, ttl_minutes=15)
        
        return result
    
    def get_cached_news(self, max_age_minutes: int = 60) -> Dict[str, Any]:
        """Get all cached news articles that are recent.
        
        Args:
            max_age_minutes: Maximum age of cached articles to return
            
        Returns:
            All recent cached news articles
        """
        if not self.mongodb:
            return self.format_error("MongoDB not available for cache retrieval", "NO_DATABASE")
        
        try:
            db = self.mongodb.db
            cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
            
            # Find all recent news cache entries
            cached_entries = db.cache.find({
                'key': {'$regex': '"action":"news"'},
                'expires': {'$gt': datetime.now()},
                'created_at': {'$gt': cutoff_time}
            }).sort('created_at', -1).limit(10)
            
            all_articles = []
            sources = set()
            
            for entry in cached_entries:
                if 'value' in entry and 'data' in entry['value']:
                    data = entry['value']['data']
                    if 'articles' in data:
                        all_articles.extend(data['articles'])
                        if 'sources' in data:
                            sources.update(data.get('sources', []))
            
            # Remove duplicates based on title
            unique_articles = []
            seen_titles = set()
            for article in all_articles:
                title = article.get('title', '')
                if title and title not in seen_titles:
                    unique_articles.append(article)
                    seen_titles.add(title)
            
            result_data = {
                'articles': unique_articles[:50],  # Limit to 50 most recent
                'total': len(unique_articles),
                'sources': list(sources),
                'cached': True,
                'timestamp': datetime.now().isoformat()
            }
            
            Logger.info(self.name, f"Retrieved {len(unique_articles)} cached news articles")
            return self.format_success(result_data, "Cached news retrieved")
            
        except Exception as e:
            Logger.error(self.name, f"Failed to retrieve cached news: {e}")
            return self.format_error(f"Cache retrieval failed: {str(e)}", "CACHE_ERROR")
    
    # Private helper methods
    
    def _format_weather_data(self, api_data: Dict, units: str) -> Dict[str, Any]:
        """Format weather API response into consistent structure."""
        temp_unit = '°C' if units == 'metric' else ('°F' if units == 'imperial' else 'K')
        
        return {
            'location': {
                'name': api_data.get('name', 'Unknown'),
                'country': api_data.get('sys', {}).get('country', ''),
                'coordinates': {
                    'lat': api_data.get('coord', {}).get('lat'),
                    'lon': api_data.get('coord', {}).get('lon')
                }
            },
            'current': {
                'temperature': api_data.get('main', {}).get('temp'),
                'feels_like': api_data.get('main', {}).get('feels_like'),
                'temp_min': api_data.get('main', {}).get('temp_min'),
                'temp_max': api_data.get('main', {}).get('temp_max'),
                'unit': temp_unit,
                'humidity': api_data.get('main', {}).get('humidity'),
                'pressure': api_data.get('main', {}).get('pressure'),
                'description': api_data.get('weather', [{}])[0].get('description', ''),
                'icon': api_data.get('weather', [{}])[0].get('icon', ''),
                'wind_speed': api_data.get('wind', {}).get('speed'),
                'clouds': api_data.get('clouds', {}).get('all')
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'openweathermap'
        }
    
    def _format_forecast_data(self, api_data: Dict, days: int, units: str) -> Dict[str, Any]:
        """Format forecast API response into consistent structure."""
        temp_unit = '°C' if units == 'metric' else ('°F' if units == 'imperial' else 'K')
        
        forecasts = []
        list_data = api_data.get('list', [])
        
        # Group by day and get one forecast per day
        current_day = None
        for item in list_data:
            dt = datetime.fromtimestamp(item.get('dt', 0))
            day = dt.date()
            
            if day != current_day:
                current_day = day
                forecasts.append({
                    'date': day.isoformat(),
                    'day_name': dt.strftime('%A'),
                    'temperature': {
                        'avg': item.get('main', {}).get('temp'),
                        'min': item.get('main', {}).get('temp_min'),
                        'max': item.get('main', {}).get('temp_max'),
                        'unit': temp_unit
                    },
                    'description': item.get('weather', [{}])[0].get('description', ''),
                    'icon': item.get('weather', [{}])[0].get('icon', ''),
                    'humidity': item.get('main', {}).get('humidity'),
                    'wind_speed': item.get('wind', {}).get('speed'),
                    'clouds': item.get('clouds', {}).get('all')
                })
            
            if len(forecasts) >= days:
                break
        
        return {
            'location': {
                'name': api_data.get('city', {}).get('name', 'Unknown'),
                'country': api_data.get('city', {}).get('country', ''),
                'coordinates': {
                    'lat': api_data.get('city', {}).get('coord', {}).get('lat'),
                    'lon': api_data.get('city', {}).get('coord', {}).get('lon')
                }
            },
            'forecast': forecasts,
            'days': len(forecasts),
            'timestamp': datetime.now().isoformat(),
            'source': 'openweathermap'
        }
    
    def _format_news_data(self, api_data: Dict) -> Dict[str, Any]:
        """Format news API response into consistent structure."""
        articles = []
        sources = set()
        
        for article in api_data.get('articles', []):
            source_name = article.get('source', {}).get('name', 'Unknown')
            sources.add(source_name)
            
            articles.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'content': article.get('content', ''),
                'author': article.get('author', 'Unknown'),
                'source': source_name,
                'url': article.get('url', ''),
                'image_url': article.get('urlToImage', ''),
                'published_at': article.get('publishedAt', '')
            })
        
        return {
            'articles': articles,
            'total': api_data.get('totalResults', len(articles)),
            'sources': list(sources),
            'timestamp': datetime.now().isoformat(),
            'source': 'newsapi'
        }
    
    def _get_mock_weather(self, location: str, units: str) -> Dict[str, Any]:
        """Generate mock weather data when API is unavailable."""
        temp_unit = '°C' if units == 'metric' else ('°F' if units == 'imperial' else 'K')
        base_temp = 20 if units == 'metric' else 68
        
        return {
            'location': {
                'name': location,
                'country': 'XX',
                'coordinates': {'lat': 0.0, 'lon': 0.0}
            },
            'current': {
                'temperature': base_temp,
                'feels_like': base_temp - 2,
                'temp_min': base_temp - 3,
                'temp_max': base_temp + 3,
                'unit': temp_unit,
                'humidity': 65,
                'pressure': 1013,
                'description': 'partly cloudy',
                'icon': '02d',
                'wind_speed': 5.0,
                'clouds': 40
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data',
            'offline': True
        }
    
    def _get_mock_forecast(self, location: str, days: int, units: str) -> Dict[str, Any]:
        """Generate mock forecast data when API is unavailable."""
        temp_unit = '°C' if units == 'metric' else ('°F' if units == 'imperial' else 'K')
        base_temp = 20 if units == 'metric' else 68
        
        forecasts = []
        for i in range(days):
            day = datetime.now() + timedelta(days=i)
            forecasts.append({
                'date': day.date().isoformat(),
                'day_name': day.strftime('%A'),
                'temperature': {
                    'avg': base_temp + i,
                    'min': base_temp + i - 3,
                    'max': base_temp + i + 3,
                    'unit': temp_unit
                },
                'description': ['sunny', 'partly cloudy', 'cloudy', 'rainy'][i % 4],
                'icon': ['01d', '02d', '03d', '10d'][i % 4],
                'humidity': 65 + (i * 5),
                'wind_speed': 5.0 + i,
                'clouds': 20 + (i * 10)
            })
        
        return {
            'location': {
                'name': location,
                'country': 'XX',
                'coordinates': {'lat': 0.0, 'lon': 0.0}
            },
            'forecast': forecasts,
            'days': days,
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data',
            'offline': True
        }
    
    def _get_mock_news(self, query: str, category: str, page_size: int) -> Dict[str, Any]:
        """Generate mock news data when API is unavailable."""
        mock_articles = [
            {
                'title': f'Sample {category.title()} News Article 1',
                'description': f'This is a sample article about {category}. API key required for real news.',
                'content': 'Full content would appear here with real API.',
                'author': 'Sample Author',
                'source': 'Mock News Network',
                'url': 'https://example.com/news1',
                'image_url': '',
                'published_at': datetime.now().isoformat()
            },
            {
                'title': f'Breaking: Latest {category.title()} Update',
                'description': f'Important developments in {category}. Configure NEWS_API_KEY for real data.',
                'content': 'Full content would appear here with real API.',
                'author': 'News Bot',
                'source': 'Sample Times',
                'url': 'https://example.com/news2',
                'image_url': '',
                'published_at': (datetime.now() - timedelta(hours=1)).isoformat()
            },
            {
                'title': f'{category.title()} Analysis: Expert Insights',
                'description': f'Expert analysis on current {category} trends.',
                'content': 'Full content would appear here with real API.',
                'author': 'Expert Panel',
                'source': 'Mock Gazette',
                'url': 'https://example.com/news3',
                'image_url': '',
                'published_at': (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
        
        # Filter by page_size
        articles = mock_articles[:min(page_size, len(mock_articles))]
        
        return {
            'articles': articles,
            'total': len(articles),
            'sources': ['Mock News Network', 'Sample Times', 'Mock Gazette'],
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data',
            'offline': True
        }
