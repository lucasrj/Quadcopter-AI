import os
import argparse
import statistics
import pandas as pd
from quadai.balloon import balloon
from quadai.player import SACPlayer

def create_sac_players(path):
    sac_players = []

    # Iterate over each folder in the given path
    for folder_name in os.listdir(path):
        folder_path = os.path.join(path, folder_name)
        
        # Ensure it's a directory
        if os.path.isdir(folder_path):
            model_zip_path = os.path.join(folder_path, 'model.zip')
            
            # Check if 'model.zip' exists in this folder
            if os.path.exists(model_zip_path):
                # Use the full folder name as the player name
                sac_player = SACPlayer(name=folder_name, model_path=model_zip_path)
                sac_players.append(sac_player)

    return sac_players

def calculate_statistics(scores):
    # Calculate statistics for a given list of scores
    stats = {
        'Min': min(scores),
        'Max': max(scores),
        'Mean': statistics.mean(scores),
        'Median': statistics.median(scores),
        'Standard Deviation': statistics.stdev(scores) if len(scores) > 1 else 0  # Avoid stdev error if there's only one score
    }
    return stats

if __name__ == '__main__':
    # Set up argument parser with shortened versions of arguments
    parser = argparse.ArgumentParser(description="Create SACPlayer instances for each model folder.")
    parser.add_argument("-p", "--path", type=str, default=None, help="Path to the models directory. If not provided, defaults to './models'.")
    parser.add_argument("-r", "--run_count", type=int, default=1, help="Number of times to run the balloon function.")
    parser.add_argument("-o", "--output", type=str, help="File path to save the output CSV file.")

    args = parser.parse_args()

    # Determine the path to use
    if args.path:
        path = args.path
    else:
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, 'models')

    # Run the balloon function multiple times and gather scores
    player_scores = {}
    for _ in range(args.run_count):
        sac_players = create_sac_players(path)
        scores = balloon(sac_players)  # Assuming balloon returns a dictionary with player scores
        for player, score in scores.items():
            if player not in player_scores:
                player_scores[player] = []
            player_scores[player].append(score)

    # Calculate and organize the statistics for each player into a Pandas DataFrame
    stats_data = []
    for player, scores in player_scores.items():
        stats = calculate_statistics(scores)
        stats['Player'] = player
        stats_data.append(stats)

    # Convert the list of dictionaries to a Pandas DataFrame
    stats_df = pd.DataFrame(stats_data)

    # Set 'Player' as the index for better display
    stats_df.set_index('Player', inplace=True)

    # Display the DataFrame
    print(stats_df)

    # Save to CSV if the output file path is provided
    if args.output:
        stats_df.to_csv(args.output)
        print(f"Statistics saved to {args.output}")
