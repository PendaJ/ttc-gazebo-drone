#!/usr/bin/env bash
set -euo pipefail

echo "Checking TTC experiment ROS topics..."
for topic in \
  /drone/camera/image_raw \
  /model/x3/odometry \
  /X3/gazebo/command/twist; do
  if ros2 topic list | grep -Fxq "$topic"; then
    echo "[OK] $topic"
  else
    echo "[MISSING] $topic"
  fi
done

echo
echo "Expected camera rate: approximately 30 Hz"
echo "Run manually if desired: ros2 topic hz /drone/camera/image_raw"
