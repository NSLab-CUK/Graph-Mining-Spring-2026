"""Build a small DBLP-style author collaboration dataset for TIMERS practice."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

RNG = np.random.default_rng(42)

# DBLP-inspired research communities (synthetic author names)
COMMUNITIES = {
    "database": [
        "Michael Stonebraker", "Hector Garcia-Molina", "Raghu Ramakrishnan",
        "Surajit Chaudhuri", "AnHai Doan", "Alon Halevy", "Jennifer Widom",
        "Dan Suciu", "Christopher Ré", "Neoklis Polyzotis",
    ],
    "data_mining": [
        "Jiawei Han", "Jian Pei", "Philip S. Yu", "Christos Faloutsos",
        "Charu C. Aggarwal", "Hanghang Tong", "Jingrui He", "Peng Cui",
        "Ziwei Zhang", "Wenwu Zhu",
    ],
    "ml_theory": [
        "Geoffrey Hinton", "Yann LeCun", "Yoshua Bengio", "Andrew Ng",
        "Michael I. Jordan", "Stuart Russell", "Peter Norvig", "Tom Mitchell",
        "Leslie Valiant", "Percy Liang",
    ],
    "systems": [
        "Jeffrey Dean", "Sanjay Ghemawat", "Luiz André Barroso",
        "Ion Stoica", "Matei Zaharia", "Scott Shenker", "David Patterson",
        "John Ousterhout", "Remzi Arpaci-Dusseau", "Andrea Arpaci-Dusseau",
    ],
    "nlp": [
        "Christopher Manning", "Dan Klein", "Percy Liang", "Noah Smith",
        "Yoav Goldberg", "Mihai Surdeanu", "Dan Jurafsky", "Regina Barzilay",
        "Kyunghyun Cho", "Emily M. Bender",
    ],
    "vision": [
        "Fei-Fei Li", "Jitendra Malik", "Trevor Darrell", "Ross Girshick",
        "Kaiming He", "Alex Krizhevsky", "Andrew Zisserman", "Antonio Torralba",
        "Li Fei-Fei", "Devi Parikh",
    ],
}

# Cross-community bridges (famous collaborations)
BRIDGE_PAIRS = [
    ("Jiawei Han", "Christopher Ré"),
    ("Philip S. Yu", "Jian Pei"),
    ("Peng Cui", "Ziwei Zhang"),
    ("Hanghang Tong", "Jiawei Han"),
    ("Jeffrey Dean", "Andrew Ng"),
    ("Matei Zaharia", "Jeffrey Dean"),
    ("Christopher Manning", "Percy Liang"),
    ("Fei-Fei Li", "Jitendra Malik"),
    ("Michael Stonebraker", "Jennifer Widom"),
    ("Dan Suciu", "Christopher Ré"),
]


def _unique_authors() -> list[str]:
    seen: set[str] = set()
    authors: list[str] = []
    for names in COMMUNITIES.values():
        for name in names:
            if name not in seen:
                seen.add(name)
                authors.append(name)
    return authors


def _author_index(authors: list[str]) -> dict[str, int]:
    return {name: i for i, name in enumerate(authors)}


def _community_edges(authors: list[str], idx: dict[str, int], p_intra: float) -> list[tuple[int, int, int]]:
    """Return (u, v, year) collaboration edges inside communities."""
    edges: list[tuple[int, int, int]] = []
    for comm, names in COMMUNITIES.items():
        ids = [idx[n] for n in names if n in idx]
        base_year = {"database": 1998, "data_mining": 2004, "ml_theory": 2006,
                     "systems": 2003, "nlp": 2008, "vision": 2009}[comm]
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                if RNG.random() < p_intra:
                    year = int(base_year + RNG.integers(0, 8))
                    u, v = sorted((ids[i], ids[j]))
                    edges.append((u, v, year))
    return edges


def build(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    authors = _unique_authors()
    n = len(authors)
    idx = _author_index(authors)

    all_edges = _community_edges(authors, idx, p_intra=0.55)
    for a, b in BRIDGE_PAIRS:
        if a in idx and b in idx:
            u, v = sorted((idx[a], idx[b]))
            all_edges.append((u, v, int(RNG.integers(2010, 2016))))

    # Deduplicate undirected edges, keep earliest year
    edge_map: dict[tuple[int, int], int] = {}
    for u, v, year in all_edges:
        key = (u, v)
        edge_map[key] = min(edge_map.get(key, year), year)

    ordered = sorted(edge_map.items(), key=lambda x: (x[1], x[0]))
    static_cut = int(0.35 * len(ordered))
    static_edges = ordered[:static_cut]
    dynamic_edges = ordered[static_cut:]

    with (output_dir / "authors.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["author_id", "name"])
        for i, name in enumerate(authors):
            w.writerow([i, name])

    with (output_dir / "edges_static.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["u", "v", "year"])
        for (u, v), year in static_edges:
            w.writerow([u, v, year])

    with (output_dir / "edges_dynamic.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["u", "v", "year"])
        for (u, v), year in dynamic_edges:
            w.writerow([u, v, year])

    with (output_dir / "README.txt").open("w", encoding="utf-8") as f:
        f.write(
            "DBLP-mini: synthetic author collaboration network inspired by DBLP.\n"
            f"Nodes: {n} authors | Static edges: {len(static_edges)} | "
            f"Dynamic edges: {len(dynamic_edges)}\n"
            "Similarity matrix S equals adjacency A (as in the reference TIMERS code).\n"
        )

    print(f"Wrote {output_dir}: {n} authors, {len(static_edges)} static, {len(dynamic_edges)} dynamic edges")


if __name__ == "__main__":
    build(Path(__file__).resolve().parent)