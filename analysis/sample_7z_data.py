import json
import os
import py7zr
import tempfile
import argparse
from linear_regression import LinearRegressionModel

def extract_7z_and_get_json(archive_path):
    """Extract the .7z file and return the path to the extracted .json file"""
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

def print_json_sample(json_file_path, num_events=1):
    """Print a sample of the JSON data from the file"""
    with open(json_file_path) as f:
        data = json.load(f)
    
    print(f"Number of events: {len(data['events'])}")
    
    for i, event in enumerate(data['events'][:num_events]):
        print(f"\n--- Event {i + 1} ---")
        print(json.dumps(event, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract and print a sample of NBA game data from a .7z file.')
    parser.add_argument('--path', type=str, help='Path to the .7z file containing the game events', required=True)
    parser.add_argument('--num_events', type=int, default=1, help='Number of events to print (default is 1)')

    args = parser.parse_args()

    json_file_path = extract_7z_and_get_json(args.path)

    print_json_sample(json_file_path, args.num_events)

