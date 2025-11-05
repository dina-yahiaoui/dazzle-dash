# utils/loaders.py
from pathlib import Path
import pandas as pd
from functools import lru_cache

DATA_WHO_RAW = Path("data/raw/Life Expectancy Data.csv")

def _read_auto(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = df.columns.str.strip()
    return df

@lru_cache(maxsize=8)
def get_who() -> pd.DataFrame:
    print("[WHO] Lecture :", DATA_WHO_RAW.resolve())
    if not DATA_WHO_RAW.exists():
        print("[WHO] Fichier introuvable")
        return pd.DataFrame(columns=["Country", "Year", "Status", "Life expectancy"])
    df = _read_auto(DATA_WHO_RAW)

    # Normalise "Life expectancy" si l'intitulé varie
    if "Life expectancy" not in df.columns:
        for c in df.columns:
            if c.strip().lower() == "life expectancy":
                df = df.rename(columns={c: "Life expectancy"})
                break

    keep = [c for c in ["Country", "Year", "Status", "Life expectancy"] if c in df.columns]
    df = df[keep].copy()
    if "Year" in df: df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    if "Life expectancy" in df: df["Life expectancy"] = pd.to_numeric(df["Life expectancy"], errors="coerce")
    df = df.dropna(subset=[c for c in ["Country","Year","Life expectancy"] if c in df.columns])
    if "Year" in df: df["Year"] = df["Year"].astype(int)

    print("[WHO] Colonnes :", list(df.columns))
    print("[WHO] Shape    :", df.shape)
    return df

# Placeholders pour éviter que Food/Flights plantent
def get_food(): return pd.DataFrame()
def get_flights(): return pd.DataFrame()
