#!/usr/bin/env python3
"""Offline, private-by-default DrawingML design inventory. Python stdlib only."""
import argparse, collections, hashlib, json, math, os, posixpath, shutil, sys, zipfile
from pathlib import Path
import xml.etree.ElementTree as E
VERSION='1.0.0'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def tag(e): return e.tag.split('}')[-1]
def digest(b): return hashlib.sha256(b).hexdigest()
def tree(e):
    if e is None: return None
    return {'tag':tag(e),'attributes':dict(e.attrib),'text':e.text if e.text and e.text.strip() else None,'children':[tree(c) for c in e]}
def dump(p,o): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def flatten(shapes):
    for s in shapes:
        yield s
        yield from flatten(s['children'])
class Deck:
    def __init__(self,path):
        self.z=zipfile.ZipFile(path); self.names=set(self.z.namelist())
        if len(self.names)!=len(self.z.namelist()): raise ValueError('duplicate ZIP member')
        if any(n.startswith('/') or '..' in n.split('/') for n in self.names): raise ValueError('unsafe ZIP path')
        if sum(i.file_size for i in self.z.infolist())>1024**3: raise ValueError('package exceeds 1 GiB')
        self.cache={}
    def xml(self,p):
        if p not in self.cache: self.cache[p]=E.fromstring(self.z.read(p))
        return self.cache[p]
    def rels(self,p):
        r=posixpath.join(posixpath.dirname(p),'_rels',posixpath.basename(p)+'.rels')
        if r not in self.names:return {}
        return {x.get('Id'):{'type':x.get('Type').split('/')[-1],'external':x.get('TargetMode')=='External','target':x.get('Target') if x.get('TargetMode')=='External' else posixpath.normpath(posixpath.join(posixpath.dirname(p),x.get('Target')))} for x in self.xml(r)}
    def linked(self,p,kind): return next((r['target'] for r in self.rels(p).values() if r['type']==kind and not r['external']),None)
    def theme(self,p):
        layout=self.linked(p,'slideLayout'); master=self.linked(layout,'slideMaster') if layout else None; th=self.linked(master,'theme') if master else None
        root=self.xml(th) if th else None; colors={}
        if root is not None:
            for c in root.findall('.//a:clrScheme/*',NS):
                if len(c): colors[tag(c)]=c[0].get('val') if tag(c[0])=='srgbClr' else c[0].get('lastClr')
        cmap={}
        if master:
            n=self.xml(master).find('p:clrMap',NS)
            if n is not None:cmap.update(n.attrib)
        for part in (layout,p):
            if part:
                n=self.xml(part).find('p:clrMapOvr/a:overrideClrMapping',NS)
                if n is not None:cmap.update(n.attrib)
        return layout,master,th,colors,cmap
    def colors(self,e,palette,cmap):
        out=[]
        for c in e.iter():
            k=tag(c)
            if k not in ('srgbClr','schemeClr','sysClr','prstClr','scrgbClr','hslClr'):continue
            v=c.get('val'); base=v if k=='srgbClr' else c.get('lastClr') if k=='sysClr' else palette.get(cmap.get(v,v)) if k=='schemeClr' else None
            rgb=base; transforms=[{'type':tag(t),'value':t.get('val')} for t in c]
            supported={'alpha','alphaMod','alphaOff','tint','shade','lumMod','lumOff'}
            if base and len(base)==6 and all(t['type'] in supported for t in transforms):
                import colorsys
                r,g,b=[int(base[i:i+2],16)/255 for i in (0,2,4)]
                for t in transforms:
                    q=int(t['value'] or 0)/100000
                    if t['type']=='tint':r,g,b=[x+(1-x)*q for x in (r,g,b)]
                    elif t['type']=='shade':r,g,b=[x*q for x in (r,g,b)]
                    elif t['type'] in ('lumMod','lumOff'):
                        h,l,s=colorsys.rgb_to_hls(r,g,b); l=l*q if t['type']=='lumMod' else l+q; r,g,b=colorsys.hls_to_rgb(h,max(0,min(1,l)),s)
                rgb=''.join(f'{round(max(0,min(1,x))*255):02X}' for x in (r,g,b))
            elif transforms:rgb=None
            out.append({'kind':k,'value':v,'base_rgb':base,'resolved_rgb':rgb,'transforms':transforms,'raw':tree(c)})
        return out
    def shape(self,e,part,path,palette,cmap):
        nv=next((n for n in e.iter() if tag(n)=='cNvPr'),None)
        x=e.find('p:spPr/a:xfrm',NS)
        if x is None:x=e.find('p:grpSpPr/a:xfrm',NS)
        if x is None:x=e.find('p:xfrm',NS)
        geo={'coordinate_space':'parent-group' if '/' in path else 'slide','transform':tree(x),'units':'EMU','rotation_units':'1/60000 degree'}
        if x is not None:
            for n in x:
                geo[tag(n)]={k:int(v) for k,v in n.attrib.items()}
            geo['attributes']=dict(x.attrib)
        runs=[]
        for n in e.findall('.//a:r',NS)+e.findall('.//a:fld',NS):
            rp=n.find('a:rPr',NS); attrs=dict(rp.attrib) if rp is not None else {}
            runs.append({'label':''.join(n.itertext()) if n.find('a:t',NS) is None else n.find('a:t',NS).text,'font_size_pt':int(attrs['sz'])/100 if 'sz'in attrs else None,'bold':attrs.get('b'),'fonts':[dict(f.attrib) for f in rp or [] if tag(f) in ('latin','ea','cs','sym')],'colors':self.colors(rp,palette,cmap) if rp is not None else [],'properties':tree(rp),'inheritance':'null means inherited/unresolved; see layout/master/theme XML'})
        images=[]; rels=self.rels(part)
        for b in e.findall('.//a:blip',NS):
            rid=b.get('{'+NS['r']+'}embed') or b.get('{'+NS['r']+'}link'); rel=rels.get(rid); item={'relationship_id':rid,'relationship':rel}
            if rel and not rel['external'] and rel['target'] in self.names:
                data=self.z.read(rel['target']); item.update(sha256=digest(data),bytes=len(data),part=rel['target'])
            images.append(item)
        children=[self.shape(c,part,path+'/'+str(i),palette,cmap) for i,c in enumerate(e) if tag(c) in ('sp','pic','grpSp','cxnSp','graphicFrame','contentPart')]
        return {'id':path,'native_id':nv.get('id') if nv is not None else None,'name':nv.get('name') if nv is not None else None,'type':tag(e),'label':'\n'.join(t.text or '' for t in e.findall('.//a:t',NS)) if tag(e)!='grpSp' else '', 'geometry':geo,'colors':self.colors(e,palette,cmap),'fill':[tree(n) for n in e.findall('p:spPr/*',NS) if tag(n) in ('solidFill','gradFill','blipFill','noFill','pattFill','grpFill')], 'stroke':[tree(n) for n in e.findall('p:spPr/a:ln',NS)],'effects':[tree(n) for n in e.iter() if tag(n) in ('effectLst','effectDag','effectRef')],'style':tree(e.find('p:style',NS)),'text_body':tree(e.find('p:txBody',NS)),'runs':runs,'images':images,'crops':[dict(n.attrib) for n in e.findall('.//a:srcRect',NS)],'tables':[tree(n) for n in e.findall('.//a:tbl',NS)],'charts':[{'relationship':rels.get(n.get('{'+NS['r']+'}id'))} for n in e.iter() if tag(n)=='chart'],'children':children,'raw_xml':E.tostring(e,encoding='unicode')}
    def extract(self):
        p='ppt/presentation.xml'; root=self.xml(p); rels=self.rels(p); slides=[]
        for idx,sid in enumerate(root.findall('p:sldIdLst/p:sldId',NS),1):
            part=rels[sid.get('{'+NS['r']+'}id')]['target']; r=self.xml(part); layout,master,th,pal,cmap=self.theme(part); st=r.find('p:cSld/p:spTree',NS)
            shapes=[self.shape(n,part,str(i),pal,cmap) for i,n in enumerate(st) if tag(n) not in ('nvGrpSpPr','grpSpPr')]
            bg=[]
            for origin in (part,layout,master):
                if origin:
                    b=self.xml(origin).find('p:cSld/p:bg',NS)
                    if b is not None:bg.append({'origin':origin,'xml':tree(b),'colors':self.colors(b,pal,cmap)})
            slides.append({'index':idx,'native_id':sid.get('id'),'part':part,'hidden':r.get('show')=='0','layout':layout,'master':master,'theme':th,'palette':pal,'color_map':cmap,'backgrounds':bg,'effective_background_origin':bg[0]['origin'] if bg else None,'shapes':shapes,'relationships':self.rels(part)})
        parts={n:{'sha256':digest(self.z.read(n)),'xml':self.z.read(n).decode('utf-8')} for n in sorted(self.names) if n.endswith('.xml') and any(t in n for t in ('slideMasters/','slideLayouts/','theme/','charts/'))}
        return {'schema_version':VERSION,'slide_size_emu':dict(root.find('p:sldSz',NS).attrib),'slides':slides,'support_parts':parts,'limitations':['No visual rendering or visual QA performed.','Group transforms preserved in parent coordinates; no world-space bounding box approximation.','Unspecified text styling is inherited; raw layout/master/theme retained, not guessed.','Theme style references, arbitrary color transforms, presets and background fills may require renderer.','Labels are private identifiers, not semantic/marketing analysis.']}
