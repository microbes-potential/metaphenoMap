#!/usr/bin/env python3
import argparse, pandas as pd
import matplotlib.pyplot as plt

def plot_speed(summary_csv, out_png="speed.png"):
    df = pd.read_csv(summary_csv)
    plt.figure()
    labels = [f"{t}-{m}" for t,m in zip(df["tool"], df["mode"])]
    plt.bar(labels, df["elapsed_sec"])
    plt.ylabel("Seconds (lower is better)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout(); plt.savefig(out_png); print(f"[✓] {out_png}")

def plot_throughput(summary_csv, out_png="throughput.png"):
    df = pd.read_csv(summary_csv)
    plt.figure()
    plt.plot(df["n"], df["records_per_sec"], marker="o")
    plt.xlabel("Records"); plt.ylabel("Records/sec (higher is better)")
    plt.tight_layout(); plt.savefig(out_png); print(f"[✓] {out_png}")

def plot_human(summary_csv, out_png="human_effort.png"):
    df = pd.read_csv(summary_csv)
    plt.figure()
    vals = [float(df["manual_min"][0]), float(df["mpm_min"][0])]
    plt.bar(["Manual","MetaPhenoMap"], vals)
    plt.ylabel("Minutes (lower is better)")
    plt.tight_layout(); plt.savefig(out_png); print(f"[✓] {out_png}")

def plot_completeness(summary_csv, out_png="completeness.png"):
    df = pd.read_csv(summary_csv)
    plt.figure()
    plt.bar(df["tool"], df["completeness"])
    plt.ylabel("Fraction of key fields present")
    plt.ylim(0,1)
    plt.tight_layout(); plt.savefig(out_png); print(f"[✓] {out_png}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--speed"); ap.add_argument("--throughput")
    ap.add_argument("--human"); ap.add_argument("--completeness")
    args = ap.parse_args()
    if args.speed: plot_speed(args.speed)
    if args.throughput: plot_throughput(args.throughput)
    if args.human: plot_human(args.human)
    if args.completeness: plot_completeness(args.completeness)
