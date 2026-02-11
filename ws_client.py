"""
WebSocket client for Polymarket live market data.
"""
import json
import threading
import time
from typing import Dict, List, Optional
from websocket import WebSocketApp


class WSClient:
    """WebSocket client for live market data from CLOB."""
    
    WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    
    def __init__(self):
        self.ws = None
        self.thread = None
        self.running = False
        self.live_prices = {}  # {asset_id: {best_bid, best_ask, last_trade_price}}
        self.lock = threading.Lock()
        self.subscribed_assets = set()
        self.last_ping = 0
    
    def connect(self, asset_ids: List[str]):
        """
        Connect to WebSocket and subscribe to asset IDs.
        
        Args:
            asset_ids: List of CLOB token IDs to subscribe to
        """
        if self.running:
            # Already connected, just add new subscriptions
            self._subscribe(asset_ids)
            return
        
        self.running = True
        self.subscribed_assets.update(asset_ids)
        
        def on_open(ws):
            print(f"WebSocket connected, subscribing to {len(asset_ids)} assets")
            self._send_subscribe(ws, asset_ids)
        
        def on_message(ws, message):
            try:
                # Skip empty messages
                if not message or not message.strip():
                    return
                    
                data = json.loads(message)
                self._process_message(data)
            except json.JSONDecodeError as e:
                # Skip logging for common empty/ping messages
                if message.strip():
                    print(f"Error parsing WebSocket message: {e}")
            except Exception as e:
                print(f"Error processing WebSocket message: {e}")
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"WebSocket closed: {close_status_code} - {close_msg}")
            self.running = False
        
        self.ws = WebSocketApp(
            self.WS_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Run in background thread
        self.thread = threading.Thread(target=self._run_forever, daemon=True)
        self.thread.start()
    
    def _run_forever(self):
        """Run WebSocket connection in loop with ping."""
        while self.running:
            try:
                self.ws.run_forever(ping_interval=10, ping_timeout=5)
            except Exception as e:
                print(f"WebSocket run error: {e}")
            
            if self.running:
                print("WebSocket disconnected, reconnecting in 5s...")
                time.sleep(5)
    
    def _send_subscribe(self, ws, asset_ids: List[str]):
        """Send subscription message."""
        subscribe_msg = {
            "assets_ids": asset_ids,
            "type": "market"
        }
        ws.send(json.dumps(subscribe_msg))
    
    def _subscribe(self, asset_ids: List[str]):
        """Subscribe to additional assets on existing connection."""
        new_assets = [aid for aid in asset_ids if aid not in self.subscribed_assets]
        if new_assets and self.ws:
            self.subscribed_assets.update(new_assets)
            self._send_subscribe(self.ws, new_assets)
    
    def _process_message(self, data: Dict):
        """Process incoming WebSocket message."""
        # Skip if data is not a dict
        if not isinstance(data, dict):
            return
            
        msg_type = data.get("event_type") or data.get("type")
        
        if msg_type == "book":
            # Full book snapshot
            asset_id = data.get("asset_id")
            if asset_id:
                with self.lock:
                    if asset_id not in self.live_prices:
                        self.live_prices[asset_id] = {}
                    
                    # Extract best bid/ask from book
                    bids = data.get("bids", [])
                    asks = data.get("asks", [])
                    
                    if bids and isinstance(bids, list) and len(bids) > 0:
                        bid = bids[0]
                        if isinstance(bid, dict):
                            self.live_prices[asset_id]["best_bid"] = float(bid.get("price", 0))
                        elif isinstance(bid, list) and len(bid) >= 2:
                            # Sometimes bids are [price, size] arrays
                            self.live_prices[asset_id]["best_bid"] = float(bid[0])
                    
                    if asks and isinstance(asks, list) and len(asks) > 0:
                        ask = asks[0]
                        if isinstance(ask, dict):
                            self.live_prices[asset_id]["best_ask"] = float(ask.get("price", 0))
                        elif isinstance(ask, list) and len(ask) >= 2:
                            # Sometimes asks are [price, size] arrays
                            self.live_prices[asset_id]["best_ask"] = float(ask[0])
        
        elif msg_type == "price_change":
            # Price change update
            asset_id = data.get("asset_id")
            if asset_id:
                with self.lock:
                    if asset_id not in self.live_prices:
                        self.live_prices[asset_id] = {}
                    
                    if "best_bid" in data:
                        self.live_prices[asset_id]["best_bid"] = float(data["best_bid"])
                    if "best_ask" in data:
                        self.live_prices[asset_id]["best_ask"] = float(data["best_ask"])
        
        elif msg_type == "last_trade_price":
            # Last trade price
            asset_id = data.get("asset_id")
            if asset_id:
                with self.lock:
                    if asset_id not in self.live_prices:
                        self.live_prices[asset_id] = {}
                    
                    if "price" in data:
                        self.live_prices[asset_id]["last_trade_price"] = float(data["price"])
    
    def get_live_prices(self, asset_id: str) -> Optional[Dict]:
        """
        Get current live prices for an asset.
        
        Args:
            asset_id: CLOB token ID
            
        Returns:
            Dictionary with best_bid, best_ask, last_trade_price (if available)
        """
        with self.lock:
            return self.live_prices.get(asset_id, {}).copy()
    
    def get_all_live_prices(self) -> Dict[str, Dict]:
        """Get all live prices."""
        with self.lock:
            return {k: v.copy() for k, v in self.live_prices.items()}
    
    def disconnect(self):
        """Disconnect from WebSocket."""
        self.running = False
        if self.ws:
            self.ws.close()