def token_stats(inv):
    buckets=collections.defaultdict(lambda:collections.defaultdict(list))
    for sl in inv['slides']:
        for sh in flatten(sl['shapes']):
            ref=f"slide:{sl['index']}/shape:{sh['id']}"
            # group descendant colors/runs would duplicate; use leaf shapes only
            if sh['children']:continue
            for c in sh['colors']:
                if c['resolved_rgb']:buckets['color'][c['resolved_rgb']].append(ref)
            for run in sh['runs']:
                if run['font_size_pt'] is not None:buckets['font_size_pt'][str(run['font_size_pt'])].append(ref)
                for f in run['fonts']:
                    if f.get('typeface'):buckets['font_family'][f['typeface']].append(ref)
            for k in ('ext','off'):
                for axis,v in sh['geometry'].get(k,{}).items(): buckets['geometry_'+k+'_'+axis][str(v)].append(ref)
    return {'method':'Explicit XML occurrences; candidates not approved tokens. Colors include text/fill/stroke/effect roles; no semantic role inferred. Group descendants counted at leaves.','categories':{k:[{'value':v,'count':len(refs),'provenance':refs,'status':'candidate'} for v,refs in sorted(vals.items(),key=lambda x:(-len(x[1]),x[0]))] for k,vals in buckets.items()}}
