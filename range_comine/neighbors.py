
from typing import List, Dict, Tuple
from collections import defaultdict
import math

# Object record: (id, feature, x, y)
Obj = Tuple[str, str, float, float]

def euclid(a: Obj, b: Obj) -> float:
    return math.hypot(a[2] - b[2], a[3] - b[3])

def build_star_neighborhood(objects: List[Obj], dmax: float):
    """
    Build star neighborhood SNd for maximum distance dmax.
    Returns:
      star: dict center_id -> list of tuples (neighbor_id, neighbor_feature, dist)
      objects_by_id: dict id -> Obj
      feature_order: deterministic order of features (sorted by name)
    Definition (adapted): only keep neighbors whose feature is <= center feature
    in a total order, to avoid duplicates (joinless/star schema).
    """
    # deterministic total order by feature string
    features = sorted({o[1] for o in objects})
    feat_index = {f:i for i,f in enumerate(features)}
    objects_by_id = {o[0]: o for o in objects}

    star = defaultdict(list)
    n = len(objects)
    # O(n^2) naive; fine for demo-scale
    for i in range(n):
        oi = objects[i]
        for j in range(n):
            oj = objects[j]
            if i == j:
                # self-loop with distance 0 (useful for diameter logic)
                star[oi[0]].append((oj[0], oj[1], 0.0))
                continue
            d = euclid(oi, oj)
            if d <= dmax:
                # star condition: keep neighbor if feat_j <= feat_i in order.
                if feat_index[oj[1]] <= feat_index[oi[1]]:
                    star[oi[0]].append((oj[0], oj[1], d))
    return dict(star), objects_by_id, features
