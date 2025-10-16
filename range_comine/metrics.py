
from typing import Dict, List, Tuple, Set

def participation_index(cliques: List[Tuple[Tuple[str,...], float]],
                        objects_by_id: Dict[str, tuple]) -> float:
    """
    PI = min_f (#distinct instances of f in any clique) / (total instances of f)
    cliques: list of (tuple of object ids in clique), diameter
    """
    if not cliques:
        return 0.0
    # collect features per object id
    feat_of = {oid: objects_by_id[oid][1] for cid,_ in cliques for oid in cid}
    features = set(feat_of.values())
    by_feat: Dict[str, Set[str]] = {f:set() for f in features}
    for cid,_ in cliques:
        for oid in cid:
            by_feat[feat_of[oid]].add(oid)
    # total counts per feature in the dataset
    total_by_feat = {}
    for oid, obj in objects_by_id.items():
        f = obj[1]
        if f in features:
            total_by_feat[f] = total_by_feat.get(f, 0) + 1
    ratios = []
    for f in features:
        num = len(by_feat[f])
        den = total_by_feat[f]
        ratios.append(num / den if den else 0.0)
    return min(ratios) if ratios else 0.0
