// GPL-2.0-or-later. Browser integration: Old Games Archive / CatBroDev.
// Original Dave Gnukem: David Joffe and credited contributors.
#include <SDL.h>
#include <SDL_mixer.h>
#include <emscripten.h>
#include <cstring>
#include <string>
#include "djinput.h"
#include "djstring.h"
#include "config.h"
#include "djgraph.h"
#include "graph.h"
extern void DaveCleanup();
static int paused=0,stopping=0,muted=1,ready=0;
static Uint64 pauseStart=0,pauseTotal=0;
static Mix_Music *music=nullptr;
static std::string wanted;
extern "C" {
EMSCRIPTEN_KEEPALIVE void oga_release(){SDL_ResetKeyboard();SDL_FlushEvents(SDL_KEYDOWN,SDL_MOUSEWHEEL);std::memset(g_iKeys,0,sizeof(g_iKeys));std::memset(g_iKeysLast,0,sizeof(g_iKeysLast));}
EMSCRIPTEN_KEEPALIVE void oga_pause(int value){oga_release();if(value&&!paused)pauseStart=SDL_GetTicks64();if(!value&&paused)pauseTotal+=SDL_GetTicks64()-pauseStart;paused=value!=0;}
EMSCRIPTEN_KEEPALIVE int oga_paused(){return paused;}
EMSCRIPTEN_KEEPALIVE void oga_mute(int value){muted=value!=0;}
EMSCRIPTEN_KEEPALIVE void oga_stop(){stopping=1;oga_pause(0);}
EMSCRIPTEN_KEEPALIVE void oga_checkpoint(){/* Native Save Game owns checkpoint timing. */}
Uint64 oga_ticks(){return (paused?pauseStart:SDL_GetTicks64())-pauseTotal;}
void oga_sleep(unsigned ms){
 if(!ready){ready=1;EM_ASM(if(Module.onGameReady)Module.onGameReady(););}
 do{emscripten_sleep(paused?50:(ms?ms:1));if(stopping){Mix_HaltMusic();if(music){Mix_FreeMusic(music);music=nullptr;}DaveCleanup();Mix_CloseAudio();SDL_Quit();emscripten_force_exit(0);}if(paused&&pVisMain)djgFlip(pVisMain,nullptr,false);}while(paused);
}
static void gate(void*,Uint8* stream,int length){if(muted||paused||stopping)std::memset(stream,0,length);}
void oga_audio_install(){Mix_SetPostMix(gate,nullptr);}
void oga_request_music(const char* path){if(wanted==path)return;wanted=path;Mix_HaltMusic();if(music){Mix_FreeMusic(music);music=nullptr;}EM_ASM(if(Module.requestMusic)Module.requestMusic(UTF8ToString($0));,path);}
EMSCRIPTEN_KEEPALIVE int oga_music_ready(const char* path){if(wanted!=path||stopping)return 0;if(music){Mix_HaltMusic();Mix_FreeMusic(music);}music=Mix_LoadMUS(path);if(!music)return 0;return Mix_FadeInMusic(music,-1,500)==0;}
}
#ifdef OGA_DIAGNOSTIC
#include <cstdio>
#include "hero.h"
extern bool g_bGameRunning;
extern "C" EMSCRIPTEN_KEEPALIVE const char* oga_state(){static char b[300];int held=0;for(int v:g_iKeys)held+=v!=0;std::snprintf(b,sizeof(b),"{\"x\":%d,\"small\":%d,\"y\":%d,\"offset\":%d,\"mode\":%d,\"held\":%d,\"running\":%d,\"paused\":%d,\"music\":%d}",g_Player.x,g_Player.x_small,g_Player.y,g_Player.y_offset,g_Player.hero_mode,held,g_bGameRunning,paused,Mix_PlayingMusic());return b;}
#endif
