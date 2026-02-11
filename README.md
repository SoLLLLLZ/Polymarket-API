# Polymarket-API

Polymarket data is accessed through its public REST API using the standard HTTP GET requests. Requests are made using Python’s requests library, with key parameters such as market IDs, tags, or other fields included to filter results. The API returns structured JSON data containing market metadata, prices (implied probabilities), volumes, and timestamps, which are then parsed into Python dictionaries or DataFrames for analysis.

Most endpoints for market data are publicly accessible and do not require authentication. However, if you wanted to actually make trades using the API then you would require an API key and wallet authentication. To obtain an API key, you would create an account on Polymarket and follow their developer documentation to generate credentials, then store the key securely in a gitignore environment and reference it in code without committing it to the repository.

Prompt History:
Used Cursor to generate an implementation plan for the project with techstack, architecture overview, and stages to implement. I then gave that implementation plan to Claude to actually create the project. I had Claude create each stage and I tested it at each stage to verify that it works. 
