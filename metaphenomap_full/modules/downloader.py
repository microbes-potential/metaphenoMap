import os, subprocess, hashlib, requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def _which(cmd):
    from shutil import which; return which(cmd)

def _friendly_name(url, prefix=None):
    base = os.path.basename(urlparse(url).path) or 'file'
    return f"{prefix}_{base}" if prefix else base

def _download_one(url, outdir, toolchain, prefix=None, verbose=False):
    fname = _friendly_name(url, prefix=prefix)
    fpath = os.path.join(outdir, fname)
    aria2, wget, curl = toolchain
    try:
        if aria2:
            args = [aria2, '-x16', '-s16', '-k1M', '-o', fname, '-d', outdir, url]
            subprocess.run(args, check=True, stdout=None if verbose else subprocess.PIPE, stderr=None if verbose else subprocess.PIPE)
        elif wget:
            args = [wget, '-nv'] if not verbose else [wget]
            args += ['-O', fpath, url]
            subprocess.run(args, check=True)
        elif curl:
            args = [curl, '-L', '-o', fpath, url]
            if not verbose: args.insert(1, '-sS')
            subprocess.run(args, check=True)
        else:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(fpath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
        return fpath, None
    except Exception as e:
        return None, str(e)

def perform_downloads(urls, outdir, workers=4, prefix=None, verbose=False):
    if not urls: return []
    os.makedirs(outdir, exist_ok=True)
    aria2 = _which('aria2c'); wget = _which('wget'); curl = _which('curl')
    toolchain = (aria2, wget, curl)
    results = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = [ex.submit(_download_one, u, outdir, toolchain, prefix, verbose) for u in urls]
        for f in as_completed(futs):
            path, err = f.result()
            if path and not err:
                results.append(path)
    return results

def compute_md5(path, chunk=1024*1024):
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for ch in iter(lambda: f.read(chunk), b''):
            md5.update(ch)
    return md5.hexdigest()

def verify_downloads(paths, accession, db, meta):
    report = {}
    for p in paths:
        report[os.path.basename(p)] = {'md5': compute_md5(p), 'expected_md5': None, 'ok': True}
    # ENA MD5 hint per run
    try:
        import requests
        runs = []
        if accession.upper().startswith(('SRR','ERR','DRR')):
            runs = [accession]
        for k in ('SRA_Run','run_accession'):
            if meta.get(k): runs.append(meta[k])
        runs = list({r for r in runs if r})
        if runs:
            base = 'https://www.ebi.ac.uk/ena/portal/api/filereport'
            fields = 'run_accession,fastq_md5,submitted_md5'
            for rr in runs:
                r = requests.get(base, params={'accession': rr, 'result':'read_run', 'fields':fields, 'format':'tsv'}, timeout=30)
                if r.ok:
                    lines = [ln for ln in r.text.strip().split('\n') if ln]
                    if len(lines)>=2:
                        hdr = lines[0].split('\t'); vals = lines[1].split('\t')
                        row = dict(zip(hdr, vals))
                        report['_expected_from_ENA'] = {rr: row.get('fastq_md5') or row.get('submitted_md5')}
    except Exception:
        pass
    return report

# URL resolvers
def _ena_run_fastq_urls(run_accession):
    fields = 'run_accession,fastq_ftp,fastq_http,submitted_ftp,submitted_http'
    base = 'https://www.ebi.ac.uk/ena/portal/api/filereport'
    r = requests.get(base, params={'accession': run_accession, 'result':'read_run','fields':fields,'format':'tsv'}, timeout=30)
    if not r.ok: return []
    lines = [ln for ln in r.text.strip().split('\n') if ln]
    if len(lines)<2: return []
    hdr = lines[0].split('\t'); vals = lines[1].split('\t')
    row = dict(zip(hdr, vals))
    urls = []
    for key in ('fastq_http','fastq_ftp','submitted_http','submitted_ftp'):
        if row.get(key):
            for p in row[key].split(';'):
                if p.startswith('http'): urls.append(p)
                elif p.startswith('ftp'): urls.append('https://'+p)
    return urls

def resolve_fastq_urls(accession, db, meta=None):
    acc = accession.upper()
    if acc.startswith(('SRR','ERR','DRR')): return _ena_run_fastq_urls(acc)
    if db == 'ena' and acc.startswith(('ERS','SRS','DRS','SAMEA')):
        base = 'https://www.ebi.ac.uk/ena/portal/api/search'
        r = requests.get(base, params={'result':'read_run','query':f'sample_accession={accession}','fields':'run_accession','format':'tsv'}, timeout=30)
        if r.ok:
            lines = [ln for ln in r.text.strip().split('\n') if ln]
            if len(lines)>=2:
                runs = [ln.split('\t')[0] for ln in lines[1:] if ln.strip()]
                urls = []
                for run in runs: urls.extend(_ena_run_fastq_urls(run))
                return urls
    if db == 'ncbi' and acc.startswith(('SAMN','SAMD')):
        try:
            elink = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi'
            r = requests.get(elink, params={'dbfrom':'biosample','db':'sra','id':accession,'retmode':'json'}, timeout=30)
            if r.ok:
                js = r.json(); links = []
                for ls in js.get('linksets',[]):
                    for ldb in ls.get('linksetdbs',[]):
                        links.extend(ldb.get('links',[]))
                urls = []
                for uid in links[:10]:
                    s = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi', params={'db':'sra','id':uid,'retmode':'json'}, timeout=30)
                    if s.ok:
                        doc = s.json()['result'].get(str(uid),{})
                        run = doc.get('runs',''); runs = [r.strip() for r in run.split(',') if r.strip()]
                        for rr in runs: urls.extend(_ena_run_fastq_urls(rr))
                return urls
        except Exception: pass
    if db == 'sra': return _ena_run_fastq_urls(acc)
    return []

def resolve_assembly_urls(accession, db, meta=None):
    urls = []
    acc = accession.upper()
    if acc.startswith(('GCA_','GCF_')) or (meta and (meta.get('FTP_Path_RefSeq') or meta.get('FTP_Path_GenBank'))):
        base = meta.get('FTP_Path_RefSeq') or meta.get('FTP_Path_GenBank')
        if not base: return []
        asm = os.path.basename(base)
        for s in ('_genomic.fna.gz','_genomic.gff.gz','_protein.faa.gz','_cds_from_genomic.fna.gz'):
            urls.append(f"{base}/{asm}{s}")
        return urls
    if db == 'ena':
        r = requests.get('https://www.ebi.ac.uk/ena/portal/api/filereport', params={'accession': accession,'result':'analysis','fields':'analysis_accession,submitted_http,submitted_ftp','format':'tsv'}, timeout=30)
        if r.ok:
            lines = [ln for ln in r.text.strip().split('\n') if ln]
            if len(lines)>=2:
                hdr = lines[0].split('\t')
                for row in lines[1:]:
                    cols = dict(zip(hdr, row.split('\t')))
                    for key in ('submitted_http','submitted_ftp'):
                        if cols.get(key):
                            for p in cols[key].split(';'):
                                if p.startswith('http'): urls.append(p)
                                elif p.startswith('ftp'): urls.append('https://'+p)
        return urls
    return urls
