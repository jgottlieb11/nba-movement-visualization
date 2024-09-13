import argparse
import os
import py7zr
import json
import tempfile
from Play import Play

def extract_7z_and_get_json(archive_path):
    temp_dir = tempfile.mkdtemp()

    with py7zr.SevenZipFile(archive_path, mode='r') as archive:
        archive.extractall(path=temp_dir)

    json_file = None
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".json"):
                json_file = os.path.join(root, file)
                break

    if not json_file:
        raise FileNotFoundError("No JSON file found inside the .7z archive")

    return json_file


def main():
    parser = argparse.ArgumentParser(description='Process arguments related to an NBA game.')
    parser.add_argument('--path', type=str,
                        help='Path to the .7z file containing the game events',
                        required=True)
    parser.add_argument('--event', type=int, default=0,
                        help="""Index of the event to animate
                                (Index starts at 0, and if the index is out of bounds,
                                the last event of the game will be shown)""")

    args = parser.parse_args()

    if args.path.endswith(".7z"):
        json_file_path = extract_7z_and_get_json(args.path)
    else:
        json_file_path = args.path

    game = Play(json_path=json_file_path, event_number=args.event)
    game.load_data()
    game.begin()

if __name__ == "__main__":
    main()
