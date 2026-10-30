"""Merge only the three latest placement deltas into v12 for the VR presentation.

No Blender file, active-model pointer or historical source is modified here.
The conversation input is a parsed summary, not a fabricated raw widget export.
"""
from pathlib import Path
from copy import deepcopy
from itertools import combinations
import hashlib
import json
import math
import sys

ROOT = Path(r'D:\AI-Yang.cn\HomeDesign')
SOURCE = ROOT / '02_geometry/geometry-master-v12.json'
DEST = ROOT / '02_geometry/geometry-master-v13.json'
STYLE_SOURCE = ROOT / '05_style/modern-japanese-v08.json'
STYLE_DEST = ROOT / '05_style/modern-japanese-v09.json'
INPUT = ROOT / '03_layout/widget-layout-v10-user-latest-v13-input.json'
LEDGER = ROOT / 'logs/v13-source-ledger.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def overlaps(a, b):
    return all(a[k] < b[k] + b[n] - .01 and a[k] + a[n] > b[k] + .01
               for k, n in [('x', 'w'), ('z', 'd'), ('y', 'h')])


def furniture_collisions(geom, obstacles):
    return [[a['id'], b['id']] for a in geom['furniture'] for b in obstacles if overlaps(a, b)]


def nearest_plan(point, obstacles):
    x, z, _ = point
    distances = []
    for o in obstacles:
        dx = max(o['x'] - x, 0, x - o['x'] - o['w'])
        dz = max(o['z'] - z, 0, z - o['z'] - o['d'])
        distances.append(dict(id=o['id'], distanceMm=round(math.hypot(dx, dz), 2)))
    return sorted(distances, key=lambda row: row['distanceMm'])[:3]


assert not DEST.exists() or '--replace-draft' in sys.argv, 'Refusing to overwrite a completed v13.'
assert not STYLE_DEST.exists() or '--replace-draft' in sys.argv
source_hash = sha(SOURCE)
style_source_hash = sha(STYLE_SOURCE)
old = json.loads(SOURCE.read_text(encoding='utf-8'))
data = deepcopy(old)
assert old['revision'] == 12 and len(old['furnitureObjects']) == 23

# Only the current absolute values of these three objects were supplied in the
# current conversation. Historical snapshot x/dx values must not be replayed.
target = {
    'sofa-modular': dict(x=3100, z=1300),
    'ottoman': dict(x=3200, z=4350),
    'side-table': dict(x=2550, z=2650),
}
roots = {q['id']: q for q in old['furnitureObjects']}
parsed = dict(
    revision=10,
    units='mm',
    source='conversation functions.untrusted_input revision10 summarized data',
    sourceFidelity='parsed summary of three objects only; not the raw or complete widget snapshot',
    baselineGeometry=SOURCE.relative_to(ROOT).as_posix(),
    baselineGeometrySHA256=source_hash,
    furniturePositions=[],
)
deltas = {}
for gid, current in target.items():
    baseline = {k: roots[gid][k] for k in ['x', 'z']}
    delta = {k: current[k] - baseline[k] for k in ['x', 'z']}
    deltas[gid] = delta
    parsed['furniturePositions'].append(dict(id=gid, current=current, v12Baseline=baseline, delta=delta))
dump(INPUT, parsed)

data.update(revision=13, project_revision=13, title='房屋主模型 · 四区360度全景观察')
data['compatiblePlacementRevisions'] = sorted(set(old['compatiblePlacementRevisions'] + [12]))
data['placementBaselinesByRevision']['12'] = {
    q['id']: dict(x=q['x'], z=q['z']) for q in old['furnitureObjects']
}
data['previousPlacements'] = deepcopy(data['placementBaselinesByRevision']['12'])
old_ten_baseline = deepcopy(data['placementBaselinesByRevision']['10'])
for gid, current in target.items():
    # Consume these already-applied offsets when the same old revision-10 state
    # is restored later. The remaining historic revision-10 baseline is intact.
    data['placementBaselinesByRevision']['10'][gid] = deepcopy(current)

