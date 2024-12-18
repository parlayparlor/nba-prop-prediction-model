from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players, teams
import pandas as pd
import logging

# Setup logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Function to get Player ID by Partial Name (Active Players Only)
def get_player_id_by_partial_name(player_name):
    all_players = players.get_active_players()
    matching_players = [p for p in all_players if player_name.lower() in p['full_name'].lower()]
    if not matching_players:
        raise ValueError(f"No active player found with the name '{player_name}'.")
    if len(matching_players) > 12:
        print("Too many results found. Showing the first 12 matches:")
        matching_players = matching_players[:12]
    if len(matching_players) > 1:
        print("\nMultiple active players found:")
        for idx, p in enumerate(matching_players, 1):
            print(f"{idx}. {p['full_name']}")
        choice = input("Enter the number of the player you want: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(matching_players):
            selected = matching_players[int(choice) - 1]
            return selected['id'], selected['full_name']
        else:
            raise ValueError("Invalid selection. Please try again.")
    else:
        return matching_players[0]['id'], matching_players[0]['full_name']


# Function to fetch Player Game Logs
def fetch_player_data_by_name(player_name, season="2023-24"):
    player_id, full_name = get_player_id_by_partial_name(player_name)
    logging.info(f"\nFetching game logs for: {full_name}")
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star="Regular Season")
    df = gamelog.get_data_frames()[0]
    return df, full_name


from nba_api.stats.endpoints import teamgamelogs

# Function to fetch recent opponent team stats
def get_opponent_team_stats(team_id, season="2023-24", num_games=5):
    # Fetch recent team game logs
    logs = teamgamelogs.TeamGameLogs(season_nullable=season)
    df = logs.get_data_frames()[0]
    
    # Filter for the specific opponent team
    team_games = df[df['TEAM_ID'] == team_id]
    
    if team_games.empty:
        return None

    # Filter only numeric columns for calculations
    numeric_stats = ['PTS', 'REB', 'AST', 'STL', 'BLK']
    team_games = team_games[numeric_stats].head(num_games).apply(pd.to_numeric, errors='coerce')
    
    # Calculate averages for last 'num_games'
    team_avg = team_games.mean()
    return team_avg.round(1)



# Function to map Team Abbreviation to Team ID
def get_team_id_by_abbreviation(abbreviation):
    nba_teams = teams.get_teams()
    team = next((team for team in nba_teams if team['abbreviation'] == abbreviation), None)
    return team['id'] if team else None


# Function to get Opponent Team ID from the Game Logs
def get_opponent_team_id(df):
    opponent_team_ids = df['MATCHUP'].apply(lambda x: x.split(' ')[-1]).unique()
    print("\nRecent Opponent Teams:")
    for idx, team in enumerate(opponent_team_ids, 1):
        print(f"{idx}. {team}")
    choice = input("Choose an opponent team number for strength analysis (or press Enter to skip): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(opponent_team_ids):
        abbreviation = opponent_team_ids[int(choice) - 1]
        return get_team_id_by_abbreviation(abbreviation)  # Convert abbreviation to Team ID
    return None


def calculate_averages(df, num_games=5):
    stats = ['PTS', 'REB', 'AST', 'STL', 'BLK']
    stats = [stat for stat in stats if stat in df.columns]
    df[stats + ['MIN']] = df[stats + ['MIN']].apply(pd.to_numeric, errors='coerce')
    avg_minutes = df['MIN'].mean()
    def weight_game(row):
        if row['MIN'] < 0.7 * avg_minutes:
            return 0.5
        elif row['MIN'] > 0.85 * avg_minutes:
            return 1.5
        return 1.0
    df['WEIGHT'] = df.apply(weight_game, axis=1)
    recent_games = df.head(num_games)
    weighted_avg = (recent_games[stats].multiply(recent_games['WEIGHT'], axis=0)).sum() / recent_games['WEIGHT'].sum()
    p = weighted_avg.get('PTS', 0)
    r = weighted_avg.get('REB', 0)
    a = weighted_avg.get('AST', 0)
    p_r = p + r
    p_a = p + a
    r_a = r + a
    p_r_a = p + r + a
    return {
        'PTS': round(p, 1), 'REB': round(r, 1), 'AST': round(a, 1),
        'STL': round(weighted_avg.get('STL', 0), 1), 'BLK': round(weighted_avg.get('BLK', 0), 1),
        'P+R': round(p_r, 1), 'P+A': round(p_a, 1), 'R+A': round(r_a, 1), 'P+R+A': round(p_r_a, 1)
    }


# Main Program
if __name__ == "__main__":
    while True:
        player_name = input("Enter the player's name or last name (or type 'quit' to exit): ").strip()
        if player_name.lower() in ["quit", "exit"]:
            print("Exiting the program.")
            break

        try:
            num_games_input = input("Enter the number of recent games to analyze (default is 5): ").strip()
            num_games = int(num_games_input) if num_games_input.isdigit() else 5

            season = "2023-24"
            df, full_name = fetch_player_data_by_name(player_name, season)

            if df.empty:
                print(f"No game logs found for {full_name} in the {season} season.")
            else:
                opponent_team = get_opponent_team_id(df)
                if opponent_team:
                    opponent_stats = get_opponent_team_stats(opponent_team)
                    if opponent_stats is not None:
                        print("\nOpponent Team Recent Averages:")
                        for stat, value in opponent_stats.items():
                            print(f"{stat}: {value}")
                    else:
                        print("Could not fetch opponent team stats.")
                projected_line = calculate_averages(df, num_games=num_games)
                print(f"\nProjected line for {full_name} based on last {num_games} games:")
                for stat, value in projected_line.items():
                    print(f"{stat}: {value}")
                file_name = f"{full_name.replace(' ', '_')}_projected_stats.csv"
                pd.DataFrame([projected_line]).to_csv(file_name, index=False)
                print(f"Projected stats saved to '{file_name}'.")

        except ValueError as e:
            print(e)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        print("\n--------------------------------------\n")
