from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import logging

# Setup logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Function to get Player ID by Partial Name (Active Players Only)
def get_player_id_by_partial_name(player_name):
    # Fetch strictly active players
    all_players = players.get_active_players()
    
    # Filter for partial name matches
    matching_players = [p for p in all_players if player_name.lower() in p['full_name'].lower()]
    
    # If no players found
    if not matching_players:
        raise ValueError(f"No active player found with the name '{player_name}'.")
    
    # Limit to 12 results for readability
    if len(matching_players) > 12:
        print("Too many results found. Showing the first 12 matches:")
        matching_players = matching_players[:12]

    # If multiple matches found, prompt user to choose
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
        # Return the single match
        return matching_players[0]['id'], matching_players[0]['full_name']




# Function to fetch Player Game Logs
def fetch_player_data_by_name(player_name, season="2023-24"):
    player_id, full_name = get_player_id_by_partial_name(player_name)
    logging.info(f"\nFetching game logs for: {full_name}")
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star="Regular Season")
    df = gamelog.get_data_frames()[0]
    return df, full_name

# Function to calculate Averages for N Games
def calculate_averages(df, num_games=5):
    stats = ['PTS', 'REB', 'AST', 'STL', 'BLK']
    stats = [stat for stat in stats if stat in df.columns]
    df[stats] = df[stats].apply(pd.to_numeric, errors='coerce')
    recent_games = df.head(num_games)  # Limit to the number of games
    avg_stats = recent_games[stats].mean()

    # Calculate combo stats: P+R, P+A, R+A, P+R+A
    p = avg_stats.get('PTS', 0)
    r = avg_stats.get('REB', 0)
    a = avg_stats.get('AST', 0)
    p_r = p + r
    p_a = p + a
    r_a = r + a
    p_r_a = p + r + a

    projected = {
        'PTS': round(p, 1),
        'REB': round(r, 1),
        'AST': round(a, 1),
        'STL': round(avg_stats.get('STL', 0), 1),
        'BLK': round(avg_stats.get('BLK', 0), 1),
        'P+R': round(p_r, 1),
        'P+A': round(p_a, 1),
        'R+A': round(r_a, 1),
        'P+R+A': round(p_r_a, 1)
    }

    return projected

# Main Program
if __name__ == "__main__":
    while True:
        player_name = input("Enter the player's name or last name (or type 'quit' to exit): ").strip()
        if player_name.lower() in ["quit", "exit"]:
            print("Exiting the program.")
            break

        try:
            # Allow user to specify how many games to analyze
            num_games_input = input("Enter the number of recent games to analyze (default is 5): ").strip()
            num_games = int(num_games_input) if num_games_input.isdigit() else 5

            season = "2023-24"
            df, full_name = fetch_player_data_by_name(player_name, season)

            if df.empty:
                print(f"No game logs found for {full_name} in the {season} season.")
            else:
                projected_line = calculate_averages(df, num_games=num_games)
                print(f"\nProjected line for {full_name} based on last {num_games} games:")
                for stat, value in projected_line.items():
                    print(f"{stat}: {value}")

                # Save the output to a CSV
                file_name = f"{full_name.replace(' ', '_')}_projected_stats.csv"
                pd.DataFrame([projected_line]).to_csv(file_name, index=False)
                print(f"Projected stats saved to '{file_name}'.")

        except ValueError as e:
            print(e)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        print("\n--------------------------------------\n")
