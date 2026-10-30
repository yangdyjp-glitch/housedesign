"""User-invoked launcher: reveal the managed model window rather than opening a second copy."""
from pathlib import Path
import json, sys, time
import win32con, win32gui, win32process
from mcp_launch import ensure_bridge, ROOT

ensure_bridge()
info=json.loads((ROOT/'logs/blender-bridge-process.json').read_text(encoding='utf-8'))
target_pid=info['pid'];windows=[]
def collect(handle,unused):
    thread,pid=win32process.GetWindowThreadProcessId(handle)
    if pid==target_pid and win32gui.GetClassName(handle)=='GHOST_WindowClass':windows.append(handle)
for _ in range(20):
    win32gui.EnumWindows(collect,None)
    if windows:break
    time.sleep(0.2)
if not windows:
    raise RuntimeError('未找到本项目的 Blender 窗口；请查看 logs/blender-bridge.log。')
if '--check' in sys.argv:
    print('MODEL_WINDOW_READY '+json.dumps(dict(pid=target_pid,windows=len(windows),shown=False)))
else:
    for handle in windows:
        win32gui.ShowWindow(handle,win32con.SW_RESTORE)
        try:win32gui.SetForegroundWindow(handle)
        except Exception:pass
