"""Persist product failures so later stages skip only affected rows."""
import json

class ModelProductError(ValueError):
    pass

def model_value(value):
    if isinstance(value,dict) and 'error' in value:
        reason=value['error']
        if not isinstance(reason,str) or not reason.strip():
            raise ValueError('Model product error must contain a nonempty reason')
        raise ModelProductError(reason.strip())
    return value

def failures(root):
    path=root/'product-failures.json'
    return json.loads(path.read_text()) if path.exists() else []

def active_rows(root):
    blocked={r['outputId'] for r in failures(root)}
    return [r for r in json.loads((root/'rows.json').read_text()) if r['outputId'] not in blocked]

def record_failure(root,output_id,stage,error):
    rows=failures(root)
    if not any(r['outputId']==output_id for r in rows):
        rows.append({'outputId':output_id,'stage':stage,'origin':'model' if isinstance(error,ModelProductError) else 'software','reason':str(error)})
    (root/'product-failures.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
