from collections import Counter
import hashlib, math, random
from typing import Dict, Any, List, Tuple

THEMES = [
    "oil painting",
    "watercolor",
    "neon cyberpunk",
    "ghibli",
    "vaporwave",
    "pixel art",
    "low-poly 3d",
    "origami paper",
    "charcoal sketch",
    "ink wash",
    "stained glass",
    "clay stop-motion",
    "ukiyo-e",
    "synthwave",
    "bauhaus minimal",
    "steampunk",
]
_theme_aliases = {t.lower(): t for t in THEMES}

def normalize_theme(name: str) -> str:
    if not name:
        return "oil painting"
    return _theme_aliases.get(name.strip().lower(), "oil painting")

GenreBuckets = {
  "dream pop": "dream-pop",
  "shoegaze": "dream-pop",
  "indie rock": "indie",
  "folk": "indie",
  "house": "electronic",
  "techno": "electronic",
  "classical": "classical",
  "jazz": "jazz",
  "metal": "metal",
}

PALETTES = {
  "dream-pop": ["#f8e1f4", "#c9d6ff", "#b8c6db", "#fdfbfb"],
  "electronic": ["#0d0d0d", "#2a2a72", "#009ffd", "#2a9d8f"],
  "indie": ["#264653", "#e9c46a", "#2a9d8f", "#f4a261"],
  "classical": ["#eae2b7", "#003049", "#d62828", "#f77f00"],
  "jazz": ["#001219", "#005f73", "#0a9396", "#94d2bd"],
  "metal": ["#111", "#444", "#ddd", "#e63946"],
  "default": ["#101010", "#444", "#999", "#f1faee"],
}

def stable_seed(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)

def bucket_genres(genres: List[str]) -> List[str]:
    out = []
    for g in genres:
        out.append(GenreBuckets.get(g.lower(), g.lower()))
    return out

def entropy(counts: List[int]) -> float:
    total = sum(counts) or 1
    H = 0.0
    for c in counts:
        if c:
            p = c/total
            H -= p * math.log(p + 1e-12, 2)
    return min(1.0, H/5)

def build_taste_vector(artists: List[Dict[str,Any]], tracks: List[Dict[str,Any]]):
    all_genres = []
    for a in artists:
        all_genres.extend(a.get("genres", []))
    binned = bucket_genres(all_genres)
    genre_counts = Counter(binned)
    pops = []
    for a in artists:
        if isinstance(a.get("popularity"), int):
            pops.append(a["popularity"])
    for t in tracks:
        if isinstance(t.get("popularity"), int):
            pops.append(t["popularity"])
    popularity_avg = sum(pops)/len(pops) if pops else 50

    eras = Counter(); explicit = 0; durs = []
    for t in tracks:
        if t.get("explicit"): explicit += 1
        if t.get("duration_ms"): durs.append(t["duration_ms"]) 
        year = (t.get("album", {}).get("release_date", "")[:4])
        if year and year.isdigit():
            eras[year[:3] + "0s"] += 1

    explicit_ratio = (explicit/len(tracks)) if tracks else 0
    dur_mean = sum(durs)/len(durs) if durs else 180000
    dur_std = (sum((x-dur_mean)**2 for x in durs)/len(durs))**0.5 if durs else 0

    return {
        "genreCounts": dict(genre_counts),
        "popularityAvg": popularity_avg,
        "explicitRatio": explicit_ratio,
        "durationsMs": {"mean": dur_mean, "std": dur_std},
        "eras": dict(eras),
    }

def _weighted_choice(counts: Dict[str, int]) -> str:
    items = list(counts.items())
    if not items:
        return "abstract"
    total = sum(c for _, c in items) or 1
    r, acc = random.uniform(0, total), 0
    for k, c in items:
        acc += c
        if r <= acc:
            return k
    return items[-1][0]

def popularity_word(popularity_avg: float, mainstream_threshold: int = 60) -> str:
    return "mainstream" if popularity_avg >= mainstream_threshold else "indie"

def three_words(taste: Dict[str, Any]) -> Tuple[str, str, str]:
    genres: Dict[str, int] = taste.get("genreCounts", {})
    eras: Dict[str, int] = taste.get("eras", {})
    genre = _weighted_choice(genres).replace("-", " ") if genres else "abstract"
    era = _weighted_choice(eras) if eras else "2000s"
    pop = popularity_word(float(taste.get("popularityAvg", 50)))
    return genre, pop, era

def pick_palette(top_genre: str, era: str|None) -> list:
    return PALETTES.get(top_genre, PALETTES["default"])

def map_to_visuals(taste: Dict[str,Any], user_id: str) -> Dict[str,Any]:
    genres = taste.get("genreCounts", {})
    top_genre = max(genres, key=genres.get) if genres else "default"
    era = max(taste.get("eras", {"2000s":1}), key=taste.get("eras", {"2000s":1}).get)

    seed = f"{user_id}|{top_genre}|{era}"
    rnd = random.Random(stable_seed(seed))

    density = 0.2 + (100 - taste.get("popularityAvg",50))/100 * 0.8
    density = max(0.2, min(1.0, density))
    H = entropy(list(genres.values()))
    symmetry = max(0, min(1, 1 - H))

    return {
        "seed": seed,
        "palette": pick_palette(top_genre, era),
        "density": density,
        "blur": min(0.7, 0.1 + taste.get("explicitRatio",0)*0.5),
        "motion": rnd.uniform(0.3, 1.0),
        "geometryBias": rnd.choice(["lines","blobs","polys","nebula"]),
        "symmetry": symmetry,
        "noiseScale": rnd.uniform(0.2, 0.8),
    }