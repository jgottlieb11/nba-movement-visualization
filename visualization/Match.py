from Settings import Settings
from Moment import Moment
from Team import Team
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Circle
import numpy as np
from PIL import Image

class Match:
    """A class for handling and displaying matches"""

    def __init__(self, event_data):
        moments = event_data['moments']
        self.moments = [Moment(moment) for moment in moments]
        home_players = event_data['home']['players']
        guest_players = event_data['visitor']['players']
        players = home_players + guest_players

        player_ids = [player['playerid'] for player in players]
        player_names = [" ".join([player['firstname'], player['lastname']]) for player in players]
        player_jerseys = [player['jersey'] for player in players]
        self.player_ids_dict = dict(zip(player_ids, zip(player_names, player_jerseys)))

    def update_visuals(self, index, player_circles, ball_circle, annotations, clock_info):
        moment = self.moments[index]
        for j, circle in enumerate(player_circles):
            circle.center = moment.players[j].x, moment.players[j].y
            annotations[j].set_position(circle.center)
            clock_text = 'Quarter {:d}\n {:02d}:{:02d}\n {:03.1f}'.format(
                moment.quarter,
                int(moment.game_clock) % 3600 // 60,
                int(moment.game_clock) % 60,
                moment.shot_clock if moment.shot_clock is not None else 0
            )
            clock_info.set_text(clock_text)

        ball_circle.center = moment.ball.x, moment.ball.y
        ball_circle.radius = moment.ball.radius / Settings.SCALING_FACTOR
        return player_circles, ball_circle

    def display(self):
        fig, ax = plt.subplots()
        ax.set_xlim(Settings.MIN_X, Settings.MAX_X)
        ax.set_ylim(Settings.MIN_Y, Settings.MAX_Y)
        ax.axis('off')
        ax.grid(False)

        start_moment = self.moments[0]
        player_dict = self.player_ids_dict

        clock_info = ax.annotate('', xy=[Settings.CENTER_X, Settings.CENTER_Y],
                                 color='black', horizontalalignment='center',
                                 verticalalignment='center')

        annotations = [ax.annotate(self.player_ids_dict[player.id][1], xy=[0, 0], color='w',
                                   horizontalalignment='center', verticalalignment='center', fontweight='bold')
                       for player in start_moment.players]

        sorted_players = sorted(start_moment.players, key=lambda player: player.team.id)
        home_player = sorted_players[0]
        guest_player = sorted_players[5]
        column_labels = (home_player.team.name, guest_player.team.name)
        column_colours = (home_player.team.color, guest_player.team.color)
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

        player_circles = [Circle((0, 0), Settings.PLAYER_SIZE_RATIO, color=player.color)
                          for player in start_moment.players]
        ball_circle = Circle((0, 0), Settings.PLAYER_SIZE_RATIO, color=start_moment.ball.color)

        for circle in player_circles:
            ax.add_patch(circle)
        ax.add_patch(ball_circle)

        anim = animation.FuncAnimation(
            fig, self.update_visuals,
            fargs=(player_circles, ball_circle, annotations, clock_info),
            frames=len(self.moments), interval=Settings.REFRESH_RATE, repeat=False)

        try:
            img = Image.open("../court_converted.jpeg")
            court_array = np.asarray(img)
            ax.imshow(court_array, zorder=0, extent=[Settings.MIN_X, Settings.MAX_X - Settings.OFFSET,
                                                     Settings.MAX_Y, Settings.MIN_Y])
        except Exception as e:
            print(f"Error loading and displaying the court image: {e}")

        plt.show()
