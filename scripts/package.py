#!/usr/bin/env python3
"""Allowlisted public ZIP and isolated confidential ZIP, with byte verification."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
FILES=['README.md','DESIGN.md','HARNESS.md','.gitignore','harness.py','LICENSE']
DIRS=['tests','schemas','docs','skills','scripts']
def pack(dest,files):
    paths=sorted(set(files)); expected={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p in paths:z.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(dest) as z:
        assert set(z.namelist())==set(expected)
        for n,h in expected.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    return {'path':str(dest),'members':len(paths),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
def main():
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    public=[ROOT/n for n in FILES if (ROOT/n).is_file()]
    public += [p for d in DIRS for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo')]
    assert not any('private' in p.relative_to(ROOT).parts for p in public)
    confidential=[p for p in (ROOT/'private').rglob('*') if p.is_file()]
    results=[pack(out/'presentation-design-harness-public.zip',public),pack(out/'presentation-design-harness-PRIVATE.zip',confidential)]
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
