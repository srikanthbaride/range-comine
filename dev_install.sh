
#!/usr/bin/env bash
set -euo pipefail
python -m pip install -U pip
pip install -e .
echo "Installed range-comine in editable mode."
