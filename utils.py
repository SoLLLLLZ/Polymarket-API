"""
Utility functions for parsing Polymarket event and market data.
"""
from typing import Dict, List, Optional


def safe_float(value, default=0.0):
    """
    Safely convert a value to float, handling strings and None.
    
    Args:
        value: Value to convert (can be string, int, float, or None)
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    if value is None or value == '':
        return default
    
    try:
        # Handle string representations of lists or other complex types
        if isinstance(value, str):
            # Remove whitespace
            value = value.strip()
            # If it starts with '[' or '{', it's likely malformed data
            if value.startswith('[') or value.startswith('{'):
                return default
        
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_markets_from_event(event: Dict) -> List[Dict]:
    """
    Extract market information from an event.
    
    Args:
        event: Event dictionary from Gamma API
        
    Returns:
        List of parsed market dictionaries
    """
    import json
    
    markets = event.get("markets", [])
    parsed = []
    
    for market in markets:
        # Ensure outcomes is a list
        outcomes = market.get("outcomes", [])
        if isinstance(outcomes, str):
            try:
                # Try to parse as JSON if it's a string representation
                outcomes = json.loads(outcomes)
            except:
                # If it's a simple string, treat it as a single outcome
                outcomes = [outcomes] if outcomes else []
        elif not isinstance(outcomes, list):
            outcomes = []
        
        # Ensure outcome_prices is a list
        outcome_prices = market.get("outcomePrices", [])
        if isinstance(outcome_prices, str):
            try:
                # Try to parse as JSON
                outcome_prices = json.loads(outcome_prices)
            except:
                outcome_prices = []
        elif not isinstance(outcome_prices, list):
            outcome_prices = []
        
        # Fallback: try other price fields if outcomePrices is empty
        if not outcome_prices:
            # Try 'prices' field
            prices_alt = market.get("prices", [])
            if isinstance(prices_alt, str):
                try:
                    outcome_prices = json.loads(prices_alt)
                except:
                    pass
            elif isinstance(prices_alt, list):
                outcome_prices = prices_alt
            
            # Try individual price fields if still empty
            if not outcome_prices and outcomes:
                # Some markets have individual 'price' or probability fields
                price_val = market.get("price") or market.get("lastPrice")
                if price_val is not None:
                    outcome_prices = [safe_float(price_val, 0)]
        
        # Ensure clobTokenIds is a list
        clob_token_ids = market.get("clobTokenIds", [])
        if isinstance(clob_token_ids, str):
            try:
                # Try to parse as JSON
                clob_token_ids = json.loads(clob_token_ids)
            except:
                clob_token_ids = [clob_token_ids] if clob_token_ids else []
        elif not isinstance(clob_token_ids, list):
            clob_token_ids = []
        
        parsed_market = {
            "question": market.get("question", ""),
            "clob_token_ids": clob_token_ids,
            "outcomes": outcomes,
            "outcome_prices": outcome_prices,
            "volume": market.get("volume", 0),
            "liquidity": market.get("liquidity", 0),
        }
        parsed.append(parsed_market)
    
    return parsed


def get_first_token_id(event: Dict) -> Optional[str]:
    """
    Get the first CLOB token ID from an event (typically 'Yes' outcome).
    
    Args:
        event: Event dictionary
        
    Returns:
        Token ID string or None
    """
    import json
    
    markets = event.get("markets", [])
    if not markets:
        return None
    
    first_market = markets[0]
    token_ids = first_market.get("clobTokenIds", [])
    
    # Handle if token_ids is a string representation of an array
    if isinstance(token_ids, str):
        try:
            token_ids = json.loads(token_ids)
        except:
            return None
    
    return token_ids[0] if token_ids and isinstance(token_ids, list) else None


def get_all_token_ids(event: Dict) -> List[str]:
    """
    Get all CLOB token IDs from an event.
    
    Args:
        event: Event dictionary
        
    Returns:
        List of token ID strings
    """
    import json
    
    markets = event.get("markets", [])
    token_ids = []
    
    for market in markets:
        market_token_ids = market.get("clobTokenIds", [])
        
        # Handle if it's a string representation of an array
        if isinstance(market_token_ids, str):
            try:
                market_token_ids = json.loads(market_token_ids)
            except:
                continue
        
        if isinstance(market_token_ids, list):
            token_ids.extend(market_token_ids)
    
    return token_ids


def format_price(price: float) -> str:
    """
    Format a price (0-1) as a percentage.
    
    Args:
        price: Price value between 0 and 1 (can be string or number)
        
    Returns:
        Formatted percentage string
    """
    price = safe_float(price, 0)
    return f"{price * 100:.1f}%"


def format_volume(volume: float) -> str:
    """
    Format volume with K/M suffix.
    
    Args:
        volume: Volume value (can be string or number)
        
    Returns:
        Formatted volume string
    """
    volume = safe_float(volume, 0)
    if volume >= 1_000_000:
        return f"${volume / 1_000_000:.1f}M"
    elif volume >= 1_000:
        return f"${volume / 1_000:.1f}K"
    else:
        return f"${volume:.0f}"