for q in data['furnitureObjects']:
    if q['id'] in deltas:
        delta = deltas[q['id']]
        for axis in ['x', 'z']:
            q[axis] += delta[axis]
            q['meshBoundsMm'][axis] += delta[axis]
        q['placement_source'] = INPUT.relative_to(ROOT).as_posix()
        q['placement_revision_13_delta_mm'] = delta
for q in data['furniture']:
    if q['parent'] in deltas:
        for axis in ['x', 'z']:
            q[axis] += deltas[q['parent']][axis]

# The tea set stays fixed; its relation to the newly moved sofa changes by 100.
data['features']['balconyTeaSet']['sofaGapMm'] = 330
data['assumptions'].append(
    'v13只合并本轮收到的旧revision10快照摘要增量：沙发z1300、脚凳z4350、茶几z2650；'
    'x不变，其他20件及v12门厅、电视墙、矮茶席、窗帘与灯光方案保持。三件偏移已烘焙，重复恢复不再次叠加。'
)
data['provenance'].update(
    revision=13,
    baseline=SOURCE.relative_to(ROOT).as_posix(),
    baseline_sha256=source_hash,
    layout='v12 complete 23-object model plus exactly three summarized user placement deltas',
    layout_source=INPUT.relative_to(ROOT).as_posix(),
    layout_source_sha256=sha(INPUT),
)
data['provenance']['new_user_decisions'] = old['provenance'].get('new_user_decisions', []) + [
    '餐厅、门厅、客厅、阳台制作可360度观察的VR影像'
]

stable_keys = ['floor', 'walls', 'glass', 'removed', 'openings', 'rooms', 'dimensions', 'beams',
               'measurements', 'furnitureMaterials', 'style', 'windowParts', 'doorParts',
               'detailParts', 'referenceParts', 'curtainParts']
assert all(data[key] == old[key] for key in stable_keys)
assert len(data['furnitureObjects']) == len(old['furnitureObjects']) == 23
assert len(data['furniture']) == len(old['furniture'])
for before, after in zip(old['furnitureObjects'], data['furnitureObjects']):
    assert before['id'] == after['id']
    if before['id'] not in deltas:
        assert before == after
for before, after in zip(old['furniture'], data['furniture']):
    expected = deepcopy(before)
    if before['parent'] in deltas:
        for axis in ['x', 'z']:
            expected[axis] += deltas[before['parent']][axis]
    assert after == expected

ff = [[a['id'], b['id']] for a, b in combinations(data['furniture'], 2)
      if a['parent'] != b['parent'] and overlaps(a, b)]
fw = furniture_collisions(data, data['walls'])
fg = furniture_collisions(data, data['glass'] + data['windowParts'])
fr = furniture_collisions(data, [p for p in data['referenceParts'] if p.get('collidable')])
fd = furniture_collisions(data, data['detailParts'])
door_checks = {}
for opened in [False, True]:
    door = deepcopy(data['doorParts'])
    if opened:
        for part in door:
            if part.get('movingLeaf') == 'left':
                part['x'] += data['features']['kitchenSlidingDoor']['openTravelMm']
    door_checks['open' if opened else 'closed'] = furniture_collisions(data, door)
curtain_checks = {}
for opened in [False, True]:
    curtain = deepcopy(data['curtainParts'])
    if opened:
        for part in curtain:
            part.update(part['openPlan'])
    curtain_checks['open' if opened else 'closed'] = furniture_collisions(data, curtain)
curtain_sweep = furniture_collisions(data, [dict(
    id='v12-curtain-reserved-sweep',
    **data['features']['referenceRefinement']['curtain']['reservedSweepMm'],
)])
collision_results = dict(
    furnitureFurniture=ff, furnitureWall=fw, furnitureGlassAndWindow=fg,
    furnitureCollidableReference=fr, furniturePublicDetails=fd,
    kitchenDoor=door_checks, curtain=curtain_checks, curtainReservedSweep=curtain_sweep,
    method='Strict 3D axis-aligned component-envelope intersection; 0.01 mm tolerance; not site clearance certification',
)
assert not any([ff, fw, fg, fr, fd, curtain_sweep] + list(door_checks.values()) + list(curtain_checks.values())), collision_results

