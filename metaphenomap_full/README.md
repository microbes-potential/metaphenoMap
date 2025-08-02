# MetaPhenoMap — Final Full Package

## One-time installation
```bash
cd metaphenomap_full
conda env create -f environment.yml
conda activate metaphenomap-env
make install
```

## Run (project root!)
```bash
# Mixed file, auto-detect db/module, download FASTQs, verify, zip-all
python metaphenomap.py --auto-db -i data/test_accessions.txt -o out_auto.csv --download fastq --verify --max-workers 6 --outdir downloads --zip-all --verbose

# Single assembly with artifacts + zip
python metaphenomap.py --db ncbi --module assembly -a GCF_000146045.2 -o out_asm.csv --download assembly --outdir downloads --zip-output --verbose

# SRA run → FASTQ
python metaphenomap.py --db sra --module sample -a SRR390728 -o out_sra.csv --download fastq --outdir downloads --zip-output --verbose

# PATRIC genome metadata
python metaphenomap.py --db patric --module both -a 511145.183 -o out_patric.csv --verbose
```

## Common pitfalls
- **Run from the project root** (the folder that contains `metaphenomap.py`), not from `downloads/`.
- If you get “file not found: metaphenomap.py”, do:
  ```bash
  cd /path/to/metaphenomap_full
  python metaphenomap.py --help
  ```
- Use absolute paths when in doubt.
