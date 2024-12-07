import os
import json
import argparse


def get_audio_files(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(('.mp3', '.wav'))]


def load_config(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config


def parse_arguments():
    parser = argparse.ArgumentParser(description="Audio Similarity Script")
    parser.add_argument(
        "--config", 
        type=str, 
        required=True, 
        help="Path to the configuration file (e.g., config.json)"
    )
    return parser.parse_args()
  
  
def pretty_print_similarity_results(audio_files, indices, values, user_query, k, similarity_method):
    print(f"\nTop {k} songs for query '{user_query}' using {similarity_method}:")
    for i, index in enumerate(indices):
        song = audio_files[index]
        score = values[i].item()
        print(f"  {i + 1}. {song} (Similarity: {score:.2f})")
