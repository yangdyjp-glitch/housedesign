from pathlib import Path
import hashlib, json, re, subprocess, sys, yaml

ROOT=Path(__file__).resolve().parents[1]
SKILLS=Path.home()/'.codex/skills'
NAMES=['interior-design-expert','moodboard-aesthetic-iteration','interior-designer','xiong-interior-design','interior-design-visualizer','home-design-director']
VALIDATOR=SKILLS/'.system/skill-creator/scripts/quick_validate.py'
rows=[]
for name in NAMES:
    folder=SKILLS/name;skill=(folder/'SKILL.md').read_text(encoding='utf-8')
    metadata=yaml.safe_load(skill.split('---',2)[1]);assert metadata['name']==name
    assert '[TODO' not in skill
    missing=[]
    for target in re.findall(r'\]\(([^)]+)\)',skill):
        if '://' not in target and not (folder/target).exists():missing.append(target)
    assert not missing,missing
    ui=yaml.safe_load((folder/'agents/openai.yaml').read_text(encoding='utf-8'))['interface']
    assert 25<=len(ui['short_description'])<=64,(name,len(ui['short_description']))
    assert '$'+name in ui['default_prompt']
    result=subprocess.run([sys.executable,'-X','utf8',str(VALIDATOR),str(folder)],capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,(name,result.stdout,result.stderr)
    row=dict(name=name,path=str(folder),validation=result.stdout.strip(),references_resolved=True,ui_prompt_valid=True,
             skill_sha256=hashlib.sha256((folder/'SKILL.md').read_bytes()).hexdigest(),session_discovery='pending next normal Codex turn; not hot-loaded in this turn')
    rows.append(row)
(ROOT/'logs/skill-validation.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=True,indent=2))