def elements(inv):
    lines=['# Приватный каталог элементов','Все значения извлечены из XML. EMU; 914400 EMU = 1 дюйм. Порядок — порядок отрисовки внутри контейнера. Групповые координаты локальные. null/отсутствие — наследование или неизвестное, не отсутствие оформления. Визуальная проверка не выполнена.']
    for sl in inv['slides']:
        lines += [f"\n## Слайд {sl['index']}",f"Part: `{sl['part']}`; hidden={sl['hidden']}; layout={sl['layout']}; master={sl['master']}; theme={sl['theme']}",'Фон: `'+json.dumps(sl['backgrounds'],ensure_ascii=False)+'`']
        for sh in flatten(sl['shapes']):
            lines += [f"\n### Элемент {sh['id']} · {sh['type']} · {sh['name']}",'Label: '+json.dumps(sh['label'],ensure_ascii=False)]
            for key in ('geometry','fill','colors','stroke','effects','style','runs','images','crops','tables','charts'):
                lines += [f"- {key}: `"+json.dumps(sh[key],ensure_ascii=False)+'`']
            lines += ['- Полный XML: `inventory.json`, стабильный путь shape.id; включает custom geometry, placeholders, paragraphs, table cell styles, connectors и расширения.']
    return '\n'.join(lines)+'\n'
