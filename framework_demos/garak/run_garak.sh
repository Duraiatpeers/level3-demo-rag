#!/bin/bash
# Run both Garak scans against the local PX Service Assistant, then apply the PX rules.
# Usage:  PX_KEY=<your TRAINING_API_KEY> bash run_garak.sh
# Needs the app running on localhost:8000 and Garak installed (see ../README.md).
set -u
cd "$(dirname "$0")"
export REST_API_KEY="${PX_KEY:?Set PX_KEY to your TRAINING_API_KEY first}"
status=0
for run in px_direct px_indirect; do
  echo "=== garak: $run ==="
  garak --config "$run.yaml" || status=1
  python check_garak_report.py "$run" || status=1
done
exit $status
