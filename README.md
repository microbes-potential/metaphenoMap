# 🧬 MetaPhenoMap

A **unified command-line tool** for mining phenotype-linked metadata from public genomic repositories.

> Supports accessions from **NCBI**, **SRA**, and **PATRIC** with:
> - ✅ Auto-detection of input type (BioSample, SRA, GCF, PATRIC)
> - 📥 FASTQ/assembly downloads (multithreaded)
> - 🧠 Metadata parsing & verification
> - 📊 Unified CSV output and ZIP packaging

---

## 📸 Demo Screenshot

<img src="assets/demo_example.png" width="90%">

---

## 📦 Installation

### 1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
```bash
# Linux/macOS
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

---

### 2. Clone MetaPhenoMap and install
```bash
git clone https://github.com/yourusername/metaphenomap.git
cd metaphenomap_full

# Create conda environment
conda env create -f environment.yml
conda activate metaphenomap-env

# Install via Makefile
make install
```

---

## 🚀 Quick Start

```bash
python metaphenomap.py --auto-db   -i data/test_accessions.txt   -o out.csv   --download fastq   --verify   --max-workers 6   --outdir downloads   --zip-all   --verbose
```

---

## 📘 Available Modules

| Module     | Description                         |
|------------|-------------------------------------|
| `sample`   | SRA metadata & FASTQ download       |
| `assembly` | NCBI/RefSeq GCF metadata            |
| `both`     | PATRIC genomes and metadata         |

---

## ⚙️ Full CLI Reference

```bash
python metaphenomap.py --help
```

### 🔹 Main Flags

| Flag | Description |
|------|-------------|
| `--db`             | Database: `ncbi`, `sra`, `patric` |
| `--module`         | Module type: `sample`, `assembly`, `both` |
| `--auto-db`        | Detect module/database automatically |
| `-i`, `--input`    | Text file with accession list |
| `-a`, `--accession`| Single accession input |
| `-o`, `--output`   | Output CSV file path |
| `--download`       | Type: `fastq`, `assembly`, or `none` |
| `--outdir`         | Download output directory |
| `--zip-output`     | Compress single output |
| `--zip-all`        | Compress all artifacts |
| `--verify`         | Check accession status |
| `--max-workers`    | Parallel threads |
| `--verbose`        | Enable debug/info logs |

---

## 🧪 Example Workflows

### 🔁 Mixed accessions (auto detect)
```bash
python metaphenomap.py --auto-db -i data/test_accessions.txt -o results.csv   --download fastq --verify --zip-all --max-workers 6
```

### 📥 SRA FASTQ download
```bash
python metaphenomap.py --db sra --module sample -a SRR390728   -o out_sra.csv --download fastq --outdir downloads
```

### 🧬 NCBI Assembly
```bash
python metaphenomap.py --db ncbi --module assembly   -a GCF_000146045.2 -o out_asm.csv --download assembly --zip-output
```

### 🔍 PATRIC Genome Metadata
```bash
python metaphenomap.py --db patric --module both   -a 511145.183 -o out_patric.csv
```

---

## 📁 Output Files

Each run generates:
- `out.csv` → Harmonized metadata table
- `downloads/` → FASTQ or genome files (if `--download` used)
- `.zip` → (Optional) compressed outputs for archiving

---

## 🧠 Best Practices & Tips

- Always run commands from the **root directory** (where `metaphenomap.py` is)
- Use **absolute paths** if you get file not found errors
- Re-activate environment anytime with:
  ```bash
  conda activate metaphenomap-env
  ```

---

## 📈 Benchmarking

Check the `metaphenomap_bench/` folder for:
- Real-world test datasets
- Runtime/memory benchmarks
- Evaluation of multithreading & accession scaling

---

## 🧾 Citation

> [Your Name]. *MetaPhenoMap: A Unified CLI for Mining Phenotype-Linked Metadata from Public Genomic Repositories*. (2025) [DOI or Preprint link]

---

## 🧑‍💻 Contributing

PRs welcome! Please submit issues or feature requests.

---

## 🪪 License

MIT License © 2025 — see [`LICENSE`](LICENSE) file.

---

_Made with ❤️ for microbial metadata mining_