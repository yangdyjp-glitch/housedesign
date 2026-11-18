"""Read-only project integrity check; standard Python 3, no packages/network.

Use --baseline only on initial restoration of the 2026-11-18 design state.
Later legitimate design updates should be checked against their active pointers.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


BASELINE = {
    'model': '0be76a9211d7130e1ad52aa642049a48ede6e5cb468f04dd2eee097825bec450',
    'geometry': 'd0e845b52223128eefbb7636a9c1ad105479d8aef9917a5d98b56d68dd9fbb6c',
    'style': '42c9fc094e271d5f816061513ec804835c1fffe6094bfbe8b4d60c30b364390b',
}
BASE_COMMIT = '323f294aecf255b77f2262af95bf626e17d09b87'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument('--baseline', action='store_true')
    args = ap.parse_args()
    root = args.root.resolve()
    checks = []

    def check(name, ok, detail=None):
        checks.append({'check': name, 'passed': bool(ok), 'detail': detail})

    def within(relative):
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Project pointer escaped the repository: ' + relative)
        return path

    def digest(path):
        h = hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                h.update(block)
        return h.hexdigest()

    def git(*cmd):
        return subprocess.run(['git', '-C', str(root), *cmd],
                              capture_output=True, text=True, encoding='utf-8', errors='replace')

    try:
        a = json.loads(within('06_blender/active-model.json').read_text(encoding='utf-8'))
        targets = {
            'model': ('06_blender/' + a['filename'], a['model_sha256']),
            'geometry': (a['geometry'], a['geometry_sha256']),
            'style': (a['style'], a['style_sha256']),
        }
        for kind, (rel, expected) in targets.items():
            path = within(rel)
            actual = digest(path) if path.is_file() else None
            check(kind + '_hash_matches_active', actual == expected, {'path': rel, 'sha256': actual})
            if args.baseline:
                check(kind + '_matches_handoff_baseline', actual == BASELINE[kind])

        geo = json.loads(within(a['geometry']).read_text(encoding='utf-8'))
        ids = [q['id'] for q in geo.get('furnitureObjects', [])]
        check('unique_furniture_assemblies', len(ids) == len(set(ids)), len(ids))
        check('furniture_count_matches_active', len(ids) == a['furniture_count'])
        check('millimetre_units', geo.get('units') == 'mm')
        check('geometry_alias_matches_active', digest(within('02_geometry/geometry-master.json')) == a['geometry_sha256'])
        if args.baseline:
            check('complete_v20_not_early_integration', a.get('revision') == 20 and a.get('implementation_phase') == 'full-design')
            check('baseline_28_furniture', len(ids) == 28)
            check('baseline_63_source_walls', len(geo['walls']) == 63, len(geo['walls']))
            check('baseline_12_glass', len(geo['glass']) == 12, len(geo['glass']))
            check('baseline_furniture_positions', all(
                next((f.get('x'), f.get('z')) for f in geo['furnitureObjects'] if f['id'] == key) == val
                for key, val in {'sofa-modular': (3100,1400),'side-table': (2550,2850),
                                 'ottoman': (3200,4450),'master-bed': (8645,1826)}.items()))

        entries = [a.get('interactive_model'), a.get('current_perspective_renders'), a.get('panorama_tour')]
        for rel in entries:
            check('active_delivery_exists', bool(rel) and within(rel).is_file(), rel)
        if args.baseline:
            for rel in ['09_delivery/master-suite-plans-20261110/主卧主卫-修改前.png',
                        '09_delivery/master-suite-plans-20261110/主卧主卫-修改后-v20.png',
                        '09_delivery/house-v20-complete-fragment.html']:
                check('handoff_deliverable_exists', within(rel).is_file(), rel)

        present = json.loads(within('06_blender/active-presentation.json').read_text(encoding='utf-8'))
        # Metadata is nested in some earlier versions. Use only actually
        # present pointer values, instead of assuming a new schema.
        check('presentation_metadata_readable', isinstance(present, dict))
        if args.baseline:
            for rel in ['living', 'dining', 'balcony', 'entry']:
                check('native_pano_exists', within('07_renders/v20-complete-native/' + rel + '-pano-native.png').is_file(), rel)

        try:
            head = git('rev-parse', 'HEAD')
            check('git_checkout_readable', head.returncode == 0, head.stdout.strip())
            shallow = git('rev-parse', '--is-shallow-repository')
            check('not_shallow_clone', shallow.returncode == 0 and shallow.stdout.strip() == 'false')
            if args.baseline:
                ancestry = git('merge-base', '--is-ancestor', BASE_COMMIT, 'HEAD')
                check('contains_uploaded_complete_design_commit', ancestry.returncode == 0, BASE_COMMIT)
            status = git('status', '--porcelain')
            git_state = {'head': head.stdout.strip(), 'working_tree_clean': not status.stdout.strip(),
                         'remote': git('remote', 'get-url', 'origin').stdout.strip()}
        except FileNotFoundError:
            git_state = {'error': 'Git executable not found'}
            check('git_available', False)

        report = {'status': 'passed' if all(q['passed'] for q in checks) else 'failed',
                  'root': str(root), 'mode': 'handoff-baseline' if args.baseline else 'current-active',
                  'git': git_state, 'checks': checks,
                  'limits': 'Read-only hashes, source counts, positions and file existence; no Blender connection, render, browser or headset test.'}
    except Exception as exc:
        report = {'status': 'failed', 'root': str(root), 'checks': checks, 'error': str(exc)}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
