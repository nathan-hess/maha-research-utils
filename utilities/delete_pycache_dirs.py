import pathlib
import shutil

# Get location of project directory
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

# Get location of any `__pycache__/` directories
pycache_dirs = [path for path in BASE_DIR.glob('**/__pycache__/')
                if path.is_dir()]
num_pycache_dirs = len(pycache_dirs)

# Remove `__pycache__/` directories
if num_pycache_dirs > 0:
    print(f'Removing {num_pycache_dirs} `__pycache__/` '
          f'director{"y" if num_pycache_dirs == 1 else "ies"}...')

    for path in pycache_dirs:
        print(f'  {path}')
        shutil.rmtree(path)
else:
    print('Did not find any `__pycache__/` directories to remove')