def validate(root):
    reg=json.loads((root/'registry.json').read_text()); errors=[]
    if reg.get('schema_version')!=VERSION:errors.append('unsupported registry schema')
    ids=set()
    for ent in reg['sources']:
        sid=ent['id']
        if sid in ids:errors.append('duplicate source id')
        ids.add(sid)
        if sid!=ent['sha256'] or len(sid)!=64 or any(c not in '0123456789abcdef' for c in sid):errors.append('invalid immutable id')
        folder=root/'sources'/sid
        for name,h in ent['artifacts'].items():
            if name.startswith('/') or '..' in Path(name).parts: errors.append('unsafe artifact path');continue
            file=folder/name
            if not file.exists() or digest(file.read_bytes())!=h:errors.append('artifact hash mismatch: '+name)
        try:
            inv=json.loads((folder/'inventory.json').read_text())
            if inv['schema_version']!=VERSION:errors.append('unsupported inventory schema')
            if len(inv['slides'])!=ent['slide_count']:errors.append('slide count mismatch')
            for slide in inv['slides']:
                seen=set()
                for shape in flatten(slide['shapes']):
                    if shape['id'] in seen:errors.append('duplicate shape id')
                    seen.add(shape['id'])
            source=folder/'source.pptx'
            if digest(source.read_bytes())!=sid:errors.append('source hash mismatch')
            actual=Deck(source).extract()
            if actual!=inv:errors.append('inventory differs from source extraction')
        except (OSError,ValueError,KeyError,zipfile.BadZipFile,E.ParseError) as ex:errors.append(str(ex))
    if errors:raise ValueError('; '.join(errors))
    return {'valid':True,'sources':len(ids)}
def ingest(source,root):
    data=source.read_bytes(); sid=digest(data); regpath=root/'registry.json'; reg=json.loads(regpath.read_text()) if regpath.exists() else {'schema_version':VERSION,'sources':[]}
    if reg['schema_version']!=VERSION:raise ValueError('unsupported registry schema')
    if any(e['id']==sid for e in reg['sources']): validate(root);return {'id':sid,'status':'already-present'}
    folder=root/'sources'/sid
    if folder.exists():raise ValueError('unregistered directory conflict; never overwrite')
    inv=Deck(source).extract(); folder.mkdir(parents=True)
    try:
        (folder/'source.pptx').write_bytes(data); dump(folder/'inventory.json',inv); dump(folder/'tokens.json',token_stats(inv)); (folder/'docs').mkdir(); (folder/'docs/ELEMENTS.md').write_text(elements(inv),encoding='utf-8')
        artifacts={p.relative_to(folder).as_posix():digest(p.read_bytes()) for p in folder.rglob('*') if p.is_file()}
        entry={'id':sid,'sha256':sid,'slide_count':len(inv['slides']),'artifacts':artifacts,'review':'unreviewed','visual_qa':'not-performed'}
        reg['sources'].append(entry); dump(regpath,reg)
    except Exception:
        shutil.rmtree(folder);raise
    return {'id':sid,'status':'ingested','slides':len(inv['slides']),'shapes':sum(1 for sl in inv['slides'] for _ in flatten(sl['shapes']))}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--library',type=Path,default=Path('private/library')); sub=ap.add_subparsers(dest='command',required=True); ing=sub.add_parser('ingest');ing.add_argument('source',type=Path);sub.add_parser('validate');sub.add_parser('stats'); a=ap.parse_args()
    try:
        if a.command=='ingest': result=ingest(a.source,a.library)
        elif a.command=='validate':result=validate(a.library)
        else:
            validate(a.library); reg=json.loads((a.library/'registry.json').read_text()); result={'sources':len(reg['sources']),'slides':sum(x['slide_count'] for x in reg['sources']),'inventories':[x['id'] for x in reg['sources']]}
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,zipfile.BadZipFile,E.ParseError) as ex:print(json.dumps({'error':str(ex)},ensure_ascii=False),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
