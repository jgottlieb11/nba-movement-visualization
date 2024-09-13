import json
from Settings import Settings
from Match import Match
from Team import Team

class Play:
    """A class for managing game sessions"""

    def __init__(self, json_path, event_number):
        self.home_team = None
        self.guest_team = None
        self.match = None
        self.json_path = json_path
        self.event_number = event_number

    def load_data(self):
        with open(self.json_path) as f:
            data = json.load(f)

        last_event_index = len(data['events']) - 1
        self.event_number = min(self.event_number, last_event_index)

        print(Settings.NOTIFICATION + str(last_event_index))

        event_data = data['events'][self.event_number]
        self.match = Match(event_data)
        self.home_team = Team(event_data['home']['teamid'])
        self.guest_team = Team(event_data['visitor']['teamid'])

    def begin(self):
        self.match.display()
