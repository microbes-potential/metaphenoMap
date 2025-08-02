.PHONY: install auto sra ncbi_asm patric
install:
	pip install -r requirements.txt
auto:
	python metaphenomap.py --auto-db -i data/test_accessions.txt -o out_auto.csv --download fastq --verify --max-workers 6 --outdir downloads --zip-all --verbose
sra:
	python metaphenomap.py --db sra --module sample -a SRR390728 -o out_sra.csv --download fastq --outdir downloads --zip-output --verbose
ncbi_asm:
	python metaphenomap.py --db ncbi --module assembly -a GCF_000146045.2 -o out_asm.csv --download assembly --outdir downloads --zip-output --verbose
patric:
	python metaphenomap.py --db patric --module both -a 511145.183 -o out_patric.csv --verbose
