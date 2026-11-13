"""Public helper: make only the synthetic numerical phantom data."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mexmfa_demo.core import make_synthetic_dataset

if __name__ == '__main__':
    out = Path(__file__).resolve().parents[1] / 'data' / 'synthetic_af4.npz'
    make_synthetic_dataset(out)
    print(out)
