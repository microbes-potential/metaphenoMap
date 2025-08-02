#!/usr/bin/env python3
import argparse, subprocess, time, csv, sys
from pathlib import Path

def run_batch(project_root, db, module, input_file, out_csv):
    cmd = [sys.executable, str(Path(project_root)/"metaphenomap.py"),
           "--db", db, "--module", module, "-i", input_file, "-o", out_csv]
    t0 = time.perf_counter()
    subprocess.run(cmd, cwd=project_root)
    t1 = time.perf_counter()
    return t1 - t0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--sizes", type=str, default="100,1000,10000")
    ap.add_argument("--db", default="ncbi")
    ap.add_argument("--module", default="sample")
    ap.add_argument("--prefix", default="bench")
    ap.add_argument("--summary", default="throughput_summary.csv")
    args = ap.parse_args()

    sizes = [int(x) for x in args.sizes.split(",")]
    rows = []
    for n in sizes:
        infile = f"{args.prefix}_{n}.txt"
        outfile = f"{args.prefix}_out_{n}.csv"
        elapsed = run_batch(args.project_root, args.db, args.module, infile, outfile)
        rows.append({"n": n, "elapsed_sec": elapsed, "records_per_sec": n/elapsed if elapsed>0 else 0})

    with open(args.summary, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["n","elapsed_sec","records_per_sec"])
        w.writeheader(); w.writerows(rows)
    print(f"[✓] Wrote {args.summary}")

if __name__ == "__main__":
    main()
