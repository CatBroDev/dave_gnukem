from pathlib import Path
import hashlib,json,re,shutil,sys,zipfile
lab=Path(__file__).resolve().parents[1]; root=lab.parent
assert re.fullmatch('[a-z0-9-]+',sys.argv[1]); build=lab/'build'/sys.argv[1]
assert '_oga_state' not in (build/'dave.js').read_text()
for source,name in [(root/'COPYING','COPYING.txt'),(lab/'RELEASE-README.md','README.txt'),(lab/'notices.txt','notices.txt')]: shutil.copy2(source,build/name)
items=[p for p in root.rglob('*') if p.is_file() and not set(p.relative_to(root).parts)&{'.git','node_modules','__pycache__'} and not p.is_relative_to(lab/'build') and not p.is_relative_to(lab/'emsdk') and not p.is_relative_to(lab/'evidence')]
manifest=[{'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(items)]
with zipfile.ZipFile(build/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(items): z.write(p,p.relative_to(root).as_posix())
 z.writestr('SOURCE-MANIFEST.json',json.dumps(manifest,indent=2))
names=['index.html','dave.js','dave.wasm.bin','dave.data.bin','bridge.js','input.js','persistence.js','music.js','music-manifest.js','COPYING.txt','README.txt','notices.txt','source.zip']+[p.relative_to(build).as_posix() for p in sorted((build/'music').glob('*.ogg'))]
(build/'release-manifest.json').write_text(json.dumps({'files':[{'path':n,'bytes':(build/n).stat().st_size,'sha256':hashlib.sha256((build/n).read_bytes()).hexdigest()} for n in names]},indent=2))
print('Packaged',len(items),'source files and',len(names),'runtime/download files')
