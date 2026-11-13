"""Public helper: run the compiled production MExMFA ZS-SSL pathway."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mexmfa_demo.core import DemoConfig, make_synthetic_dataset
from mexmfa_zssl import run_production_zssl

root = Path(__file__).resolve().parents[1]
data = root / 'data' / 'synthetic_af4_zssl.npz'
if not data.exists(): make_synthetic_dataset(data, DemoConfig(matrix=24))
result = run_production_zssl(data, root / 'results', epochs=2, seed=100, device='cpu')
mean = {k: sum(row[k] for row in result['metrics']) / len(result['metrics']) for k in ('nrmse','psnr_db','ssim')}
print(mean)
