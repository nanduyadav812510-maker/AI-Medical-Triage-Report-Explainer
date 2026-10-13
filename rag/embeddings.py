import math
import re
from typing import List, Dict


def tokenize(text: str) -> List[str]:
    """Basic word tokenizer."""
    return re.findall(r"\w+", text.lower())


def compute_tf(text: str) -> Dict[str, float]:
    """Compute Term Frequency."""
    words = tokenize(text)
    total = len(words)
    if total == 0:
        return {}
    tf_dict = {}
    for word in words:
        tf_dict[word] = tf_dict.get(word, 0) + 1 / total
    return tf_dict


def cosine_similarity_tf(text1: str, text2: str) -> float:
    """Compute cosine similarity between two text snippets."""
    tf1 = compute_tf(text1)
    tf2 = compute_tf(text2)

    vocab = set(tf1.keys()).union(set(tf2.keys()))
    if not vocab:
        return 0.0

    dot_product = sum(tf1.get(w, 0.0) * tf2.get(w, 0.0) for w in vocab)
    norm1 = math.sqrt(sum(v ** 2 for v in tf1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in tf2.values()))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot_product / (norm1 * norm2)
