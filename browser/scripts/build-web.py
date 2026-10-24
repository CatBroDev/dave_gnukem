from pathlib import Path
import json,os,re,shutil,subprocess,sys,time,hashlib
lab=Path(__file__).resolve().parents[1];src=lab.parent;data=next((lab/'data-archive').iterdir());sdk=Path(os.environ.get('DAVE_EMSDK',str(lab/'emsdk')))
name=sys.argv[1];assert re.fullmatch('[a-z0-9-]+',name);out=lab/'build'/name;out.mkdir(parents=True,exist_ok=False);(out/'tmp').mkdir();shutil.copytree(src/'src',out/'src')
# Reuse the working native menu under Asyncify. The unfinished legacy Web
# branch both calls menu_move with an obsolete signature and never returns
# its selected menu item to the caller.
p=out/'src/menu.cpp';s=p.read_text(encoding='utf-8');s=s.replace('__EMSCRIPTEN__','OGA_LEGACY_MENU_PUMP');p.write_text(s,encoding='utf-8')
changes=[]
for p in (out/'src').rglob('*'):
 if p.suffix not in ['.cpp','.h']:continue
 s=p.read_text(encoding='utf-8');new=s.replace('#include <SDL/SDL.h>','#include <SDL.h>')
 new=re.sub(r'/\*SDL_Delay\((\d+)\);\*/',r'SDL_Delay(\1);',new)
 if p.name=='djinput.cpp':new=new.replace('void djiPoll()\n{','void djiPoll()\n{\n\toga_sleep(1); // Let browser keyup events reach polling waits.')
 if p.name=='djstring.cpp':new=new.replace('std::string djGetFolderUserSettings()\n{','std::string djGetFolderUserSettings()\n{\n return "/persistent_data"; // Web-only override; original source is preserved.\n')
 if p.name=='game.cpp':
  anchor='\tfclose(pOut);\n\treturn true;'
  assert new.count(anchor)==1
  new=new.replace(anchor,'\tfclose(pOut);\n\tEM_ASM({ Module.flushSaves(); });\n\treturn true;')
 if new!=s:p.write_text(new,encoding='utf-8');changes.append(p.relative_to(out).as_posix())
(out/'web-compat.h').write_text('#include <SDL.h>\n#include <emscripten.h>\nextern "C" { void oga_sleep(unsigned); unsigned long long oga_ticks(); void oga_audio_install(); void oga_request_music(const char*); }\n#define SDL_Delay(ms) oga_sleep(ms)\n',encoding='utf-8')
# Browser-only transformations, preserving the downloaded source tree.
def edit(rel,old,new):
 p=out/'src'/rel;t=p.read_text();assert old in t,(rel,old);p.write_text(t.replace(old,new))
edit('sdl/djinput.cpp','void djiPollBegin()\n{','void djiPollBegin()\n{\n oga_sleep(1);')
edit('main.cpp','//DaveCleanup();','DaveCleanup();\n Mix_CloseAudio();\n SDL_Quit();')
edit('sdl/djsound.cpp','g_bSoundInit = true;','g_bSoundInit = true;\n oga_audio_install();')
edit('sdl/djtime.cpp','SDL_GetTicks()','oga_ticks()');edit('sdl/djtime.cpp','SDL_GetTicks64()','oga_ticks()')
edit('game.cpp','g_pInGameMusic = Mix_LoadMUS((sBasePath + asMusicFiles[nMusicFile]).c_str());','oga_request_music((sBasePath + asMusicFiles[nMusicFile]).c_str());')
p=out/'src/mainmenu.cpp';t=p.read_text();a=t.index('g_Menu.pMusic = Mix_LoadMUS(');b=t.index('#endif',a)
t=t[:a]+'oga_request_music(djDATAPATHc("music/eric_matyas/8-Bit-Mayhem.ogg"));\n'+t[b:]
t=t.replace('Mix_FadeInMusic(g_Menu.pMusic, -1, 800);','oga_request_music(djDATAPATHc("music/eric_matyas/8-Bit-Mayhem.ogg"));').replace('Mix_FadeInMusicPos(g_Menu.pMusic, -1, 800, 0);','oga_request_music(djDATAPATHc("music/eric_matyas/8-Bit-Mayhem.ogg"));').replace('if (g_Menu.pMusic!=NULL)','if (true)')
p.write_text(t)
assets=out/'assets';shutil.copytree(data,assets,ignore=shutil.ignore_patterns('music'))
music={}
for p in (data/'music').rglob('*.ogg'):
 target=out/'music'/p.name;target.parent.mkdir(exist_ok=True);shutil.copy2(p,target)
 key='/data/'+p.relative_to(data).as_posix();music[key]={'url':'music/'+p.name,'path':key,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(out/'music-manifest.js').write_text('Module.musicFiles='+json.dumps(music)+';')
section=re.search(r'OBJ = (.*?)\n\n', (src/'Makefile').read_text(),re.S).group(1)
files=[out/p.replace('.o','.cpp') for p in re.findall(r'src/[\w/]+\.o',section)]
assert all(p.exists() for p in files)
files.append(lab/'web-browser.cpp')
flags=['-O2', '-I'+str(out/'src'),'-std=c++14','-include',str(out/'web-compat.h'),'-DDATA_DIR="/data/"','-DVERSION="1.0.3-web-probe"','-sUSE_SDL=2','-sUSE_SDL_MIXER=2','-sSDL2_MIXER_FORMATS=["ogg"]','-sASYNCIFY','-sASYNCIFY_STACK_SIZE=131072','-sSTACK_SIZE=1048576','-sALLOW_MEMORY_GROWTH=1','-sINITIAL_MEMORY=67108864','-sFORCE_FILESYSTEM=1','-sEXIT_RUNTIME=1','-lidbfs.js','-sEXPORTED_RUNTIME_METHODS=["FS","IDBFS","callMain","ccall","UTF8ToString","addRunDependency","removeRunDependency"]','--preload-file',str(assets)+'@/data','-o',str(out/'dave.js')]
if '--state' in sys.argv:flags.append('-DOGA_DIAGNOSTIC')
(out/'compile.rsp').write_text('\n'.join(json.dumps(str(a)) for a in [*files,*flags]))
env=dict(os.environ,EM_CONFIG=str(sdk/'.emscripten'),EMSDK_PYTHON=sys.executable,EMCC_CORES='4',TEMP=str(out/'tmp'),TMP=str(out/'tmp'))
start=time.monotonic()
with (out/'build.log').open('w') as log:r=subprocess.run([sys.executable,str(sdk/'upstream/emscripten/em++.py'),'@'+str(out/'compile.rsp')],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
result={'exitCode':r.returncode,'seconds':round(time.monotonic()-start,1),'translationUnits':len(files),'overrides':['src/menu.cpp',*changes]};(out/'build-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if r.returncode:print((out/'build.log').read_text()[-4500:]);sys.exit(r.returncode)

for f in (lab/'web').iterdir():shutil.copy2(f,out/f.name)
for suffix in ['wasm','data']:(out/('dave.'+suffix)).rename(out/('dave.'+suffix+'.bin'))
print(json.dumps({'preloadBytes':(out/'dave.data.bin').stat().st_size,'deferredMusicBytes':sum(v['bytes'] for v in music.values()),'testExports':'--state' in sys.argv}))
