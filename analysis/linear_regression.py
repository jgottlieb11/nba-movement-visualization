import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import argparse

class LinearRegressionModel:
    """
    A class to load game data and perform linear regression between
    Home Team Defensive Spacing Differential and Home Team Score Differential.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.game_data = None
        self.home_defensive_spacing_diff = []
        self.home_score_diff = []

    def load_data(self):
        """
        Loads the JSON data from a specified file path.
        """
        extracted_path = "./temp_extracted"
        os.system(f"7za x {self.file_path} -o{extracted_path}")
        
        json_file = None
        for file in os.listdir(extracted_path):
            if file.endswith('.json'):
                json_file = os.path.join(extracted_path, file)
                break
        
        if not json_file:
            raise FileNotFoundError("No JSON file found in the extracted .7z archive.")
        
        with open(json_file, 'r') as f:
            self.game_data = json.load(f)

        os.system(f"rm -rf {extracted_path}")
        
        print(f"Loaded data from {json_file}")

    def process_data(self):
        """
        Processes the loaded game data to extract the defensive spacing
        differential and score differential.
        """
        for event in self.game_data['events']:
            home_score = event.get('home_score', 0)
            visitor_score = event.get('visitor_score', 0)

            score_diff = home_score - visitor_score

            home_positions = [moment['positions'] for moment in event['moments'] if moment['team'] == 'home']
            away_positions = [moment['positions'] for moment in event['moments'] if moment['team'] == 'visitor']
            
            home_area = self.calculate_convex_hull_area(home_positions)
            away_area = self.calculate_convex_hull_area(away_positions)

            defensive_spacing_diff = home_area - away_area
            
            self.home_defensive_spacing_diff.append(defensive_spacing_diff)
            self.home_score_diff.append(score_diff)

    def calculate_convex_hull_area(self, positions):
        """
        Calculates the convex hull area from player positions.
        Args:
            positions (list): List of player positions [(x, y), ...]
        Returns:
            float: Convex hull area
        """
        from scipy.spatial import ConvexHull
        if len(positions) < 3:
            return 0.0
        positions = np.array(positions)
        hull = ConvexHull(positions)
        return hull.area

    def perform_regression(self):
        """
        Performs linear regression on the extracted data.
        """
        X = np.array(self.home_defensive_spacing_diff).reshape(-1, 1)
        y = np.array(self.home_score_diff)

        reg = LinearRegression()
        reg.fit(X, y)

        y_pred = reg.predict(X)

        plt.figure(figsize=(8, 6))
        plt.scatter(X, y, color='blue', label='Data Points')
        plt.plot(X, y_pred, color='red', label='Regression Line')
        plt.xlim(-10, 10)
        plt.ylim(-60, 60)
        plt.xlabel("Home Team Defensive Spacing Differential")
        plt.ylabel("Home Team Score Differential")
        plt.title("Linear Regression: Spacing Differential vs Score Differential")
        plt.legend()
        plt.grid(True)
        plt.show()

        print(f"R-squared: {r2_score(y, y_pred)}")


def main():
    parser = argparse.ArgumentParser(description="Perform linear regression on NBA game data.")
    parser.add_argument('--path', required=True, help="Path to the .7z file containing the game data.")
    args = parser.parse_args()

    regressor = LinearRegressionModel(file_path=args.path)
    
    regressor.load_data()
    regressor.process_data()

    regressor.perform_regression()


if __name__ == "__main__":
    main()
