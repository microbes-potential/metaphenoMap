#!/usr/bin/env python3
"""
Estimate human effort vs. MetaPhenoMap.
"""
import argparse, csv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=1000)
    ap.add_argument("--manual_sec_per_sample", type=float, default=20.0)
    ap.add_argument("--mpm_elapsed_sec", type=float, default=32.0)
    ap.add_argument("--summary", default="human_effort_summary.csv")
    args = ap.parse_args()

    manual_total_min = (args.samples * args.manual_sec_per_sample) / 60.0
    mpm_total_min = args.mpm_elapsed_sec / 60.0

    with open(args.summary, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["samples","manual_min","mpm_min","speedup_x"])
        w.writeheader()
        w.writerow({"samples": args.samples,
                    "manual_min": round(manual_total_min,2),
                    "mpm_min": round(mpm_total_min,2),
                    "speedup_x": round(manual_total_min / mpm_total_min if mpm_total_min>0 else 0, 2)})
    print(f"[✓] Wrote {args.summary}")

if __name__ == "__main__":
    main()
