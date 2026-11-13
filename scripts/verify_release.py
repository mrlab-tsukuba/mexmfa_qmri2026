"""Release guardrails: execute the demo and reject obvious disclosure mistakes."""
from pathlib import Path
import marshal, subprocess, sys, types

root = Path(__file__).resolve().parents[1]
forbidden_suffixes = {'.img', '.flt', '.mhd', '.raw', '.dat', '.nii', '.nii.gz'}
allowed_py = {root / 'scripts' / 'generate_synthetic_data.py', root / 'scripts' / 'run_demo.py', root / 'scripts' / 'verify_release.py', root / 'scripts' / 'audit_provenance.py', root / 'scripts' / 'audit_operators_equivalence.py'}
violations = []
for p in root.rglob('*'):
    if not p.is_file(): continue
    name = p.name.lower()
    if p.suffix.lower() in forbidden_suffixes: violations.append(f'private-like imaging file: {p.relative_to(root)}')
    if p.suffix == '.py' and p not in allowed_py: violations.append(f'unexpected Python source: {p.relative_to(root)}')
    if any(token in name for token in ('credential','secret','password','token')): violations.append(f'sensitive-looking filename: {p.relative_to(root)}')
    if p.suffix == '.pyc':
        try:
            with p.open('rb') as handle:
                handle.read(16)
                code = marshal.load(handle)
            pending = [code]
            while pending:
                item = pending.pop()
                if isinstance(item, types.CodeType):
                    if any(marker in item.co_filename.lower() for marker in ('/workdir/', '\\workdir\\', '20260310@v2', '/data/', '\\data\\')):
                        violations.append(f'non-public source path in bytecode: {p.relative_to(root)}')
                        break
                    pending.extend(constant for constant in item.co_consts if isinstance(constant, types.CodeType))
        except Exception as exc:
            violations.append(f'could not inspect bytecode {p.relative_to(root)}: {exc}')
if violations:
    print('\n'.join(violations)); raise SystemExit(1)
completed = subprocess.run([sys.executable, str(root / 'scripts' / 'run_demo.py')], cwd=root, check=False)
if completed.returncode: raise SystemExit(completed.returncode)
required = ('reconstructed_images_zssl.npy', 'M0_zssl.npy', 'T1_s_zssl.npy', 'T2star_s_zssl.npy', 'image_metrics_zssl.csv', 'loss_zssl.csv')
missing = [f for f in required if not (root / 'results' / f).exists()]
if missing: raise SystemExit('missing outputs: ' + ', '.join(missing))
print('release verification passed')
