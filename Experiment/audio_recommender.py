import os
from msclap import CLAP
from custom_similarity import CustomSimilarity
from Experiment.utility import *


def main():
    args = parse_arguments()

    config = load_config(args.config)

    # Ensure audio directory and fetch all audio files
    audio_dir = config["audio_directory"]
    print("Retrieving audio files...")
    audio_files = get_audio_files(audio_dir)
    print("Retrieval complete!")

    text_queries = config["text_query"]
    similarity_methods = config["similarity_methods"]
    postprocessing_method = config["postprocessing_method"]
    save_to = config.get("save_to", None)
    include_original = config.get("include_original", False)
    k = config.get("top_k", 3)

    # Convert single strings to lists
    if isinstance(text_queries, str):
        text_queries = [text_queries]
    if isinstance(similarity_methods, str):
        similarity_methods = [similarity_methods]

    # Validate configuration
    if len(text_queries) > 1 and len(similarity_methods) > 1:
        raise ValueError(
            "Configuration error: Provide either multiple text queries or multiple compute methods, not both.")

    # Initialize CLAP model
    clap_model = CLAP(version="2023", use_cuda=False)

    # Compute audio embeddings
    print("Computing audio embeddings...")
    audio_embeddings = clap_model.get_audio_embeddings(
        audio_files, resample=False)
    print("Audio embeddings complete!")

    # Prepare output handling
    if save_to:
        os.makedirs(os.path.dirname(save_to), exist_ok=True)
        output_file = open(save_to, "w")
        output_file.write(f"Experiment Configuration:\n")
        output_file.write(f"Audio Directory: {audio_dir}\n")
        output_file.write(f"Postprocessing Method: {postprocessing_method}\n")
        output_file.write(f"Top K: {k}\n\n")
    else:
        output_file = None

    def format_audio_name(filepath):
        return os.path.splitext(os.path.basename(filepath))[0]

    # Generate results
    print("Generating results...")
    for query in text_queries:
        text_embedding = clap_model.get_text_embeddings([query])

        for similarity_method in similarity_methods:
            similarity_computer = CustomSimilarity(
                method=similarity_method, postprocessing=postprocessing_method)
            custom_similarities = similarity_computer.compute_similarity(
                audio_embeddings, text_embedding)

            custom_values, custom_indices = custom_similarities.squeeze().topk(k)

            # Write results
            if output_file:
                output_file.write(f"Text Query: {query}\n")
                output_file.write(f"Similarity Method: {similarity_method}\n")
                output_file.write(f"Top {k} Songs:\n")
                for i, index in enumerate(custom_indices):
                    song = format_audio_name(audio_files[index])
                    score = custom_values[i].item()
                    output_file.write(
                        f"  {i + 1}. {song} (Similarity: {score:.2f})\n")
                output_file.write("\n")
            else:
                pretty_print_similarity_results(
                    audio_files, custom_indices, custom_values, query, k, similarity_method)

        # Include original compute similarity if flag is set
        if include_original:
            original_similarities = clap_model.compute_similarity(
                audio_embeddings, text_embedding)

            original_values, original_indices = original_similarities.squeeze().topk(k)

            if output_file:
                output_file.write(f"Text Query: {query}\n")
                output_file.write("Original Compute Similarity Results:\n")
                output_file.write(f"Top {k} Songs:\n")
                for i, index in enumerate(original_indices):
                    song = format_audio_name(audio_files[index])
                    score = original_values[i].item()
                    output_file.write(
                        f"  {i + 1}. {song} (Similarity: {score:.2f})\n")
                output_file.write("\n")
            else:
                pretty_print_similarity_results(
                    audio_files, original_indices, original_values, query, k, "Original Compute Similarity")

    print("Generation complete!")
    if output_file:
        output_file.close()
        print(f"Results written to {save_to}")


if __name__ == "__main__":
    main()
