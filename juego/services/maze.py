"""Generación de caminos simples en un grafo ortogonal de 25 celdas."""

import random


def neighbors(n):
    r, c = divmod(n, 5)
    return [
        rr * 5 + cc
        for rr, cc in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]
        if 0 <= rr < 5 and 0 <= cc < 5
    ]


def paths(safe, goal, limit=3):
    found = []

    def visit(node, path):
        if len(found) >= limit:
            return
        if node == goal:
            found.append(path)
            return
        for nxt in neighbors(node):
            if nxt in safe and nxt not in path:
                visit(nxt, path + [nxt])

    visit(0, [0])
    return found


def generate(code, rng=None, route_count=None):
    rng = rng or random.SystemRandom()
    count = route_count if route_count is not None else (1 if code == "OMEGA" else 2)
    minimum, maximum = {"ALFA": (6, 10), "BETA": (8, 13), "OMEGA": (10, 17)}[code]
    for _ in range(6000):
        path = [0]
        target = rng.randint(minimum + 1, maximum)
        while len(path) < target:
            candidates = [
                n
                for n in neighbors(path[-1])
                if n not in path and sum(v in path for v in neighbors(n)) == 1
            ]
            if not candidates:
                break
            path.append(rng.choice(candidates))
        if len(path) < minimum + 1:
            continue
        safe = set(path)
        goal = path[-1]
        if count == 2:
            candidates = [
                n
                for n in range(1, 25)
                if n not in safe and sum(v in safe for v in neighbors(n)) == 2
            ]
            rng.shuffle(candidates)
            valid = False
            for n in candidates:
                trial = safe | {n}
                routes = paths(trial, goal)
                if len(routes) == 2 and min(map(len, routes)) >= minimum + 1:
                    safe = trial
                    valid = True
                    break
            if not valid:
                continue
        routes = paths(safe, goal)
        if len(routes) == count:
            return {"safe": sorted(safe), "goal": goal, "routes": routes, "start": 0}
    raise RuntimeError("No se pudo generar un tablero válido; vuelve a intentar.")


def label(n):
    r, c = divmod(n, 5)
    return f"{chr(65 + r)}{c + 1}"


def crash_path(board, position):
    """Desvío ortogonal hasta el virus más cercano; no teletransporta al personaje."""
    from collections import deque

    safe = set(board["safe"])
    queue = deque([[position]])
    visited = {position}
    while queue:
        path = queue.popleft()
        for nxt in neighbors(path[-1]):
            if nxt not in safe:
                return path + [nxt]
            if nxt not in visited:
                visited.add(nxt)
                queue.append(path + [nxt])
    raise ValueError("El tablero debe contener virus.")
