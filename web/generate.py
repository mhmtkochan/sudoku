"""Sudoku generator: 4 levels x 30 puzzles, unique solution, graded by solving technique.

Levels (hardest technique required):
  1 easy      naked / hidden singles
  2 medium    + naked/hidden pairs & triples, pointing / claiming
  3 hard      + X-Wing, Swordfish, XY-Wing
  4 legendary beyond all of the above (needs chains / guessing)
"""
import json
import random
import sys
from itertools import combinations
from multiprocessing import Pool

ROWS = [[r * 9 + c for c in range(9)] for r in range(9)]
COLS = [[r * 9 + c for r in range(9)] for c in range(9)]
BOXES = [[(br * 3 + r) * 9 + bc * 3 + c for r in range(3) for c in range(3)]
         for br in range(3) for bc in range(3)]
UNITS = ROWS + COLS + BOXES
PEERS = []
for i in range(81):
    s = set()
    for u in UNITS:
        if i in u:
            s.update(u)
    s.discard(i)
    PEERS.append(sorted(s))
FULL = 0x1FF
POP = [bin(i).count("1") for i in range(512)]


# ---------------------------------------------------------------- solver (counting)
def count_solutions(grid, limit=2):
    """grid: list of 81 ints (0 empty). Returns number of solutions up to limit."""
    rows = [0] * 9
    cols = [0] * 9
    boxes = [0] * 9
    for i, v in enumerate(grid):
        if v:
            b = 1 << (v - 1)
            r, c = divmod(i, 9)
            if rows[r] & b or cols[c] & b or boxes[r // 3 * 3 + c // 3] & b:
                return 0
            rows[r] |= b
            cols[c] |= b
            boxes[r // 3 * 3 + c // 3] |= b
    g = grid[:]
    found = 0

    def rec():
        nonlocal found
        best = -1
        best_mask = 0
        best_n = 10
        for i in range(81):
            if g[i] == 0:
                r, c = divmod(i, 9)
                m = FULL & ~(rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3])
                n = POP[m]
                if n < best_n:
                    best, best_mask, best_n = i, m, n
                    if n <= 1:
                        break
        if best < 0:
            found += 1
            return
        if best_n == 0:
            return
        r, c = divmod(best, 9)
        bx = r // 3 * 3 + c // 3
        m = best_mask
        while m and found < limit:
            b = m & -m
            m ^= b
            g[best] = b.bit_length()
            rows[r] |= b
            cols[c] |= b
            boxes[bx] |= b
            rec()
            rows[r] &= ~b
            cols[c] &= ~b
            boxes[bx] &= ~b
            g[best] = 0

    rec()
    return found


def random_solution(rng):
    grid = [0] * 81
    rows = [0] * 9
    cols = [0] * 9
    boxes = [0] * 9

    def rec(i):
        if i == 81:
            return True
        r, c = divmod(i, 9)
        bx = r // 3 * 3 + c // 3
        digits = list(range(1, 10))
        rng.shuffle(digits)
        for d in digits:
            b = 1 << (d - 1)
            if rows[r] & b or cols[c] & b or boxes[bx] & b:
                continue
            grid[i] = d
            rows[r] |= b
            cols[c] |= b
            boxes[bx] |= b
            if rec(i + 1):
                return True
            rows[r] &= ~b
            cols[c] &= ~b
            boxes[bx] &= ~b
            grid[i] = 0
        return False

    rec(0)
    return grid


# ---------------------------------------------------------------- logical grader
class Board:
    def __init__(self, grid):
        self.val = [0] * 81
        self.cand = [FULL] * 81
        for i, v in enumerate(grid):
            if v:
                self.place(i, v)

    def place(self, i, d):
        b = 1 << (d - 1)
        self.val[i] = d
        self.cand[i] = 0
        for p in PEERS[i]:
            self.cand[p] &= ~b

    def solved(self):
        return all(self.val)

    # -- level 1
    def singles(self):
        progress = False
        changed = True
        while changed:
            changed = False
            for i in range(81):
                m = self.cand[i]
                if m and POP[m] == 1:
                    self.place(i, m.bit_length())
                    changed = progress = True
            for u in UNITS:
                for d in range(1, 10):
                    b = 1 << (d - 1)
                    spots = [i for i in u if self.cand[i] & b]
                    if len(spots) == 1:
                        self.place(spots[0], d)
                        changed = progress = True
        return progress

    # -- level 2
    def naked_subsets(self):
        for u in UNITS:
            cells = [i for i in u if self.cand[i]]
            for k in (2, 3):
                pool = [i for i in cells if POP[self.cand[i]] <= k]
                for combo in combinations(pool, k):
                    m = 0
                    for i in combo:
                        m |= self.cand[i]
                    if POP[m] != k:
                        continue
                    hit = False
                    for i in cells:
                        if i not in combo and self.cand[i] & m:
                            self.cand[i] &= ~m
                            hit = True
                    if hit:
                        return True
        return False

    def hidden_subsets(self):
        for u in UNITS:
            digs = []
            for d in range(1, 10):
                b = 1 << (d - 1)
                spots = [i for i in u if self.cand[i] & b]
                if spots:
                    digs.append((d, spots))
            for k in (2, 3):
                pool = [(d, s) for d, s in digs if len(s) <= k]
                for combo in combinations(pool, k):
                    cells = set()
                    for _, s in combo:
                        cells.update(s)
                    if len(cells) != k:
                        continue
                    keep = 0
                    for d, _ in combo:
                        keep |= 1 << (d - 1)
                    hit = False
                    for i in cells:
                        if self.cand[i] & ~keep:
                            self.cand[i] &= keep
                            hit = True
                    if hit:
                        return True
        return False

    def intersections(self):
        for d in range(1, 10):
            b = 1 << (d - 1)
            for box in BOXES:
                spots = [i for i in box if self.cand[i] & b]
                if len(spots) < 2:
                    continue
                for line_set in (ROWS, COLS):
                    idx = {(i // 9 if line_set is ROWS else i % 9) for i in spots}
                    if len(idx) == 1:  # pointing
                        line = line_set[idx.pop()]
                        hit = False
                        for i in line:
                            if i not in box and self.cand[i] & b:
                                self.cand[i] &= ~b
                                hit = True
                        if hit:
                            return True
            for line in ROWS + COLS:
                spots = [i for i in line if self.cand[i] & b]
                if len(spots) < 2:
                    continue
                boxes = {(i // 27) * 3 + (i % 9) // 3 for i in spots}
                if len(boxes) == 1:  # claiming
                    box = BOXES[boxes.pop()]
                    hit = False
                    for i in box:
                        if i not in line and self.cand[i] & b:
                            self.cand[i] &= ~b
                            hit = True
                    if hit:
                        return True
        return False

    # -- level 3
    def fish(self):
        for size in (2, 3):
            for d in range(1, 10):
                b = 1 << (d - 1)
                for base_set, cover_set, axis in ((ROWS, COLS, 0), (COLS, ROWS, 1)):
                    lines = []
                    for li, line in enumerate(base_set):
                        spots = [i for i in line if self.cand[i] & b]
                        if 2 <= len(spots) <= size:
                            lines.append((li, spots))
                    for combo in combinations(lines, size):
                        covers = set()
                        for _, spots in combo:
                            for i in spots:
                                covers.add(i % 9 if axis == 0 else i // 9)
                        if len(covers) != size:
                            continue
                        base_idx = {li for li, _ in combo}
                        hit = False
                        for ci in covers:
                            for i in cover_set[ci]:
                                li = i // 9 if axis == 0 else i % 9
                                if li not in base_idx and self.cand[i] & b:
                                    self.cand[i] &= ~b
                                    hit = True
                        if hit:
                            return True
        return False

    def xy_wing(self):
        bivalue = [i for i in range(81) if POP[self.cand[i]] == 2]
        for p in bivalue:
            pm = self.cand[p]
            peers_p = [q for q in PEERS[p] if POP[self.cand[q]] == 2]
            for w1, w2 in combinations(peers_p, 2):
                m1, m2 = self.cand[w1], self.cand[w2]
                if m1 == m2 or m1 == pm or m2 == pm:
                    continue
                if POP[m1 & pm] != 1 or POP[m2 & pm] != 1:
                    continue
                if (m1 & pm) == (m2 & pm):
                    continue
                z = m1 & m2
                if POP[z] != 1 or (z & pm):
                    continue
                hit = False
                for t in PEERS[w1]:
                    if t in PEERS[w2] and t != p and self.cand[t] & z:
                        self.cand[t] &= ~z
                        hit = True
                if hit:
                    return True
        return False


def grade(grid):
    """Return hardest technique level (1-3) needed, or 4 if logic runs dry."""
    bd = Board(grid)
    level = 1
    while not bd.solved():
        if bd.singles():
            continue
        if bd.naked_subsets() or bd.hidden_subsets() or bd.intersections():
            level = max(level, 2)
            continue
        if bd.fish() or bd.xy_wing():
            level = 3
            continue
        return 4
    return level


# ---------------------------------------------------------------- puzzle creation
CLUE_RANGE = {1: (36, 42), 2: (30, 35), 3: (25, 29), 4: (22, 26)}


def make_puzzle(level, rng):
    sol = random_solution(rng)
    lo, hi = CLUE_RANGE[level]
    floor = rng.randint(lo, hi) if level < 4 else 0
    grid = sol[:]
    order = list(range(81))
    rng.shuffle(order)
    clues = 81
    for i in order:
        if clues <= floor:
            break
        keep = grid[i]
        grid[i] = 0
        if count_solutions(grid) != 1 or (level < 4 and grade(grid) > level):
            grid[i] = keep
        else:
            clues -= 1
    if not (lo <= clues <= hi):
        return None
    if grade(grid) != level:
        return None
    return "".join(map(str, grid)), "".join(map(str, sol)), clues


def worker(args):
    level, seed = args
    rng = random.Random(seed)
    while True:
        res = make_puzzle(level, rng)
        if res:
            return level, res


def main():
    per_level = 30
    names = {1: "easy", 2: "medium", 3: "hard", 4: "legendary"}
    out = {names[l]: [] for l in names}
    seen = set()
    jobs = []
    seed = 20261003
    # oversample a little so duplicates (very unlikely) can be dropped
    for l in names:
        for _ in range(per_level + 2):
            seed += 1
            jobs.append((l, seed))
    with Pool() as pool:
        for level, (puz, sol, clues) in pool.imap_unordered(worker, jobs):
            name = names[level]
            if puz in seen or len(out[name]) >= per_level:
                continue
            seen.add(puz)
            out[name].append({"puzzle": puz, "solution": sol, "clues": clues})
            print(name, len(out[name]), clues, file=sys.stderr, flush=True)
    for name, lst in out.items():
        lst.sort(key=lambda p: -p["clues"])
        for n, p in enumerate(lst, 1):
            p["id"] = f"{name}-{n:02d}"
    with open("sudoku_puzzles.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
