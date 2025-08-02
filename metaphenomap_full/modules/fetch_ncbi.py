import requests, xml.etree.ElementTree as ET
FIELD_ALIASES = {
    'Host':['host','host organism','organism_host','host_species','host taxid'],
    'Isolation_Source':['isolation_source','isolation source','source','specimen','sample_type','body_site','source_material'],
    'Disease':['disease','host_disease','disease state','clinical_information','condition'],
    'AMR_Genes':['amr','antibiotic resistance','resistance_genes','antimicrobial resistance','drug resistance'],
    'Virulence_Genes':['virulence','virulence_factor','virulence gene','toxin_gene'],
    'Location':['geo_loc_name','geographic location','country','region','location'],
    'Collection_Date':['collection_date','sampling_date','isolation_date','date_collected'],
}
def _canonical(name):
    n=(name or '').lower()
    for canon,alist in FIELD_ALIASES.items():
        for a in alist:
            if a in n: return canon
    return None
def fetch_and_parse_biosample(accession):
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    r=requests.get(url, params={'db':'biosample','id':accession,'retmode':'xml'}, timeout=20); r.raise_for_status()
    root=ET.fromstring(r.content)
    out={k:None for k in FIELD_ALIASES}; out['Accession']=accession
    for attr in root.iter('Attribute'):
        name=attr.attrib.get('attribute_name',''); val=(attr.text or '').strip()
        if not val: continue
        key=_canonical(name)
        if key and not out.get(key): out[key]=val
    return out
