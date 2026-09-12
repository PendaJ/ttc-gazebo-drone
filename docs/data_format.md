# Dataset format

## `frames.csv`

| Column | Description |
|---|---|
| `frame_index` | zero-based saved-frame index |
| `filename` | PNG filename |
| `ros_sec` | ROS image timestamp seconds |
| `ros_nanosec` | ROS image timestamp nanoseconds |
| `timestamp_ns` | combined image timestamp in nanoseconds |
| `timestamp_s` | image timestamp in seconds |
| `robot_x_m` | latest simulator odometry x position |
| `robot_y_m` | latest simulator odometry y position |
| `displacement_m` | absolute longitudinal displacement from capture start |

## `experiment_summary.txt`

Human-readable run metadata including commanded speed, capture distance,
takeoff settings, final position, frame count, capture duration, and measured
frame rate.

## Synchronization note

The current recorder stores the latest odometry sample available when an image
callback is processed. This is appropriate for the original simulator setup,
but it is not a general exact-time interpolation mechanism. If tighter temporal
alignment is required in a future experiment, interpolate odometry to the image
header timestamp.
