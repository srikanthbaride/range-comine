
from range_comine.synthetic import generate_synthetic
from range_comine.mining import range_comine

def test_smoke():
    objs = generate_synthetic(n_features=3, instances_per_feat=3, seed=7)
    res = range_comine(objs, d1=5.0, d2=40.0, min_prev=0.3)
    assert isinstance(res, dict)
    # should at least register size-1 patterns at d1
    assert 5.0 in res
