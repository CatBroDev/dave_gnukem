from pathlib import Path
import hashlib,io,zipfile,urllib.request
lab=Path(__file__).resolve().parents[1]
pin='b50a69cbe864f6f8e30c82d719f7e46c57d9ad38'
url='https://codeload.github.com/davidjoffe/gnukem_data/zip/'+pin
blob=urllib.request.urlopen(url,timeout=60).read()
assert hashlib.sha256(blob).hexdigest()=='08fc6f2e5d1cef90ae839873b6b243c4915e1fd62daacc57fcd091b34f992c6c'
target=lab/'data-archive'; target.mkdir(exist_ok=False)
with zipfile.ZipFile(io.BytesIO(blob)) as z:
 for name in z.namelist(): assert (target/name).resolve().is_relative_to(target.resolve())
 z.extractall(target)
print('Verified and extracted original pinned data, with its original licenses.')
