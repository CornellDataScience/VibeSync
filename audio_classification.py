from msclap import CLAP
import torch.nn.functional as F


clap_model = CLAP(version = '2023', use_cuda=False)

classes = ["anime song", "pop song", "hip hop", "classical"]
audio_files = ["List of audio files"]

# Extract text embeddings
text_embeddings = clap_model.get_text_embeddings(classes)

# Extract audio embeddings
audio_embeddings = clap_model.get_audio_embeddings(audio_files, resample=True)

# Compute similarity between audio and text embeddings 
similarities = clap_model.compute_similarity(audio_embeddings, text_embeddings)

similarity = F.softmax(similarities, dim=1)
values, indices = similarity[0].topk(4)

for song_index, audio_file in enumerate(audio_files):
    print(f"\nSimilarity scores for '{audio_file}':")
    for class_index, class_label in enumerate(classes):
        score = similarity[song_index][class_index].item() * 100
        print(f"  {class_label:>16s}: {score:.2f}%")