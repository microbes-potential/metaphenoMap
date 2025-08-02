import requests
BASE='https://www.bv-brc.org/api'; HEADERS={'Accept':'application/json'}
def _get(url, params=None):
    r=requests.get(url, params=params, headers=HEADERS, timeout=30); r.raise_for_status(); return r.json()
def _first(rows):
    if isinstance(rows,list) and rows: return rows[0]
    if isinstance(rows,dict) and rows.get('genome_id'): return rows
    return None
def _search_genome(q):
    try:
        doc=_get(f'{BASE}/genome/{q}?http_accept=application/json')
        if isinstance(doc,dict) and doc.get('genome_id'): return doc
    except Exception: pass
    for field in ('genome_id','refseq_accession','genbank_accession','organism_name'):
        url=f'{BASE}/genome/?eq({field},{q})&limit(1)&http_accept=application/json'
        try:
            doc=_first(_get(url)); if doc: return doc
        except Exception: continue
    try:
        if str(q).isdigit():
            url=f'{BASE}/genome/?eq(taxon_id,{q})&sort(+genome_length)&limit(1)&http_accept=application/json'
            doc=_first(_get(url)); if doc: return doc
    except Exception: pass
    try:
        url=f'{BASE}/genome/?keyword({q})&sort(+genome_length)&limit(1)&http_accept=application/json'
        doc=_first(_get(url)); if doc: return doc
    except Exception: pass
    return None
def _map(doc):
    return {
        'Accession': doc.get('genome_id') or doc.get('genbank_accession') or doc.get('refseq_accession'),
        'Scientific_Name': doc.get('organism_name'),
        'Host': doc.get('host_name'),
        'Isolation_Source': doc.get('isolation_source'),
        'Location': doc.get('isolation_country') or doc.get('geographic_location'),
        'Collection_Date': doc.get('collection_year') or doc.get('collection_date'),
        'Disease': doc.get('disease'),
        'Genome_Status': doc.get('genome_status'),
        'Platform': doc.get('sequencing_platform') or doc.get('sequencing_centers'),
        'Genome_Length': doc.get('genome_length'),
        'GC_Content': doc.get('gc_content'),
        'Contigs': doc.get('contigs'),
        'Taxon_ID': doc.get('taxon_id'),
        'BioSample': doc.get('biosample_accession'),
        'BioProject': doc.get('bioproject_accession'),
    }
def fetch_and_parse_patric_metadata(accession):
    doc=_search_genome(accession)
    if not doc: return {}
    return _map(doc)
def fetch_and_parse_patric_assembly(accession):
    doc=_search_genome(accession)
    if not doc: return {}
    return {
        'Assembly_Accession': doc.get('refseq_accession') or doc.get('genbank_accession'),
        'Assembly_Level': doc.get('genome_status'),
        'Submitter': doc.get('sequencing_centers'),
        'BioSample': doc.get('biosample_accession'),
        'BioProject': doc.get('bioproject_accession'),
    }
