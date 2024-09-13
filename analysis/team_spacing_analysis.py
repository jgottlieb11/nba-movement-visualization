import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial import ConvexHull
from team_spacing import TeamSpacingVisualizer
from Match import Match
from Settings import Settings

def calculate_convex_hull_area(positions):
    if len(positions) < 3:
        return 0
    hull = ConvexHull(positions)
    return hull.volume

def get_game_spacing_stats(team_spacing_visualizer, moments):
    """
    Extract spacing stats (Convex Hull areas) from the game moments.

    Args:
        team_spacing_visualizer (TeamSpacingVisualizer): Visualizer instance with loaded data.
        moments (list): List of moments from the game.

    Returns:
        dict: A dictionary with summary statistics (mean Convex Hull areas).
    """
    home_offense_areas = []
    home_defense_areas = []
    away_offense_areas = []
    away_defense_areas = []

    for moment in moments:
        home_positions, away_positions, _ = team_spacing_visualizer.get_positions_and_ball(moment)

        home_hull_area = calculate_convex_hull_area(home_positions)
        away_hull_area = calculate_convex_hull_area(away_positions)

        offensive_team = team_spacing_visualizer.team_name
        if offensive_team == 'home':
            home_offense_areas.append(home_hull_area)
            away_defense_areas.append(away_hull_area)
        else:
            home_defense_areas.append(home_hull_area)
            away_offense_areas.append(away_hull_area)

    return {
        'mean_home_offense_area': np.mean(home_offense_areas),
        'mean_home_defense_area': np.mean(home_defense_areas),
        'mean_away_offense_area': np.mean(away_offense_areas),
        'mean_away_defense_area': np.mean(away_defense_areas)
    }

def plot_defensive_spacing_bar(spacing_data):
    """
    Plots a bar graph showing each team's ability to space the defense.
    
    Args:
        spacing_data (pd.DataFrame): Dataframe with columns of spacing data
            ['home_offense_areas', 'home_defense_areas', 'away_offense_areas', 'away_defense_areas']
    """
    df = pd.DataFrame()
    df['home'] = spacing_data.groupby('home_team')['mean_away_defense_area'].mean()
    df['away'] = spacing_data.groupby('away_team')['mean_home_defense_area'].mean()
    df['average_defensive_spacing'] = (df['home'] + df['away']) / 2

    df['average_defensive_spacing'].sort_values(ascending=False).plot(kind='bar', color=sns.color_palette()[0])
    plt.xlabel('Teams', fontsize=12)
    plt.ylabel("Opponent's Defensive Spacing (Convex Hull Area)", fontsize=12)
    plt.title("Team's Ability to Space the Defense", fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('team_defensive_spacing.png')
    plt.show()

def aggregate_game_data(games_list):
    """
    Aggregates all games' data for spacing analysis.

    Args:
        games_list (list): List of games, where each game is a dictionary with necessary game details.

    Returns:
        pd.DataFrame: DataFrame containing spacing statistics for each game.
    """
    game_stats = []
    for game_info in games_list:
        try:
            if not os.path.exists(game_info['file_path']):
                print(f"Error: File {game_info['file_path']} does not exist. Skipping game.")
                continue

            visualizer = TeamSpacingVisualizer(file_path=game_info['file_path'], team_name=game_info['team_name'])
            visualizer.load_data()

            game_spacing_stats = get_game_spacing_stats(visualizer, visualizer.moments)
            game_spacing_stats['home_team'] = game_info['home_team']
            game_spacing_stats['away_team'] = game_info['away_team']

            game_stats.append(game_spacing_stats)
        except Exception as e:
            print(f"Error processing game {game_info['file_path']}: {e}")
    
    return pd.DataFrame(game_stats)

if __name__ == "__main__":
    games_list = [
        {'file_path': 'data/2016.NBA.Raw.SportVU.Game.Logs/01.01.2016.NYK.at.CHI.7z', 'team_name': 'home', 'home_team': 'CHI', 'away_team': 'NYK'},
        {'file_path': 'data/2016.NBA.Raw.SportVU.Game.Logs/01.01.2016.LAL.at.GSW.7z', 'team_name': 'home', 'home_team': 'GSW', 'away_team': 'LAL'},
    ]
    
    spacing_data = aggregate_game_data(games_list)
    plot_defensive_spacing_bar(spacing_data)
