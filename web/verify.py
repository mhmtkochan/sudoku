import json
import sys
from generate import count_solutions, grade, UNITS

path = sys.argv[1] if len(sys.argv) > 1 else "sudoku_puzzles.json"
data = json.load(open(path, encoding="utf-8"))
levels = {"easy": 1, "medium": 2, "hard": 3, "legendary": 4}
allp = set()
ok = True
for name, lst in data.items():
    clues = [p["clues"] for p in lst]
    print(f"{name:10} count={len(lst)} clues={min(clues)}-{max(clues)}")
    if len(lst) != 30:
        ok = False
        print("  !! count != 30")
    for p in lst:
        g = [int(c) for c in p["puzzle"]]
        s = [int(c) for c in p["solution"]]
        errs = []
        if len(g) != 81 or len(s) != 81:
            errs.append("length")
        if sum(1 for v in g if v) != p["clues"]:
            errs.append("clue count")
        if any(a and a != b for a, b in zip(g, s)):
            errs.append("givens differ from solution")
        if any(sorted(s[i] for i in u) != list(range(1, 10)) for u in UNITS):
            errs.append("invalid solution")
        if count_solutions(g) != 1:
            errs.append("not unique")
        if grade(g) != levels[name]:
            errs.append("grade mismatch")
        if p["puzzle"] in allp:
            errs.append("duplicate")
        allp.add(p["puzzle"])
        if errs:
            ok = False
            print("  !!", p["id"], errs)
print("ALL OK" if ok and len(allp) == 120 else "PROBLEMS FOUND")
