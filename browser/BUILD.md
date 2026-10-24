# Reproduce the browser edition

Upstream code base: `fbda206d0aac575146b01179330484ccf1569aab`.
Original data: `davidjoffe/gnukem_data@b50a69cbe864f6f8e30c82d719f7e46c57d9ad38`.
Install Python 3 and Emscripten **4.0.23**; set `DAVE_EMSDK` to the absolute
SDK directory. Run from this Fork's repository root:

```sh
python -X utf8 browser/scripts/fetch-data.py
python -X utf8 browser/scripts/build-web.py release
python -X utf8 browser/scripts/package-release.py release
python -X utf8 -m http.server 8080 --directory browser/build/release
```

The data script verifies the pinned archive SHA-256 before extraction and retains
all original data notices. It refuses to overwrite an existing data directory.
The build similarly requires a new output name. No private site files or keys
are needed. Emscripten fetches its SDL2/SDL2_mixer/Ogg/Vorbis ports on first use.
PowerShell example: `$env:DAVE_EMSDK = 'C:/tools/emsdk'`.

Open localhost:8080, wait for loading, then dismiss the in-game credits.
Sound starts off. Serve `.wasm.bin` as `application/wasm` and `.data.bin` as
`application/octet-stream`; preserve decoded file bytes if using HTTP gzip.
The 5.6 MB startup data excludes 19.5 MB of music, which loads only when needed
after sound is enabled. The source ZIP is a separate download, never startup data.

Optional automated acceptance (Node.js, `npm install --no-save playwright`,
and installed Google Chrome):

```sh
node browser/scripts/accept-release.mjs release smoke-01
```

This runs headlessly with audio output muted and closes its own browser/server.
It covers first-level movement, native save/restore across a browser restart,
isolated storage, PCM output/mute, failed optional music, and native exit.
Do not publish a build made with `--state`: that flag enables diagnostic exports.

The original sources remain at the root; `browser/web-browser.cpp` and the build
script make Web-only changes explicit. `RUNTIME-SOURCE-MANIFEST.json` records
source hashes for the accepted live release. Packaging the Fork produces a
different source ZIP from the earlier release archive; gameplay inputs and
original data remain the same. Physical phones and full-campaign completion
are not certified. See RELEASE-README.md and notices.txt for credits/licenses.
