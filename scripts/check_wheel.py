"""Smoke-test package contents outside the checkout, without backend credentials."""
import pathlib
import subprocess
import sys
import tempfile
import venv


def main():
    wheels = list(pathlib.Path('dist').glob('*.whl'))
    if len(wheels) != 1:
        raise SystemExit('Expected exactly one wheel in dist; use a clean build directory.')
    wheel = wheels[0].resolve()
    with tempfile.TemporaryDirectory(prefix='arcticdb-wheel-') as temporary:
        root = pathlib.Path(temporary)
        venv.EnvBuilder(with_pip=True).create(root / 'venv')
        python = root / 'venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        subprocess.run([str(python), '-m', 'pip', 'install', '--no-deps', str(wheel)],
                       cwd=root, check=True)
        subprocess.run([str(python), '-I', '-c', '''
from importlib.metadata import distribution
from pathlib import Path
import arcticdb_mcp.registry as registry
package = Path(registry.__file__).parent
assert 'site-packages' in str(package), package
for relative in ('main.py', '__main__.py', 'tools/batch_tools.py', 'utils/serialization.py'):
    assert (package / relative).is_file(), relative
dist = distribution('arcticdb-mcp')
assert any(e.name == 'arcticdb-mcp' and e.value == 'arcticdb_mcp.main:main'
           for e in dist.entry_points)
print('Installed wheel contents and entry point verified.')
'''], cwd=root, check=True)


if __name__ == '__main__':
    main()
