import copy, importlib.util, json, tempfile, unittest, zipfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import harness as h

class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root=Path(self.tmp.name); self.source=self.root/'fixture.pptx'; self.lib=self.root/'lib'
        with zipfile.ZipFile(self.source,'w') as z:
            z.writestr('ppt/presentation.xml','<p:presentation xmlns:p="'+h.NS['p']+'" xmlns:r="'+h.NS['r']+'"><p:sldIdLst><p:sldId id="1" r:id="r1"/></p:sldIdLst><p:sldSz cx="100" cy="100"/></p:presentation>')
            z.writestr('ppt/_rels/presentation.xml.rels','<Relationships><Relationship Id="r1" Type="x/slide" Target="slides/slide1.xml"/></Relationships>')
            z.writestr('ppt/slides/slide1.xml','<p:sld xmlns:p="'+h.NS['p']+'" xmlns:a="'+h.NS['a']+'"><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="1" name="fixture"/></p:nvSpPr><p:spPr><a:xfrm><a:off x="10" y="20"/><a:ext cx="30" cy="40"/></a:xfrm></p:spPr></p:sp></p:spTree></p:cSld></p:sld>')
    def ingest(self):return h.ingest(self.source,self.lib)
    def test_roundtrip(self):
        a=self.ingest();self.assertEqual(a['shapes'],1);self.assertTrue(h.validate(self.lib)['valid']);self.assertEqual(self.ingest()['status'],'already-present')
    def test_tampered_source(self):
        a=self.ingest();(self.lib/'sources'/a['id']/'source.pptx').write_bytes(b'broken')
        with self.assertRaises(ValueError):h.validate(self.lib)
    def test_tampered_inventory(self):
        a=self.ingest();(self.lib/'sources'/a['id']/'inventory.json').write_text('{}')
        with self.assertRaises(ValueError):h.validate(self.lib)
    def test_unregistered_conflict(self):
        (self.lib/'sources'/h.digest(self.source.read_bytes())).mkdir(parents=True)
        with self.assertRaises(ValueError):self.ingest()
    def test_bad_zip(self):
        self.source.write_bytes(b'not zip')
        with self.assertRaises(zipfile.BadZipFile):self.ingest()
    def test_zip_traversal(self):
        with zipfile.ZipFile(self.source,'a') as z:z.writestr('../secret','bad')
        with self.assertRaises(ValueError):self.ingest()
    def test_schema_conflict(self):
        self.lib.mkdir();h.dump(self.lib/'registry.json',{'schema_version':'99','sources':[]})
        with self.assertRaises(ValueError):self.ingest()
    def test_registry_duplicate(self):
        self.ingest();p=self.lib/'registry.json';r=json.loads(p.read_text());r['sources']*=2;h.dump(p,r)
        with self.assertRaises(ValueError):h.validate(self.lib)
    def test_semantic_tamper_even_rehashed(self):
        a=self.ingest();f=self.lib/'sources'/a['id']/'inventory.json';v=json.loads(f.read_text());v['slides'][0]['shapes']=[];h.dump(f,v);p=self.lib/'registry.json';r=json.loads(p.read_text());r['sources'][0]['artifacts']['inventory.json']=h.digest(f.read_bytes());h.dump(p,r)
        with self.assertRaises(ValueError):h.validate(self.lib)
    def test_theme_color(self):
        e=h.E.fromstring('<a:solidFill xmlns:a="'+h.NS['a']+'"><a:schemeClr val="tx1"><a:tint val="50000"/></a:schemeClr></a:solidFill>');d=h.Deck(self.source)
        self.assertEqual(d.colors(e,{'dk1':'000000'},{'tx1':'dk1'})[0]['resolved_rgb'],'808080')
if __name__=='__main__':unittest.main()
