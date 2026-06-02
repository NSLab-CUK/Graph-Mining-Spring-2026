"""Write a smaller subset for quick notebook runs."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "ht2009_contact_list.dat"
OUT = ROOT / "ht2009_contact_list_small.dat"
MAX_ROWS = 6000

def main():
    rows = []
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) >= 3:
                rows.append(f"{p[0]}\t{p[1]}\t{p[2]}\n")
            if len(rows) >= MAX_ROWS:
                break
    OUT.write_text("".join(rows), encoding="utf-8")
    print(f"Wrote {OUT} ({len(rows)} events)")

if __name__ == "__main__":
    main()