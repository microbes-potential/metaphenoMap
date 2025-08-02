def normalize_fields(d, validate_terms=True):
    norm=dict(d)
    if isinstance(d.get('Isolation_Source'), str):
        v=d['Isolation_Source'].lower()
        if 'feces' in v or 'stool' in v:
            norm['Isolation_Source_normalized']='feces'
            norm['Isolation_Source_IRI']='http://purl.obolibrary.org/obo/ENVO_02000044'
        elif 'shoot apical meristem' in v:
            norm['Isolation_Source_normalized']='shoot apical meristem'
            norm['Isolation_Source_IRI']='http://purl.obolibrary.org/obo/PO_0020148'
    return norm
