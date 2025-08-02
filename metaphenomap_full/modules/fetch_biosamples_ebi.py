import requests
def fetch_and_parse_ebibiosamples_metadata(accession):
    url=f'https://www.ebi.ac.uk/biosamples/samples/{accession}'
    r=requests.get(url, timeout=20)
    if not r.ok: return {}
    js=r.json(); ch=js.get('characteristics',{}) or {}
    def pick(*keys):
        for k in keys:
            v=ch.get(k)
            if isinstance(v,list) and v: return v[0].get('text')
            if isinstance(v,dict): return v.get('text')
        return None
    return {
        'Accession': accession,
        'Host': pick('host','host organism'),
        'Isolation_Source': pick('isolation source','isolation_source','source'),
        'Disease': pick('disease','host disease'),
        'Location': pick('geographic location','geo_loc_name','country'),
        'Collection_Date': pick('collection date','collection_date'),
        'Scientific_Name': pick('organism','scientific name'),
    }
