"""Local MCP entrypoint: ensure the managed Blender bridge, then run upstream MCP."""
from pathlib import Path
import json, os, socket, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
BLENDER=ROOT/'tools/runtime/blender/blender-4.5.15-windows-x64/blender.exe'
SERVER=ROOT/'tools/runtime/mcp-env/Scripts/mcp-for-blender.exe'
ENV=os.environ.copy()
ENV.update(DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',BLENDER_HOST='127.0.0.1',BLENDER_PORT='9876',PYTHONUTF8='1')

def listening():
    try:
        with socket.create_connection(('127.0.0.1',9876),timeout=0.4):return True
    except OSError:return False

def ensure_bridge():
    if listening():return
    # The upstream addon requires Blender's GUI event loop; a hidden window keeps it alive.
    startup=subprocess.STARTUPINFO()
    startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow=0
    args=[str(BLENDER),'--disable-autoexec','--no-window-focus']
    manifest=ROOT/'06_blender/active-model.json'
    active=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
    main=(ROOT/'06_blender'/active.get('filename','home-main-v05.blend')).resolve()
    if not main.is_relative_to((ROOT/'06_blender').resolve()):raise RuntimeError('Active model path is outside project models')
    if main.exists():args.append(str(main))
    args+=['--python',str(ROOT/'tools/blender_bridge_startup.py')]
    with (ROOT/'logs/blender-bridge.log').open('ab') as log:
        process=subprocess.Popen(args,cwd=ROOT,env=ENV,stdout=log,stderr=log,startupinfo=startup,
                                 creationflags=subprocess.DETACHED_PROCESS)
    (ROOT/'logs/blender-bridge-process.json').write_text(json.dumps(dict(pid=process.pid,executable=str(BLENDER),started=time.time()),indent=2),encoding='utf-8')
    for _ in range(100):
        if listening():return
        if process.poll() is not None:raise RuntimeError('Blender exited; see logs/blender-bridge.log')
        time.sleep(0.3)
    raise RuntimeError('Blender bridge did not listen on 127.0.0.1:9876 within 30 seconds')

if __name__=='__main__':
    ensure_bridge()
    if '--bridge-only' in sys.argv:
        print('Blender bridge ready at 127.0.0.1:9876')
    else:
        # Do not print to stdout: it belongs exclusively to the MCP transport.
        raise SystemExit(subprocess.call([str(SERVER),'--host','127.0.0.1','--port','9876'],env=ENV,cwd=ROOT))
