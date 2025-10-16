
from typing import List, Dict, Tuple

# Object record: (id, feature, x, y)
Obj = Tuple[str, str, float, float]

def load_objects_csv(path: str) -> List[Obj]:
    """Load spatial objects from a CSV with header: id,feature,x,y"""
    out: List[Obj] = []
    import csv
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append((row['id'], row['feature'], float(row['x']), float(row['y'])))
    return out
