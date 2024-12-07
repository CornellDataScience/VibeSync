import torch
import torch.nn.functional as F
from scipy.stats import pearsonr
from scipy.spatial.distance import mahalanobis
from utility import *


class CustomSimilarity:
    
    def __init__(self, method="cosine_similarity", postprocessing="raw"):
        self.method = method
        self.postprocessing = postprocessing

    def compute_similarity(self, embeddings_a, embeddings_b):
        if self.method == "cosine_similarity":
            similarities = self.cosine_similarity(embeddings_a, embeddings_b)
        elif self.method == "euclidean_distance":
            similarities = self.euclidean_distance(embeddings_a, embeddings_b)
        elif self.method == "manhattan_distance":
            similarities = self.manhattan_distance(embeddings_a, embeddings_b)
        elif self.method == "jaccard_similarity":
            similarities = self.jaccard_similarity(embeddings_a, embeddings_b)
        elif self.method == "kl_divergence":
            similarities = self.kl_divergence(embeddings_a, embeddings_b)
        elif self.method == "pearson_correlation":
            similarities = self.pearson_correlation(embeddings_a, embeddings_b)
        else:
            raise ValueError(f"Unknown similarity method: {self.method}")
        
        return self.postprocess(similarities)

    @staticmethod
    def cosine_similarity(embeddings_a, embeddings_b):
        embeddings_a = embeddings_a / torch.norm(embeddings_a, dim=-1, keepdim=True)
        embeddings_b = embeddings_b / torch.norm(embeddings_b, dim=-1, keepdim=True)
        return embeddings_a @ embeddings_b.T

    @staticmethod
    def euclidean_distance(embeddings_a, embeddings_b):
        distances = torch.cdist(embeddings_a, embeddings_b, p=2)
        return -distances
    
    @staticmethod
    def manhattan_distance(embeddings_a, embeddings_b):
        distances = torch.cdist(embeddings_a, embeddings_b, p=1)
        return -distances

    @staticmethod
    def jaccard_similarity(embeddings_a, embeddings_b):
        embeddings_a = embeddings_a > 0
        embeddings_b = embeddings_b > 0

        intersection = torch.sum(embeddings_a & embeddings_b, dim=-1, keepdim=True)
        union = torch.sum(embeddings_a | embeddings_b, dim=-1, keepdim=True)
        return intersection / union

    @staticmethod
    def kl_divergence(embeddings_a, embeddings_b):
        eps = 1e-10  # Small value to avoid log(0)
        embeddings_a = F.softmax(embeddings_a, dim=-1) + eps
        embeddings_b = F.softmax(embeddings_b, dim=-1) + eps

        embeddings_a_log = embeddings_a.log()
        embeddings_b_log = embeddings_b.log()

        embeddings_a = embeddings_a.unsqueeze(1)
        embeddings_a_log = embeddings_a_log.unsqueeze(1)

        embeddings_b = embeddings_b.unsqueeze(0)
        embeddings_b_log = embeddings_b_log.unsqueeze(0)

        kl_div = (embeddings_a * (embeddings_a_log - embeddings_b_log)).sum(dim=-1)
        return -kl_div

    @staticmethod
    def pearson_correlation(embeddings_a, embeddings_b):
        similarities = []
        for a in embeddings_a:
            sim = [pearsonr(a.numpy(), b.numpy())[0] for b in embeddings_b]  # Move tensors to CPU first if using GPU
            similarities.append(sim)
        return torch.tensor(similarities)
    
    # TODO: Make the ordering invariant of the postprocessing method (for now, default to raw)
    def postprocess(self, similarities):
        if self.postprocessing == "softmax":
            return F.softmax(similarities, dim=0) * 100
        elif self.postprocessing == "scaled_100":
            min_val, max_val = similarities.min(), similarities.max()
            scaled = (similarities - min_val) / (max_val - min_val) * 100
            return scaled
        elif self.postprocessing == "raw":
            return similarities
        else:
            raise ValueError(f"Unknown postprocessing method: {self.postprocessing}")
