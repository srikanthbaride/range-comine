
from typing import List, Dict, Tuple, Iterable, Set
from collections import defaultdict
import itertools, math
from .neighbors import build_star_neighborhood

# Helpers
def pattern_features(pattern: Tuple[str,...]) -> Tuple[str,...]:
    return tuple(sorted(pattern))

def candidate_join(prev: List[Tuple[str,...]]) -> List[Tuple[str,...]]:
    """Apriori candidate generation from prevalent (k-1)-patterns"""
    prev_sorted = [tuple(sorted(p)) for p in prev]
    prev_sorted = sorted(set(prev_sorted))
    k = len(prev_sorted[0]) + 1 if prev_sorted else 1
    C = set()
    for i in range(len(prev_sorted)):
        for j in range(i+1, len(prev_sorted)):
            p, q = prev_sorted[i], prev_sorted[j]
            if p[:-1] == q[:-1]:
                cand = tuple(sorted(set(p) | set(q)))
                if len(cand) == k:
                    # prune: all (k-1)-subsets must be in prev
                    ok = True
                    for sub in itertools.combinations(cand, k-1):
                        if tuple(sorted(sub)) not in prev_sorted:
                            ok = False; break
                    if ok:
                        C.add(cand)
    return sorted(C)

def clique_diameter(clique_obj_ids: Tuple[str,...], objects_by_id: Dict[str, tuple]) -> float:
    oids = list(clique_obj_ids)
    maxd = 0.0
    for i in range(len(oids)):
        for j in range(i+1, len(oids)):
            oi, oj = objects_by_id[oids[i]], objects_by_id[oids[j]]
            d = math.hypot(oi[2]-oj[2], oi[3]-oj[3])
            if d > maxd:
                maxd = d
    return maxd

def enumerate_size2_cliques(features: Tuple[str,str], star: Dict[str, list], objects_by_id: Dict[str, tuple], dmax: float):
    f1, f2 = features
    # build all pairs (o_i in f1, o_j in f2) such that both within dmax (already guaranteed by star)
    cliques = []
    # To avoid duplicates, enforce an order on object ids tuple
    for center, neighs in star.items():
        cfeat = objects_by_id[center][1]
        # only consider centers of one of the features
        if cfeat not in (f1, f2): 
            continue
        # neighbors that have the other feature
        for (nid, nfeat, dist) in neighs:
            if nfeat not in (f1, f2): 
                continue
            if nfeat == cfeat: 
                continue
            # pair
            a, b = sorted((center, nid))
            dia = dist  # for 2-size, diameter = pair distance
            cliques.append(((a,b), dia))
    # deduplicate pairs
    seen = set()
    uniq = []
    for cid, dia in cliques:
        if cid not in seen:
            seen.add(cid)
            uniq.append((cid, dia))
    return uniq

def filter_k_cliques(cand: Tuple[str,...], star: Dict[str, list], objects_by_id: Dict[str, tuple], dmax: float):
    """
    Build clique instances for k>=3 by joining size-2 edges implicitly.
    Naive approach: generate all combinations of objects where each feature appears exactly once,
    and keep those whose pairwise distances <= dmax.
    This is exponential; suitable for small demos.
    """
    # gather object ids by feature
    by_feat = defaultdict(list)
    for oid, obj in objects_by_id.items():
        if obj[1] in cand:
            by_feat[obj[1]].append(oid)
    # ordered feature list for consistent product
    feats = list(cand)
    lists = [by_feat[f] for f in feats]
    cliques = []
    for combo in itertools.product(*lists):
        # ensure exactly one per feature; product already guarantees that
        # check pairwise distances
        ok = True
        for i in range(len(combo)):
            oi = objects_by_id[combo[i]]
            for j in range(i+1, len(combo)):
                oj = objects_by_id[combo[j]]
                d = math.hypot(oi[2]-oj[2], oi[3]-oj[3])
                if d > dmax:
                    ok = False; break
            if not ok:
                break
        if ok:
            cid = tuple(sorted(combo))
            dia = 0.0
            # find diameter
            for i in range(len(combo)):
                oi = objects_by_id[combo[i]]
                for j in range(i+1, len(combo)):
                    oj = objects_by_id[combo[j]]
                    dd = math.hypot(oi[2]-oj[2], oi[3]-oj[3])
                    if dd > dia: dia = dd
            cliques.append((cid, dia))
    # deduplicate
    uniq = {}
    for cid, dia in cliques:
        if (cid not in uniq) or (dia < uniq[cid]):
            uniq[cid] = dia
    return [(cid, uniq[cid]) for cid in uniq.keys()]

