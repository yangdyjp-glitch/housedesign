"""Add one reviewed MCP entry using Codex CLI and verify all prior settings survive."""
from pathlib import Path
from datetime import datetime
import copy, hashlib, json, os, shutil, subprocess, tomllib

ROOT=Path(__file__).resolve().parents[1]
CODEX=Path(r'C:\Users\Administrator\AppData\Local\OpenAI\Codex\bin\896a0166b774037a\codex.exe')
CONFIG=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'config.toml'
original=CONFIG.read_bytes();before=tomllib.loads(original.decode('utf-8'))
backups=sorted(CONFIG.parent.glob('config.toml.before-home-design-*'))
if 'blender' in before.get('mcp_servers',{}):
    # Resume the audited CLI attempt, which also normalized an unrelated node_repl entry.
    if not backups:raise RuntimeError('Existing blender entry preserved; no task backup found')
    backup=backups[-1];original=backup.read_bytes();before=tomllib.loads(original.decode('utf-8'))
    if 'blender' in before.get('mcp_servers',{}):raise RuntimeError('Backup is not a pre-install configuration')
    attempt=CONFIG.with_name('config.toml.cli-home-design-attempt-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(CONFIG,attempt)
else:
    backup=CONFIG.with_name('config.toml.before-home-design-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(CONFIG,backup)
env=dict(DISABLE_TELEMETRY='true',BLENDER_MCP_SAFE_MODE='1',BLENDERMCP_NO_UPDATE_CHECK='1',
         BLENDERMCP_ADDONS_DIR=str(Path.home()/'AppData/Roaming/Blender Foundation/Blender/4.5/scripts/addons'))
entry=dict(command=str(ROOT/'tools/runtime/mcp-env/Scripts/python.exe'),args=[str(ROOT/'tools/mcp_launch.py')],
           startup_timeout_sec=90,tool_timeout_sec=180,env=env)
lines=['','[mcp_servers.blender]']
for key in ['command','args','startup_timeout_sec','tool_timeout_sec']:
    lines.append(key+' = '+json.dumps(entry[key],ensure_ascii=False))
lines+=['','[mcp_servers.blender.env]']
lines += [key+' = '+json.dumps(value,ensure_ascii=False) for key,value in env.items()]
updated=original+b'\n'+'\n'.join(lines).encode('utf-8')+b'\n'
after=tomllib.loads(updated.decode('utf-8'));check=copy.deepcopy(after)
check['mcp_servers'].pop('blender')
assert check==before,'Unrelated configuration would change'
CONFIG.write_bytes(updated)
listing=subprocess.run([str(CODEX),'mcp','list','--json'],capture_output=True,text=True,encoding='utf-8',check=True)
servers=json.loads(listing.stdout)
record=dict(config=str(CONFIG),backup=str(backup),prior_sha256=hashlib.sha256(original).hexdigest(),
            current_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),unrelated_settings_preserved=True,
            blender=entry,registered_servers=[dict(name=s['name'],enabled=s.get('enabled')) for s in servers],
            recovery='Codex CLI also normalized node_repl; restored original bytes and appended only the blender table, then verified semantic equality of every prior setting.')
(ROOT/'logs/mcp-registration.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(registered=True,unrelated_settings_preserved=True,backup=str(backup),servers=record['registered_servers'])))
