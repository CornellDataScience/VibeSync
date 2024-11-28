from msclap import CLAP
from custom_similarity import CustomSimilarity
from utility import *


def main():
    args = parse_arguments()

    config = load_config(args.config)
    audio_files = config["audio_files"]
    similarity_method = config["similarity_method"]
    postprocessing_method = config["postprocessing_method"]
    user_query = config["text_query"]
    print_original_scores = False  # for comparison

    clap_model = CLAP(version="2023", use_cuda=False)

    audio_embeddings = clap_model.get_audio_embeddings(audio_files, resample=True)
    text_embedding = clap_model.get_text_embeddings([user_query])

    similarity_computer = CustomSimilarity(method=similarity_method, postprocessing=postprocessing_method)
    custom_similarities = similarity_computer.compute_similarity(audio_embeddings, text_embedding)

    if print_original_scores:
        original_similarities = clap_model.compute_similarity(audio_embeddings, text_embedding)

    k = config.get("top_k", 3)

    custom_values, custom_indices = custom_similarities.squeeze().topk(k)

    print(f"\nTop {k} songs for query '{user_query}' using {similarity_method}:")
    pretty_print_similarity_results(audio_files, custom_indices, custom_values, user_query, k, similarity_method)

    if print_original_scores:
        original_values, original_indices = original_similarities.squeeze().topk(k)
        print(f"\nTop {k} songs for query '{user_query}' using CLAP's original compute_similarity:")
        pretty_print_similarity_results(audio_files, original_indices, original_values, user_query, k, "original_compute_similarity")


if __name__ == "__main__":
    main()
