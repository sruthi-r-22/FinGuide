RETRIEVAL_SCORE_THRESHOLD = 0.35


def cosine_similarity_from_squared_l2(distance: float) -> float:
    """Convert squared L2 distance between normalized vectors to cosine similarity."""
    return max(0.0, 1.0 - (distance / 2.0))
