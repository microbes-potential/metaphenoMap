#!/usr/bin/env python3
"""
Compute completeness (fraction of filled key fields) for MetaPhenoMap vs baselines.
Baselines assumed to be CSVs you prepare separately (e.g., from EDirect or MetaSRA).
"""
import argparse, csv, pandas as pd

KEY_FIELDS = ["Host","Isolation_Source","Disease","Location","Collection_Date"]

def frac_filled(df):
    if df.empty: return 0.0
    present = df[KEY_FIELDS].notna().sum().sum()  # total filled cells
    total = len(df) * len(KEY_FIELDS)
    return present / total if total else 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mpm_csv", required=True)
    ap.add_argument("--edirect_csv")
    ap.add_argument("--metasra_csv")
    ap.add_argument("--summary", default="completeness_summary.csv")
    args = ap.parse_args()

    rows = []
    mpm = pd.read_csv(args.mpm_csv)
    rows.append({"tool":"MetaPhenoMap","completeness": round(frac_filled(mpm), 4)})

    if args.edirect_csv:
        ed = pd.read_csv(args.edirect_csv)
        rows.append({"tool":"EDirect","completeness": round(frac_filled(ed), 4)})
    if args.metasra_csv:
        ms = pd.read_csv(args.metasra_csv)
        rows.append({"tool":"MetaSRA","completeness": round(frac_filled(ms), 4)})

    with open(args.summary, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tool","completeness"])
        w.writeheader(); w.writerows(rows)
    print(f"[✓] Wrote {args.summary}")

if __name__ == "__main__":
    main()
