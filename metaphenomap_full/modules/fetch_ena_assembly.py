import requests
def fetch_and_parse_ena_assembly_metadata(accession):
    r=requests.get('https://www.ebi.ac.uk/ena/portal/api/filereport',
                   params={'accession':accession,'result':'analysis','fields':'analysis_accession,study_accession,sample_accession,first_public,scientific_name,description,study_title','format':'tsv'}, timeout=20)
    if not r.ok or len(r.text.strip().splitlines())<2: return {'ENA_Analysis_Accession': None}
    hdr,row=r.text.strip().splitlines()[:2]; cols=dict(zip(hdr.split('\t'), row.split('\t')))
    return {
        'ENA_Analysis_Accession': cols.get('analysis_accession'),
        'ENA_Study': cols.get('study_accession'),
        'ENA_Sample': cols.get('sample_accession'),
        'ENA_First_Public': cols.get('first_public'),
        'ENA_Scientific_Name': cols.get('scientific_name'),
        'ENA_Study_Title': cols.get('study_title'),
        'ENA_Assembly_Description': cols.get('description'),
    }
