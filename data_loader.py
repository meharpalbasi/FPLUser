# data_loader.py

import requests
import pandas as pd
from datetime import datetime

def fetch_players():
    """
    Fetches player data from the FPL API and returns a mapping of player IDs to player names.
    
    Returns:
        dict: A dictionary mapping player IDs to their web names.
    """
    players_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    try:
        response = requests.get(players_url)
        response.raise_for_status()
        players_data = response.json()
        players = players_data['elements']
        player_id_to_name = {player['id']: player['web_name'] for player in players}
        return player_id_to_name
    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f'HTTP error occurred while fetching players: {http_err}') from http_err
    except Exception as err:
        raise RuntimeError(f'Other error occurred while fetching players: {err}') from err

def fetch_transfers(TID):
    """
    Fetches transfer data for a given Team ID from the FPL API and returns it as a DataFrame.
    
    Args:
        TID (str): The Team ID.
    
    Returns:
        pd.DataFrame: DataFrame containing transfer history.
    """
    transfers_url = f'https://fantasy.premierleague.com/api/entry/{TID}/transfers/'
    try:
        response = requests.get(transfers_url)
        response.raise_for_status()
        transfers_data = response.json()
        
        # Convert to DataFrame
        df_transfers = pd.json_normalize(transfers_data)
        
        # Convert 'time' to datetime
        if 'time' in df_transfers.columns:
            df_transfers['time'] = pd.to_datetime(df_transfers['time'])
        else:
            # Handle missing 'time' column
            df_transfers['time'] = pd.NaT
        
        return df_transfers
    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f'HTTP error occurred while fetching transfers: {http_err}') from http_err
    except Exception as err:
        raise RuntimeError(f'Other error occurred while fetching transfers: {err}') from err

def fetch_history(TID):
    """
    Fetches historical performance data for a given Team ID from the FPL API and returns it as a DataFrame.
    
    Args:
        TID (str): The Team ID.
    
    Returns:
        pd.DataFrame: DataFrame containing performance history.
    """
    history_url = f'https://fantasy.premierleague.com/api/entry/{TID}/history/'
    try:
        response = requests.get(history_url)
        response.raise_for_status()
        history_data = response.json()
        
        # Extract current and past history
        all_history = []
        
        # Current season
        current_history = history_data.get('current', [])
        all_history.extend(current_history)
        
        # Past seasons
        past_history = history_data.get('past', [])
        for season in past_history:
            all_history.extend(season.get('history', []))
        
        if not all_history:
            # Return empty DataFrame with expected columns
            return pd.DataFrame()
        
        # Convert to DataFrame
        df_history = pd.json_normalize(all_history)
        
        return df_history
    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f'HTTP error occurred while fetching history: {http_err}') from http_err
    except Exception as err:
        raise RuntimeError(f'Other error occurred while fetching history: {err}') from err
