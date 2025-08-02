import requests
def fetch_and_parse_assembly_metadata(accession):
    r=requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi',
                   params={'db':'assembly','term':accession,'retmode':'json'}, timeout=20); r.raise_for_status()
    ids=r.json().get('esearchresult',{}).get('idlist',[])
    if not ids:
        link=requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi',
                          params={'dbfrom':'biosample','db':'assembly','id':accession,'retmode':'json'}, timeout=20)
        if link.ok:
            js=link.json(); linksets=js.get('linksets',[])
            if linksets and 'linksetdbs' in linksets[0]:
                for ls in linksets[0]['linksetdbs']:
                    if ls.get('links'): ids=ls['links']; break
    if not ids: return {'Assembly_Accession': None}
    uid=ids[0]
    summ=requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi',
                      params={'db':'assembly','id':uid,'retmode':'json'}, timeout=20).json()
    doc=summ['result'][uid]
    return {
        'Assembly_Accession': doc.get('assemblyaccession'),
        'Organism': doc.get('organism'),
        'Assembly_Level': doc.get('assemblystatus'),
        'Submitter': doc.get('submitter'),
        'Submission_Date': doc.get('submissiondate'),
        'BioSample': doc.get('biosample'),
        'FTP_Path_GenBank': doc.get('ftppath_genbank'),
        'FTP_Path_RefSeq': doc.get('ftppath_refseq'),
    }