camera_specs = [
    ('entry', '门厅', [635, 10100, 1600], [635, 11000, 1200]),
    ('dining', '餐厅', [1100, 8000, 1600], [2680, 8100, 1050]),
    ('living', '客厅', [1800, 4500, 1600], [4200, 3000, 1050]),
    ('balcony', '阳台', [2050, 850, 1600], [3650, 620, 500]),
]
obstacles = data['furnitureObjects'] + [p for p in data['walls'] + data['referenceParts'] if p.get('y', 0) < 1700]
cameras = []
for cid, name, position, target_point in camera_specs:
    nearest = nearest_plan(position, obstacles)
    assert nearest[0]['distanceMm'] > 0
    cameras.append(dict(id=cid, name=name, positionPlanXZYmm=position, targetPlanXZYmm=target_point,
                        posture='standing', nearestPlanObstacles=nearest))

dump(DEST, data)
geometry_hash = sha(DEST)
style = json.loads(STYLE_SOURCE.read_text(encoding='utf-8'))
before_style = deepcopy(style)
style.update(version='v13-style-v09', geometry_base=DEST.relative_to(ROOT).as_posix(), geometry_sha256=geometry_hash)
assert {k: v for k, v in style.items() if k not in ['version', 'geometry_base', 'geometry_sha256']} == {
    k: v for k, v in before_style.items() if k not in ['version', 'geometry_base', 'geometry_sha256']
}
dump(STYLE_DEST, style)

migration_checks = {}
new_roots = {q['id']: q for q in data['furnitureObjects']}
for gid, current in target.items():
    baseline = data['placementBaselinesByRevision']['10'][gid]
    restored = {k: new_roots[gid][k] + current[k] - baseline[k] for k in ['x', 'z']}
    assert restored == current
    migration_checks[gid] = dict(repeatedRevision10Restore=restored, noDoubleOffset=True)
assert sha(SOURCE) == source_hash and sha(STYLE_SOURCE) == style_source_hash
ledger = dict(
    revision=13,
    sourceGeometry=SOURCE.relative_to(ROOT).as_posix(), sourceGeometrySHA256=source_hash,
    sourceStyle=STYLE_SOURCE.relative_to(ROOT).as_posix(), sourceStyleSHA256=style_source_hash,
    parsedConversationInput=INPUT.relative_to(ROOT).as_posix(), parsedConversationInputSHA256=sha(INPUT),
    geometry=DEST.relative_to(ROOT).as_posix(), geometry_sha256=geometry_hash,
    style=STYLE_DEST.relative_to(ROOT).as_posix(), style_sha256=sha(STYLE_DEST),
    changedFurnitureIds=list(deltas), placementDeltaMm=deltas,
    furnitureCount=23, furnitureComponentCount=len(data['furniture']),
    allOtherObjectsAndGeometryPreserved=True, materialsAndStyleIntentPreserved=True,
    oldRevision10BaselineBeforeConsumption=old_ten_baseline,
    oldRevision10BaselineAfterConsumption=data['placementBaselinesByRevision']['10'],
    revision12Baseline=data['placementBaselinesByRevision']['12'],
    migrationPolicy='Current revision-13 placements + (snapshot absolute placement - consumed baseline); ignore removed ids and retain current-only ids',
    migrationChecks=migration_checks,
    collisions=collision_results,
    cameras=cameras,
    cameraNotes=['Plan distances use provisional proxy envelopes, not field measurements.',
                 'Balcony point is left of the low tea set, never at the table centre.',
                 'Four monocular equirectangular nodes support looking around and hotspot transitions; no stereo/6DoF claim.'],
    budgetConsidered=False, privateBoundariesChanged=False,
    activeModelPointerChanged=False, blenderFileChanged=False,
)
dump(LEDGER, ledger)
print('V13_GEOMETRY_READY', len(data['furnitureObjects']), geometry_hash)
print('V13_STYLE_READY', sha(STYLE_DEST))
print('V13_COLLISIONS_CLEAR', json.dumps({k: v for k, v in collision_results.items() if k != 'method'}))
