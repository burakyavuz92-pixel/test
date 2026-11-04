"""Render validated CadQuery STEP outputs through the existing drafting pipeline."""
import json,sys,pathlib,traceback
import numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Torus
from OCP.BRepCheck import BRepCheck_Analyzer
from cad_recipe_executor import sheet,box
from local_drawing import resolve_local_sections
from template_layout import prepare

def dimensions(shape,cells):
    """Conservative matching: only unique axial diameter supports; never infer distances by value."""
    cylinders=[]
    ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        s=BRepAdaptor_Surface(TopoDS.Face_s(ex.Current()))
        if s.GetType()==GeomAbs_Cylinder:
            c=s.Cylinder();o=c.Location();a=c.Axis().Direction()
            if abs(a.Z())>1-1e-7:
                candidate=(c.Radius(),o.X(),o.Y())
                if not any(np.linalg.norm(np.array(candidate)-v)<1e-5 for v in cylinders):cylinders.append(candidate)
        ex.Next()
    result=[]
    for label,cell in cells.items():
        value=cell.get('nominalMm')
        if value is None:continue
        d={'id':'column_'+label,'type':'diameter' if cell.get('diameterSymbol') else 'distance','nominal':value,'valueSource':{'kind':'column','column':label},'sourceLabel':label,'sourceMeasurement':cell,'effectiveVisible':True,'axis':'Z','targets':[{'operation':'unresolved','role':'No explicit geometric reference'}]}
        candidates=[v for v in cylinders if abs(v[0]*2-value)<1e-5]
        if cell.get('diameterSymbol') and len(candidates)==1:
            r,x,y=candidates[0];d['relation']={'kind':'diameter','surfaces':[{'kind':'cylinder','radius':r,'axisOrigin':[x,y,0],'axisDirection':[0,0,1]}]}
        result.append(d)
    return result

def run(folder,image,excel):
    root=pathlib.Path(folder);job=json.loads((root/'sheet-input.json').read_text());saved={r['outputId']:r['parameters'] for r in json.loads((root/'rows.json').read_text())}
    def parameters(cells):
        result={k:v.get('nominalMm') for k,v in cells.items()}
        for k,v in cells.items():
            if v.get('chamferAngleDeg') is not None:result[k+'__angleDeg']=v['chamferAngleDeg']
        return result
    for row in job:
        if saved.get(row['outputId'])!=parameters(row['cells']):raise ValueError('Excel differs from script geometry parameters: '+row['outputId'])
    reference_file=root/'measurement-references.json'
    references=json.loads(reference_file.read_text()) if reference_file.exists() else {}
    layout=prepare(image,excel,root);evidence={}
    if (root/'visual-markers.json').exists():
        from visual_measurements import merge
        layout,evidence=merge(layout,json.loads((root/'visual-markers.json').read_text()))
    results=[]
    for row in job:
        out=root/row['outputId']
        try:
            reader=STEPControl_Reader()
            if reader.ReadFile(str(out/(row['outputId']+'.step')))!=IFSelect_RetDone:raise ValueError('Validated script STEP missing/unreadable')
            reader.TransferRoots();shape=reader.OneShape()
            if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():raise ValueError('Invalid script STEP')
            drawing=row['drawing'];drawing['dimensions']=dimensions(shape,row['cells'])
            records=references.get(row['outputId'],[]);seen=set()
            for m in records:
                label=m['source']
                if m['id'] in seen:raise ValueError('Duplicate measurement id: '+m['id'])
                seen.add(m['id'])
                existing=next((d for d in drawing['dimensions'] if d['sourceLabel']==label and 'scriptReference' not in d),None)
                if existing is None:
                    from bracket_content import literal as parse_literal
                    content=parse_literal(label);literal=content.pop('nominal')
                    from visual_measurements import canonical
                    approved=[c for c in layout['candidates'] if canonical(c['label'])==canonical(label)]
                    if any(any(symbol in c.get('sourceText','') for symbol in ('Ø','ø','⌀')) for c in approved):content['diameterSymbol']=True
                    existing={'id':m['id'],'sourceLabel':label,'valueSource':{'kind':'constant','value':literal,'unit':'mm'},'nominal':literal,'effectiveVisible':True,'targets':[],'axis':'Z','sourceMeasurement':content};drawing['dimensions'].append(existing)
                existing['type']=m['kind'];existing['scriptReference']=dict(m)
                angle=existing.get('sourceMeasurement',{}).get('chamferAngleDeg')
                if angle is not None:
                    existing['scriptReference'].update(kind='chamfer',angleDeg=angle)
                if evidence:
                    from visual_measurements import canonical
                    marker_key=m.get('markerId',canonical(label))
                    marker=evidence.get(marker_key)
                    if marker is not None:existing['sourceOccurrenceId']=marker_key
                    if marker is None:existing['scriptReference']['unresolved']='Visual evidence missing'
                    else:
                        marker=dict(marker);frame=layout.get('sourceFrames',{}).get(marker['view'],{}).get('bboxPixels')
                        if frame:marker['viewCenterNormalized']=[(frame[0]+frame[2])/2/layout['sourcePixels'][0],(frame[1]+frame[3])/2/layout['sourcePixels'][1]]
                        existing['scriptReference']['visualEvidence']=marker
            drawing['templateLayout']=layout;drawing['geometricTolerances']=[]
            recipe={'outputId':row['outputId'],'geometry':{'operations':[],'frames':[]},'drawing':resolve_local_sections(drawing,box(shape))}
            report=sheet(recipe,shape,{},out,image)
            report['unconfirmedVisualLabels']=layout.get('unconfirmedModelMarkers',[])
            results.append({'outputId':row['outputId'],'status':'sheet-produced','drafting':report})
        except Exception as ex:traceback.print_exc();results.append({'outputId':row['outputId'],'status':'failed','error':str(ex)})
    (root/'script-sheet-results.json').write_text(json.dumps({'apiCalls':0,'results':results},indent=2));print(json.dumps(results,indent=2));return all(r['status']=='sheet-produced' for r in results)
if __name__=='__main__':sys.exit(0 if run(*sys.argv[1:]) else 1)
