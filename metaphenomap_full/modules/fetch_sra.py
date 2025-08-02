import requests
def fetch_and_parse_sra_metadata(accession):
    fields='run_accession,study_accession,sample_accession,experiment_accession,library_source,library_strategy,instrument_platform,instrument_model,collection_date,country,host,scientific_name'
    r=requests.get('https://www.ebi.ac.uk/ena/portal/api/filereport', params={'accession':accession,'result':'read_run','fields':fields,'format':'tsv'}, timeout=20)
    if not r.ok or len(r.text.strip().splitlines())<2: return {}
    hdr,row=r.text.strip().splitlines()[:2]; cols=dict(zip(hdr.split('\t'), row.split('\t')))
    return {
        'Accession': accession,
        'SRA_Run': cols.get('run_accession'),
        'SRA_Experiment': cols.get('experiment_accession'),
        'SRA_Sample': cols.get('sample_accession'),
        'SRA_Study': cols.get('study_accession'),
        'Host': cols.get('host') or None,
        'Isolation_Source': cols.get('library_source'),
        'Library_Strategy': cols.get('library_strategy'),
        'Platform': cols.get('instrument_platform'),
        'Instrument': cols.get('instrument_model'),
        'Location': cols.get('country') or None,
        'Collection_Date': cols.get('collection_date') or None,
        'Scientific_Name': cols.get('scientific_name'),
        'Disease': None, 'AMR_Genes': None, 'Virulence_Genes': None,
    }
