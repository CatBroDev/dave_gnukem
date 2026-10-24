# Dave Gnukem — browser integration

Original game by David Joffe and contributors. Character sprites include work by Evil Mr Henry; Steve Merrifield contributed levels. Browser integration by Old Games Archive / CatBroDev. All original source headers, credits and licenses are retained.

Play: https://oldgamesarchive.org/games/dave-gnukem
Chinese notes: https://oldgamesarchive.org/zh-cn/games/dave-gnukem
Upstream: https://github.com/davidjoffe/dave_gnukem

Pinned code: fbda206d0aac575146b01179330484ccf1569aab
Pinned data: b50a69cbe864f6f8e30c82d719f7e46c57d9ad38

This is a browser build of the modern SDL source, not an original DOS executable. Project development began in the 1990s; version 1.0 appeared in April 2018. This is not an official upstream web release.

## Build

Install and activate Emscripten 4.0.23 and Python 3. Set DAVE_EMSDK to the absolute emsdk directory, then run from the repository root (fetch original data first as described in BUILD.md):

    python -X utf8 browser/scripts/build-web.py release
    python -X utf8 browser/scripts/package-release.py release

The build creates browser/build/release and refuses to overwrite it. The original source and data directories remain untouched. Required SDL2, SDL2_mixer, Ogg and Vorbis ports are fetched by Emscripten on its first build. Serve browser/build/release over HTTP, with dave.wasm.bin as application/wasm. A .bin file may use HTTP gzip encoding; do not change its decoded bytes.

## Changes and controls

Unified SDL2 headers/mixer; native menus run under Asyncify; polling waits yield to the browser; persistent native files use IDBFS. Added explicit host pause/resume, input release, mute, cleanup, and shared multi-touch control support. Native gameplay, level data and enemy logic are retained.

Left/Right move; Ctrl jumps; Alt fires; Up interacts. Up/Down select menus, Enter confirms, Esc opens the in-game menu. Save Game and Restore game are native level-start checkpoints, not exact-position snapshots. The game uses its own IndexedDB database (oldgames-dave-gnukem-v1), separate from other restorations. Saving is local to this browser and site origin; clearing browser storage removes it. Controls redefined inside the native game also need matching shared touch bindings.

Original effects load at startup. Original Ogg music loads on demand after sound is enabled; music failure leaves the game and effects usable, with no automatic retry loop. Audio is muted by default. The source download is not part of startup.

## Credits and licenses

Code/most assets retain the author's MIT/GPL options. This browser integration is distributed under GPL-2.0-or-later; separate asset permissions remain separate. See notices.txt, licenses/, the repository root and browser/data-archive/ for all original notices.

Music by Eric Matyas — www.soundimage.org
Additional sound effects: Eric Matyas — www.soundimage.org
These assets are under the Soundimage International Public License: https://soundimage.org/sample-page/ . They are not relicensed under GPL. They are credited inside the game as requested at https://soundimage.org/attribution-info/ . Tracks and the exit effect are unmodified.

Other credited assets include freepik/flaticon, Zingot, Vinrax and Michel Baradari (CC BY 3.0), Juhani Junkala (CC0), and the Pixel Operator font (CC0). Details and original links remain in the data/source README files.

Acceptance covers startup, first-level movement/jump/fire, menu saving and browser reopening, real PCM output/mute, optional music failure, shared touch, pause/cleanup, and responsive layouts. It does not certify the full campaign or physical Android/iOS performance.
