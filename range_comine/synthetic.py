
from typing import List, Tuple
import random, math

Obj = Tuple[str, str, float, float]

def generate_synthetic(n_features: int = 4, instances_per_feat: int = 8, 
                       width: float = 100.0, height: float = 100.0, seed: int = 13) -> List[Obj]:
    """Simple synthetic generator (demo). Returns list of (id, feature, x, y)."""
    rng = random.Random(seed)
    objs: List[Obj] = []
    features = [chr(ord('A')+i) for i in range(n_features)]
    idx = 1
    for f in features:
        for _ in range(instances_per_feat):
            x = rng.uniform(0, width)
            y = rng.uniform(0, height)
            oid = f"{f}.{idx}"
            objs.append((oid, f, x, y))
            idx += 1
    return objs
