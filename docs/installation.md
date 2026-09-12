# Installation

## Tested environment

The development workspace was tested with:

- Ubuntu 22.04-class environment
- ROS 2 Humble
- Gazebo Harmonic 8.x
- `ros_gz` bridge packages
- Python 3
- OpenCV / `cv_bridge`

The exact combination of ROS 2 Humble and Gazebo Harmonic may require the
appropriate Gazebo/ROS package repository for your system.

## Build

Clone into a directory of your choice, then build from the repository root:

```bash
source /opt/ros/humble/setup.bash
cd ttc-gazebo-drone
colcon build --symlink-install
source install/setup.bash
```

## Required ROS packages

The repository expects the packages declared by `package.xml`, particularly:

- `ros_gz_sim`
- `ros_gz_bridge`
- `rclpy`
- `cv_bridge`
- `geometry_msgs`
- `sensor_msgs`
- `nav_msgs`

Use `rosdep` where supported:

```bash
rosdep install --from-paths src --ignore-src -r -y
```
