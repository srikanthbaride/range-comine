
from typing import List, Dict, Tuple
from collections import defaultdict
import itertools, math
from .neighbors import build_star_neighborhood
from .mining import enumerate_size2_cliques, filter_k_cliques, candidate_join

def _pair_distances(star, objects_by_id, d1, d2):
    seen = set()
    dists = set()
    for center, neighs in star.items():
        for nid, nf, dist in neighs:
            if dist == 0.0: 
                continue
            a,b = sorted((center, nid))
            if (a,b) in seen:
                continue
            seen.add((a,b))
            if d1 <= dist <= d2:
                dists.add(dist)
    return sorted(dists, reverse=True)

def _prevalent_at(objects_by_id, patterns, cliques_by_pat, min_prev):
    prev = []
    for pat in patterns:
        cliques = cliques_by_pat.get(pat, [])
        if not cliques: 
            continue
        feats = set(pat)
        totals = {f:0 for f in feats}
        for oid,obj in objects_by_id.items():
            if obj[1] in feats:
                totals[obj[1]] += 1
        seen = {f:set() for f in feats}
        for cid,_ in cliques:
            for oid in cid:
                f = objects_by_id[oid][1]
                if f in feats:
                    seen[f].add(oid)
        pi = min(len(seen[f])/totals[f] for f in feats)
        if pi >= min_prev:
            prev.append(pat)
    return prev

def _cliques_at_distance(objects_by_id, star, features, d):
    # build cliques for all patterns at threshold d (recompute)
    cliques_by_pat = {}
    # k=2
    for pair in itertools.combinations(features, 2):
        cand = tuple(sorted(pair))
        cliques_by_pat[cand] = [(cid, dia) for (cid, dia) in enumerate_size2_cliques(cand, star, objects_by_id, d) if dia <= d]
    # k>=3 (naive enumeration)
    k = 3
    prev = [tuple(sorted(p)) for p in itertools.combinations(features, 2)]
    while prev:
        Ck = candidate_join(prev)
        new_prev = []
        for cand in Ck:
            clqs = [(cid, dia) for (cid, dia) in filter_k_cliques(cand, star, objects_by_id, d) if dia <= d]
            if clqs:
                cliques_by_pat[cand] = clqs
                new_prev.append(cand)
        prev = new_prev
        k += 1
    return cliques_by_pat

def naive_range(objects, d1: float, d2: float, min_prev: float):
    star, objects_by_id, features = build_star_neighborhood(objects, d2)
    # candidate distances (D_pair) from star at d2, desc
    Dpair = _pair_distances(star, objects_by_id, d1, d2)
    if not Dpair:
        return {}
    ColList = defaultdict(list)
    # initial at first (largest) distance
    clq_prev = _cliques_at_distance(objects_by_id, star, features, Dpair[0])
    patterns_all = sorted(set(list(clq_prev.keys())))
    prev_prev = _prevalent_at(objects_by_id, patterns_all, clq_prev, min_prev)
    # compare against next distances
    for i in range(1, len(Dpair)):
        d = Dpair[i]
        clq_now = _cliques_at_distance(objects_by_id, star, features, d)
        now_prev = _prevalent_at(objects_by_id, patterns_all, clq_now, min_prev)
        # Cchanged = prev_prev \ now_prev
        changed = sorted(set(prev_prev) - set(now_prev))
        if changed:
            ColList[Dpair[i-1]].extend(changed)
        prev_prev = now_prev
    return dict(sorted((k, sorted(v)) for k,v in ColList.items()))

def range_inc_mining(objects, d1: float, d2: float, min_prev: float):
    """Incremental over descending D_pair. We reuse cliques and drop those whose diameter > d."""
    star, objects_by_id, features = build_star_neighborhood(objects, d2)
    Dpair = _pair_distances(star, objects_by_id, d1, d2)
    if not Dpair:
        return {}
    ColList = defaultdict(list)
    # compute cliques at first distance (largest)
    cliques_by_pat = _cliques_at_distance(objects_by_id, star, features, Dpair[0])
    patterns_all = sorted(set(list(cliques_by_pat.keys())))
    prev_prev = _prevalent_at(objects_by_id, patterns_all, cliques_by_pat, min_prev)
    for i in range(1, len(Dpair)):
        d = Dpair[i]
        # drop cliques whose diameter > d
        for pat in list(cliques_by_pat.keys()):
            cliques_by_pat[pat] = [(cid, dia) for (cid, dia) in cliques_by_pat[pat] if dia <= d]
        now_prev = _prevalent_at(objects_by_id, patterns_all, cliques_by_pat, min_prev)
        changed = sorted(set(prev_prev) - set(now_prev))
        if changed:
            ColList[Dpair[i-1]].extend(changed)
        prev_prev = now_prev
    return dict(sorted((k, sorted(v)) for k,v in ColList.items()))
