from msclap import CLAP


audio_files = ["Audio/symphony_no_5_in_c_minor.mp3"]

clap_model = CLAP(version = 'clapcap', use_cuda=False)

captions = clap_model.generate_caption(audio_files, resample=True, beam_size=5, entry_length=67, temperature=0.01)

# Print the result
for i in range(len(audio_files)):
    print(f"Audio file: {audio_files[i]} \n")
    print(f"Generated caption: {captions[i]} \n")