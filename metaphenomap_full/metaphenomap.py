#!/usr/bin/env python3
import argparse, os, sys, importlib, logging, re
from datetime import datetime
import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

SUPPORTED_DBS = ["ncbi","ena","sra","ebibiosamples","patric"]
DL_CHOICES = ["none","fastq","assembly","both"]

def resolve_func(path, fname):
    mod = importlib.import_module(path)
    fn = getattr(mod, fname, None)
    if not callable(fn):
        raise ImportError(f"Module '{path}' does not define required function '{fname}()'.")
    return fn

def load_accessions(fp):
    with open(fp, "r") as f:
        return [ln.strip() for ln in f if ln.strip()]

def setup_logging():
    logging.basicConfig(filename="metaphenomap.log",
                        filemode="w",
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

def detect_db_and_module(acc):
    u = acc.upper()
    if u.startswith(('GCF_','GCA_')):    return ('ncbi','assembly')
    if u.startswith(('SRR','ERR','DRR')):return ('sra','sample')
    if u.startswith(('ERS','SRS','DRS','SAMEA')): return ('ena','sample')
    if u.startswith(('SAMN','SAMD')):    return ('ncbi','sample')
    if re.match(r'^\d+\.\d+$', acc):  return ('patric','both')
    return ('ena','sample')

def main():
    ap = argparse.ArgumentParser(description='MetaPhenoMap (final, auto-db, verify, parallel)')
    ap.add_argument('-i','--input', help='Text file: one accession per line')
    ap.add_argument('-a','--accession', help='Single accession')
    ap.add_argument('-o','--output', required=True, help='Output CSV path')
    ap.add_argument('--db', choices=SUPPORTED_DBS, help='Database (omit with --auto-db)')
    ap.add_argument('--module', choices=['sample','assembly','both'], help='Module (omit with --auto-db)')
    ap.add_argument('--auto-db', action='store_true', help='Auto-detect db/module per accession')
    ap.add_argument('--download', choices=DL_CHOICES, default='none', help='Download FASTQ and/or assembly')
    ap.add_argument('--outdir', default='downloads', help='Directory to save downloads')
    ap.add_argument('--zip-output', action='store_true', help='Zip each accession folder after download')
    ap.add_argument('--zip-all', action='store_true', help='Zip the whole outdir at the end')
    ap.add_argument('--normalize', action='store_true', help='Apply light ontology normalization')
    ap.add_argument('--max-workers', type=int, default=4, help='Parallel download workers')
    ap.add_argument('--verify', action='store_true', help='Compute MD5 and include ENA MD5s if available')
    ap.add_argument('--verbose', action='store_true', help='Verbose output')
    ap.add_argument('--dryrun', action='store_true', help='No file writes/downloads')
    args = ap.parse_args()

    setup_logging()

    if args.accession and args.input:
        raise SystemExit('Provide either --accession OR --input, not both.')
    if args.input:
        accessions = load_accessions(args.input)
    elif args.accession:
        accessions = [args.accession.strip()]
    else:
        raise SystemExit('Please provide either --accession or --input')

    # Utilities
    normalize_fields = None
    if args.normalize:
        try: normalize_fields = resolve_func('modules.normalize_ontology','normalize_fields')
        except Exception as e:
            logging.warning(f'Normalization disabled: {e}'); normalize_fields = None

    resolve_fastq_urls  = resolve_func('modules.downloader','resolve_fastq_urls')
    resolve_assembly_urls = resolve_func('modules.downloader','resolve_assembly_urls')
    perform_downloads   = resolve_func('modules.downloader','perform_downloads')
    verify_downloads    = resolve_func('modules.downloader','verify_downloads')

    os.makedirs(args.outdir, exist_ok=True)

    print(f"\n[+] Starting (download={args.download}, auto-db={args.auto_db})...")
    results = []
    for acc in tqdm(accessions):
        if args.auto_db:
            db, module = detect_db_and_module(acc)
        else:
            if not args.db or not args.module:
                raise SystemExit('--db and --module are required unless --auto-db is set')
            db, module = args.db, args.module

        meta = {'Accession': acc, '_db': db, '_module': module,
                '_fetched_at': datetime.utcnow().isoformat()+'Z', '_error': None}

        try:
            sample_fetch = assembly_fetch = None
            if module in ['sample','both']:
                if db == 'ncbi':   sample_fetch = resolve_func('modules.fetch_ncbi','fetch_and_parse_biosample')
                elif db == 'ena':  sample_fetch = resolve_func('modules.fetch_ena','fetch_and_parse_ena_sample')
                elif db == 'sra':  sample_fetch = resolve_func('modules.fetch_sra','fetch_and_parse_sra_metadata')
                elif db == 'ebibiosamples': sample_fetch = resolve_func('modules.fetch_biosamples_ebi','fetch_and_parse_ebibiosamples_metadata')
                elif db == 'patric': sample_fetch = resolve_func('modules.fetch_patric','fetch_and_parse_patric_metadata')
            if module in ['assembly','both']:
                if db == 'ncbi':   assembly_fetch = resolve_func('modules.fetch_assembly','fetch_and_parse_assembly_metadata')
                elif db == 'ena':  assembly_fetch = resolve_func('modules.fetch_ena_assembly','fetch_and_parse_ena_assembly_metadata')
                elif db == 'patric': assembly_fetch = resolve_func('modules.fetch_patric','fetch_and_parse_patric_assembly')

            if sample_fetch:   meta.update(sample_fetch(acc) or {})
            if assembly_fetch: meta.update(assembly_fetch(acc) or {})

            if normalize_fields: meta = normalize_fields(meta, validate_terms=True) or meta

            if args.download != 'none':
                fastq_urls = asm_urls = []
                if args.download in ['fastq','both']:
                    fastq_urls = resolve_fastq_urls(acc, db, meta) or []
                if args.download in ['assembly','both']:
                    asm_urls = resolve_assembly_urls(acc, db, meta) or []
                if args.verbose: print(f"[i] {acc} FASTQ URLs: {len(fastq_urls)}  ASM URLs: {len(asm_urls)}")
                acc_dir = os.path.join(args.outdir, acc.replace('/','_'))
                if not args.dryrun and (fastq_urls or asm_urls):
                    os.makedirs(acc_dir, exist_ok=True)
                    downloaded = perform_downloads(fastq_urls + asm_urls, acc_dir, workers=args.max_workers, prefix=acc, verbose=args.verbose)
                    meta['_downloads'] = downloaded or []
                    if args.verify and downloaded:
                        meta['_verify'] = verify_downloads(downloaded, acc, db, meta)
                    if args.zip_output and downloaded:
                        import shutil; shutil.make_archive(acc_dir, 'zip', acc_dir)
                        meta['_zip'] = acc_dir + '.zip'

            if args.verbose: print(f"[✓] {acc} → {meta}")

        except Exception as e:
            meta['_error'] = str(e)
            logging.error(f'Failed {acc}: {e}')
            if args.verbose: print(f"[!] {acc}: {e}")
        finally:
            results.append(meta)

    if args.zip_all and not args.dryrun:
        import shutil; shutil.make_archive(args.outdir.rstrip('/'), 'zip', args.outdir)

    if not results:
        print('[!] No records fetched.'); return

    df = pd.DataFrame(results)
    prov = ['Accession','_db','_module','_fetched_at','_error','_downloads','_verify','_zip']
    cols = prov + [c for c in df.columns if c not in prov]
    df = df.reindex(columns=cols)
    if args.dryrun:
        print(df.head().to_string(index=False)); print('[i] Dry-run: not writing CSV')
    else:
        df.to_csv(args.output, index=False); print(f"[✓] Saved: {args.output}")

if __name__ == '__main__':
    main()