def _critical_distance_from_cliques(cliques, objects_by_id, min_prev, d1):
    """Three-step method: map -> cumulative union -> PI per candidate distance -> smallest d >= d1 with PI>=min_prev"""
    if not cliques:
        return None
    # 1) map from diameter to per-feature object sets
    # collect features in pattern
    features = set(objects_by_id[oid][1] for cid,_ in cliques for oid in cid)
    diameters = sorted({dia for _, dia in cliques})
    per_d_feat_objs = {d: {f:set() for f in features} for d in diameters}
    for cid, dia in cliques:
        for oid in cid:
            f = objects_by_id[oid][1]
            per_d_feat_objs[dia][f].add(oid)
    # 2) cumulative union from smallest to largest diameter
    cum = {}
    running = {f:set() for f in features}
    for d in diameters:
        for f in features:
            running[f] = set(running[f]) | per_d_feat_objs[d][f]
        cum[d] = {f:set(running[f]) for f in features}
    # 3) compute PI at each candidate distance and pick smallest >= d1 that meets threshold
    # total instances per feature
    total_by_feat = {}
    for oid, obj in objects_by_id.items():
        f = obj[1]
        if f in features:
            total_by_feat[f] = total_by_feat.get(f, 0) + 1
    best = None
    for d in diameters:
        if d < d1: 
            continue
        pis = []
        for f in features:
            num = len(cum[d][f])
            den = total_by_feat[f]
            pis.append(num/den if den else 0.0)
        pi = min(pis) if pis else 0.0
        if pi >= min_prev:
            best = d
            break
    return best

def range_comine(objects, d1: float, d2: float, min_prev: float):
    """Single-pass Range–CoMine (demo-scale). Returns ColList: dict critical_distance -> [patterns].
    objects: list of (id, feature, x, y)
    """
    star, objects_by_id, features = build_star_neighborhood(objects, d2)
    # size-1 are always prevalent; critical distance = d1
    P_prev = [(f,) for f in features]
    ColList = defaultdict(list)
    for f in features:
        ColList[d1].append((f,))
    # k=2: enumerate cliques directly from star
    # then iteratively grow
    k = 2
    # track critical distances for CDMP pruning
    critical = { (f,): d1 for f in features }
    while P_prev:
        # candidates
        Ck = candidate_join(P_prev) if k>2 else [
            tuple(sorted(pair)) for pair in itertools.combinations(features, 2)
        ]
        Pk = []
        for cand in Ck:
            # build clique instances at d2
            if k == 2:
                cliques = enumerate_size2_cliques(cand, star, objects_by_id, d2)
            else:
                # coarse pruning by CDMP: require diameter >= max critical of subpatterns
                subs = [tuple(sorted(sub)) for sub in itertools.combinations(cand, k-1)]
                min_allowed = max(critical[s] for s in subs if s in critical)
                cliques_all = filter_k_cliques(cand, star, objects_by_id, d2)
                cliques = [(cid, dia) for (cid, dia) in cliques_all if dia >= min_allowed]
            # check prevalence at d2
            # compute PI at d2 using distinct object counts per feature at d2
            # fast path: build sets per feature from cliques
            if not cliques:
                continue
            feats = set(cand)
            total_by_feat = {f:0 for f in feats}
            for oid,obj in objects_by_id.items():
                if obj[1] in feats:
                    total_by_feat[obj[1]] += 1
            seen_by_feat = {f:set() for f in feats}
            for cid,_ in cliques:
                for oid in cid:
                    seen_by_feat[objects_by_id[oid][1]].add(oid)
            pi = min(len(seen_by_feat[f])/total_by_feat[f] for f in feats)
            if pi < min_prev:
                continue
            # compute critical distance
            cr = _critical_distance_from_cliques(cliques, objects_by_id, min_prev, d1)
            if cr is None:
                continue
            Pk.append(cand)
            critical[cand] = cr
            ColList[cr].append(cand)
        P_prev = Pk
        k += 1
    # sort ColList keys
    return dict(sorted((d, sorted(v)) for d,v in ColList.items()))
