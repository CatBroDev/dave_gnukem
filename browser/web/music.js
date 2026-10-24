/* GPL-2.0-or-later. Deferred original tracks, Old Games Archive / CatBroDev. */
(()=>{const loaded=new Set(),failed=new Set();let wanted,active,enabled=false,disposed=false;
const state=Module.musicState={requested:[],loaded:[],failed:[]};
const activate=p=>Module.ccall('oga_music_ready','number',['string'],[p]);
const cancel=()=>{if(active){clearTimeout(active.timer);active.controller.abort();active=null;}};
async function pump(){if(!enabled||disposed||!wanted||failed.has(wanted)||active?.path===wanted)return;if(loaded.has(wanted))return;cancel();
 const path=wanted,file=Module.musicFiles[path];if(!file)return;const job=active={path,controller:new AbortController()};job.timer=setTimeout(()=>job.controller.abort('timeout'),30000);state.requested.push(path);
 try{const r=await fetch(file.url,{signal:job.controller.signal});if(!r.ok)throw Error('Music HTTP '+r.status);const b=await r.arrayBuffer();if(b.byteLength!==file.bytes)throw Error('Music size mismatch');const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),v=>v.toString(16).padStart(2,'0')).join('');if(sha!==file.sha256)throw Error('Music integrity mismatch');if(disposed||active!==job||!enabled)return;Module.FS.mkdirTree(path.slice(0,path.lastIndexOf('/')));Module.FS.writeFile(path,new Uint8Array(b));if(!activate(path))throw Error('Music decode failed');loaded.add(path);state.loaded.push(path);
 }catch(e){if(job.controller.signal.aborted&&job.controller.signal.reason!=='timeout')return;failed.add(path);state.failed.push({path,reason:String(e)});}finally{clearTimeout(job.timer);if(active===job)active=null;}}
Module.requestMusic=path=>{if(!Module.musicFiles[path])return;if(wanted!==path){cancel();wanted=path;if(loaded.has(path)){activate(path);return;}}void pump();};
Module.setMusicEnabled=value=>{enabled=!!value;if(!enabled)cancel();else void pump();};Module.disposeMusic=()=>{disposed=true;enabled=false;cancel();};})();
