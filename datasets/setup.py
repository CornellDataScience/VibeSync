import kagglehub

# Download latest version
path = kagglehub.dataset_download("fayssalelansari/wasabi-song-corpus")

print("Path to dataset files:", path)