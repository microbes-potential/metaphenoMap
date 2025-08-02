import requests, xml.etree.ElementTree as ET
PORTAL_SEARCH='https://www.ebi.ac.uk/ena/portal/api/search'
BROWSER_XML='https://www.ebi.ac.uk/ena/browser/api/xml/'
FILEREPORT='https://www.ebi.ac.uk/ena/portal/api/filereport'
FIELDS=['sample_accession','scientific_name','tax_id','host','host_tax_id','sex','age','isolation_source','country','geographic_location','collection_date','description','broker_name','center_name']
def _portal(acc):
    r=requests.get(PORTAL_SEARCH, params={'result':'sample','query':f'sample_accession={acc}','fields':','.join(FIELDS),'format':'tsv'}, timeout=20); r.raise_for_status()
    lines=[ln for ln in r.text.strip().split('\n') if ln]; 
    if len(lines)<2: return None
    h=lines[0].split('\t'); v=lines[1].split('\t'); return dict(zip(h,v))
def _browser(acc):
    r=requests.get(BROWSER_XML+acc, timeout=20)
    if not r.ok or not r.content: return None
    root=ET.fromstring(r.content); out={'sample_accession':acc}
    for a in root.iter('SAMPLE_ATTRIBUTE'):
        tag=(a.findtext('TAG') or '').strip().lower(); val=(a.findtext('VALUE') or '').strip()
        if not val: continue
        if 'host' in tag and 'host_tax' not in tag: out.setdefault('host',val)
        elif 'isolation' in tag or 'source' in tag: out.setdefault('isolation_source',val)
        elif 'country' in tag or 'geo' in tag or 'location' in tag: out.setdefault('country',val)
        elif 'collection' in tag or 'date' in tag: out.setdefault('collection_date',val)
    sci=root.findtext('.//SAMPLE_NAME/SCIENTIFIC_NAME'); 
    if sci: out.setdefault('scientific_name',sci); 
    return out
def _filereport(acc):
    r=requests.get(FILEREPORT, params={'accession':acc,'result':'sample','fields':','.join(FIELDS),'format':'tsv'}, timeout=20)
    if not r.ok: return None
    lines=[ln for ln in r.text.strip().split('\n') if ln]; 
    if len(lines)<2: return None
    h=lines[0].split('\t'); v=lines[1].split('\t'); return dict(zip(h,v))
def fetch_and_parse_ena_sample(accession):
    row=None
    for f in (_portal,_browser,_filereport):
        try:
            row=f(accession)
            if row: break
        except Exception: row=None
    if not row: return {}
    return {
        'Accession': accession,
        'Scientific_Name': row.get('scientific_name'),
        'Host': row.get('host'),
        'Host_Tax_ID': row.get('host_tax_id'),
        'Sex': row.get('sex'),
        'Age': row.get('age'),
        'Isolation_Source': row.get('isolation_source') or row.get('description'),
        'Disease': None,
        'AMR_Genes': None,
        'Virulence_Genes': None,
        'Location': row.get('geographic_location') or row.get('country'),
        'Collection_Date': row.get('collection_date'),
        'Center_Name': row.get('center_name') or row.get('broker_name'),
    }
