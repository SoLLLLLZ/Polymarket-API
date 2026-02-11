# Polymarket-API

Polymarket Live Data Platform
A real-time data platform for Polymarket prediction markets built with Streamlit, featuring live price updates, historical charts, and market search.
Features

🔍 Smart Search: Server-side substring search across all Polymarket events
📉 Price Charts: Interactive historical price charts with multiple timeframes
📱 Responsive UI: Clean, modern interface with smooth navigation

Architecture Components

Gamma API Client (gamma_client.py)
Fetches popular events and markets
Server-side search via /public-search endpoint

CLOB API Client (clob_client.py)
Retrieves historical price data
Supports multiple intervals (1d, 1w, max)

Installation

Clone or download the repository

Install dependencies:
pip install -r requirements.txt

Run the application:
streamlit run app.py
