"""
CLOB API client for Polymarket price history and market data.
"""
import requests
from typing import List, Tuple, Dict, Optional


class CLOBClient:
    """Client for interacting with Polymarket's CLOB API."""
    
    BASE_URL = "https://clob.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
        })
    
    def get_price_history(
        self, 
        token_id: str, 
        interval: str = "1d"
    ) -> List[Tuple[int, float]]:
        """
        Fetch historical prices for a token.
        
        Args:
            token_id: CLOB token ID
            interval: Time interval ('1d', '1w', 'max')
            
        Returns:
            List of (unix_timestamp, price) tuples
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/prices-history",
                params={
                    "market": token_id,
                    "interval": interval
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Convert to list of tuples
            history = data.get("history", [])
            return [(point["t"], point["p"]) for point in history]
        except requests.RequestException as e:
            print(f"Error fetching price history for {token_id}: {e}")
            return []
    
    def get_market_data(self, token_id: str) -> Optional[Dict]:
        """
        Get current market data for a token.
        
        Args:
            token_id: CLOB token ID
            
        Returns:
            Market data dictionary or None
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/markets/{token_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching market data for {token_id}: {e}")
            return None