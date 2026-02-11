"""
Gamma API client for Polymarket events and markets.
"""
import requests
from typing import List, Dict, Optional


class GammaClient:
    """Client for interacting with Polymarket's Gamma API."""
    
    BASE_URL = "https://gamma-api.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
        })
    
    def get_popular_events(self, limit: int = 20) -> List[Dict]:
        """
        Fetch popular/featured events that are currently open.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            # Use the events endpoint with proper filters for open markets
            response = self.session.get(
                f"{self.BASE_URL}/events",
                params={
                    "limit": limit,
                    "closed": "false",  # Only open markets
                    "order": "volume24hr",  # Order by recent volume
                    "ascending": "false"  # Descending order (highest first)
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching popular events: {e}")
            return []
    
    def get_featured_events(self, limit: int = 20) -> List[Dict]:
        """
        Fetch featured/trending events (alternative to popular).
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            # Try getting from a different endpoint or tag
            response = self.session.get(
                f"{self.BASE_URL}/events",
                params={
                    "limit": limit,
                    "archived": "false",
                    "closed": "false"
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching featured events: {e}")
            return []
    
    def search_events_public(self, query: str, limit_per_type: int = 20) -> List[Dict]:
        """
        Search events using Gamma's public-search endpoint (server-side substring search).
        
        Args:
            query: Search query string
            limit_per_type: Maximum results per type
            
        Returns:
            List of matching events
        """
        if not query or not query.strip():
            return []
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/public-search",
                params={
                    "q": query.strip(),
                    "limit_per_type": limit_per_type,
                    "events_status": "open",
                    "search_profiles": "false"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("events", [])
        except requests.RequestException as e:
            print(f"Error searching events: {e}")
            return []
    
    def get_event(self, event_slug: str) -> Optional[Dict]:
        """
        Get a specific event by slug.
        
        Args:
            event_slug: Event identifier
            
        Returns:
            Event dictionary or None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/events/{event_slug}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching event {event_slug}: {e}")
            return None