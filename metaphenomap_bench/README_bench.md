# Benchmarking Suite for MetaPhenoMap

## Files
- `speed_bench.py` — end-to-end download speed comparisons.
- `throughput_bench.py` — records/sec for metadata fetches.
- `human_effort_bench.py` — manual vs automated time estimate.
- `completeness_bench.py` — fraction of key fields present per tool.
- `plots.py` — quick matplotlib visualizations.

## Usage
1) Ensure `metaphenomap.py` is installed and accessible in a project folder.
2) Prepare input accession lists (especially SRR/ERR/DRR for speed tests).

### Speed test (FASTQ downloads)
```bash
python speed_bench.py --project-root /PATH/TO/metaphenomap_full   --input /PATH/TO/metaphenomap_full/data/test_accessions.txt   --outdir ./bench_downloads --summary speed_summary.csv --runs 5
```

### Throughput test (metadata only)
- Create bench_100.txt, bench_1000.txt, bench_10000.txt (one accession per line)
```bash
python throughput_bench.py --project-root /PATH/TO/metaphenomap_full   --sizes 100,1000 --db ncbi --module sample --prefix bench --summary throughput_summary.csv
```

### Human effort estimate
```bash
python human_effort_bench.py --samples 1000 --manual_sec_per_sample 20 --mpm_elapsed_sec 32 --summary human_effort_summary.csv
```

### Completeness test
```bash
python completeness_bench.py --mpm_csv out_auto.csv --edirect_csv edirect.csv --metasra_csv metasra.csv --summary completeness_summary.csv
```

### Plotting
```bash
python plots.py --speed speed_summary.csv
python plots.py --throughput throughput_summary.csv
python plots.py --human human_effort_summary.csv
python plots.py --completeness completeness_summary.csv
```
