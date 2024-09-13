import py7zr
import tempfile
import argparse
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon, Circle
from matplotlib import animation
from PIL import Image
from Match import Match
from Settings import Settings
from Moment import Moment

class TeamSpacingVisualizer:
    def __init__(self, file_path, team_name):
        self.file_path = file_path
        self.team_name = team_name.lower()
        self.data = None
        self.moments = []
        self.match = None

    def extract_7z_and_get_json(self):
        """Extract the .7z file and return the path to the extracted .json file"""
        temp_dir = tempfile.mkdtemp()

        with py7zr.SevenZipFile(self.file_path, mode='r') as archive:
            archive.extractall(path=temp_dir)

        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".json"):
                    return os.path.join(root, file)

        raise FileNotFoundError("No JSON file found inside the .7z archive")

    def load_data(self):
        """Load game data from a .json file"""
        if self.file_path.endswith(".7z"):
            json_file = self.extract_7z_and_get_json()
        else:
            json_file = self.file_path

        with open(json_file) as f:
            self.data = json.load(f)

        for event in self.data['events']:
            self.moments.extend([Moment(moment) for moment in event['moments']])
        
        event_data = self.data['events'][0]
        self.match = Match(event_data)

    def get_positions_and_ball(self, moment):
        """Extract the positions of all players and ball for a moment"""
        home_positions = []
        away_positions = []
        ball_position = (moment.ball.x, moment.ball.y, moment.ball.radius)

        for player in moment.players:
            if player.team.id == moment.players[0].team.id:
                home_positions.append((player.x, player.y))
            else:
                away_positions.append((player.x, player.y))

        return home_positions, away_positions, ball_position

    def update_visuals(self, frame, home_circles, away_circles, ball_circle, hull_patch, annotations, clock_info):
        """Update the positions of the players, ball, and convex hull for each frame."""
        moment = self.moments[frame]
        home_positions, away_positions, ball_position = self.get_positions_and_ball(moment)

       
        for i, circle in enumerate(home_circles):
            circle.center = home_positions[i]
            annotations[i].set_position(circle.center)

        
        for i, circle in enumerate(away_circles):
            circle.center = away_positions[i]
            annotations[i + 5].set_position(circle.center)

        ball_circle.center = ball_position[0], ball_position[1]
        ball_circle.radius = ball_position[2] / 7
        
        team_positions = np.array(home_positions if self.team_name == 'home' else away_positions)
        if len(team_positions) >= 3:
            hull = ConvexHull(team_positions)
            hull_patch.set_xy(team_positions[hull.vertices])

        clock_text = 'Quarter {:d}\n{:02d}:{:02d}\n{:03.1f}'.format(
            moment.quarter,
            int(moment.game_clock) // 60,
            int(moment.game_clock) % 60,
            moment.shot_clock if moment.shot_clock is not None else 0
        )
        clock_info.set_text(clock_text)

        return home_circles + away_circles + [ball_circle, hull_patch] + [clock_info]


    def _draw_court(self, ax=None):
        """Draw the court layout with the court image as the background"""
        if ax is None:
            ax = plt.gca()

       
        try:
            img = Image.open("../court_converted.jpeg")
            court_array = np.asarray(img)
            ax.imshow(court_array, zorder=0, extent=[0, 100, 50, 0])
        except Exception as e:
            print(f"Error loading and displaying the court image: {e}")

        ax.set_xlim(0, 100)
        ax.set_ylim(0, 50)
        ax.set_xticks([])
        ax.set_yticks([])

    def animate(self):
        """Animate the team spacing visualization across multiple moments"""
        fig, ax = plt.subplots()
        self._draw_court(ax)

        start_moment = self.moments[0]
        home_positions, away_positions, ball_position = self.get_positions_and_ball(start_moment)
        home_positions = np.array(home_positions)
        away_positions = np.array(away_positions)

        home_circles = [Circle((x, y), 1.5, color='blue') for x, y in home_positions]
        away_circles = [Circle((x, y), 1.5, color='red') for x, y in away_positions]

        for circle in home_circles + away_circles:
            ax.add_patch(circle)

        ball_circle = Circle((ball_position[0], ball_position[1]), ball_position[2] / 7, color='orange')
        ax.add_patch(ball_circle)

        team_positions = home_positions if self.team_name == 'home' else away_positions

        hull_patch = Polygon([[0, 0]], alpha=0.3, color='gray')

        if len(team_positions) >= 3:
            hull = ConvexHull(team_positions)
            hull_patch = Polygon(team_positions[hull.vertices], alpha=0.3, color='gray')

        ax.add_patch(hull_patch)

        player_dict = self.match.player_ids_dict
        sorted_players = sorted(start_moment.players, key=lambda player: player.team.id)

        annotations = [
            ax.annotate(f'{player_dict[player.id][1]}', xy=pos, color='white', ha='center', va='center', fontweight='bold')
            for player, pos in zip(sorted_players[:5], home_positions)
        ]
        annotations += [
            ax.annotate(f'{player_dict[player.id][1]}', xy=pos, color='white', ha='center', va='center', fontweight='bold')
            for player, pos in zip(sorted_players[5:], away_positions)
        ]

        column_labels = (sorted_players[0].team.name, sorted_players[5].team.name)
        column_colours = (sorted_players[0].team.color, sorted_players[5].team.color)
        cell_colours = [column_colours for _ in range(5)]

        home_players = [' #'.join([player_dict[player.id][0], player_dict[player.id][1]]) for player in sorted_players[:5]]
        guest_players = [' #'.join([player_dict[player.id][0], player_dict[player.id][1]]) for player in sorted_players[5:]]
        players_data = list(zip(home_players, guest_players))

        table = plt.table(cellText=players_data, colLabels=column_labels, colColours=column_colours,
                          colWidths=[Settings.COLUMN_WIDTH, Settings.COLUMN_WIDTH], loc='bottom',
                          cellColours=cell_colours, fontsize=Settings.FONT_SIZE, cellLoc='center')
        table.scale(1, Settings.COURT_SCALE)

        table_cells = table.properties().get('child_artists', [])
        for cell in table_cells:
            cell._text.set_color('white')

        clock_info = ax.annotate('', xy=(50, 45), color='black', ha='center', va='center')

        anim = animation.FuncAnimation(
            fig, self.update_visuals, frames=len(self.moments),
            fargs=(home_circles, away_circles, ball_circle, hull_patch, annotations, clock_info),
            interval=100, blit=False, repeat=False
        )

        plt.show()
        
    def plot_team_defensive_spacing(self):
        """Plot of team's defensive spacing (bar graph)"""
        teams = ['DEN', 'DAL', 'TOR', 'MIL', 'CHA', 'POR', 'ATL', 'IND', 'BKN', 'SAC',
                 'MIA', 'OKC', 'NYK', 'PHI', 'MEM', 'ORL', 'PHX', 'SAS', 'GSW', 'UTA',
                 'MIN', 'BOS', 'LAL', 'CHI', 'HOU', 'NOP', 'CLE', 'LAC', 'WAS', 'DET']
        
        defensive_spacing = [62.2, 62.8, 62.9, 63, 63.3, 63.8, 63.8, 63.9, 63.9, 63.95,
                             64.2, 64.29, 64.8, 65, 65.3, 65.3, 65.7, 65.8, 65.8, 65.83,
                             65.85, 65.87, 65.89, 66.08, 66.12, 66.5, 66.6, 66.8, 67.68, 67.8]

        team_colors = ['#4D90CD', '#007DC5', '#CE1141', '#00471B', '#1D1160', '#E03A3E', '#E13A3E',
                       '#00275D', '#061922', '#724C9F', '#98002E', '#007DC3', '#006BB6', '#006BB6',
                       '#0F586C', '#007DC5', '#1D1160', '#BAC3C9', '#FDB927', '#00471B', '#005083',
                       '#008348', '#552582', '#CE1141', '#CE1141', '#002B5C', '#860038', '#ED174C',
                       '#002B5C', '#006BB6']
        
        plt.figure(figsize=(12, 6))
        plt.bar(teams, defensive_spacing, color=team_colors)
        plt.xlabel('', fontsize=16)
        plt.ylabel("Opponent's Defensive Spacing (sq ft)", fontsize=16)
        plt.title("Team's Ability to Space the Defense", fontsize=18)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(62, 68)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize team spacing using Convex Hull with animation.')
    parser.add_argument('--path', type=str, help='Path to the game .7z or JSON file', required=True)
    parser.add_argument('--team', type=str, help='Team name (home or visitor)', required=True)

    args = parser.parse_args()

    visualizer = TeamSpacingVisualizer(file_path=args.path, team_name=args.team)
    visualizer.load_data()
    visualizer.animate()

    visualizer.plot_team_defensive_spacing()
