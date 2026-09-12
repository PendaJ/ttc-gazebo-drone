# Experiment workflow

The controller implements a simple state machine:

1. wait for simulator odometry;
2. command vertical takeoff;
3. hover for a configurable interval;
4. establish the forward-motion reference position;
5. start image capture;
6. command a constant forward velocity;
7. stop when the configured longitudinal displacement is reached;
8. write the run summary.

The default parameter file is:

`src/drone_ttc_control/config/experiment.yaml`

The main parameters are:

| Parameter | Meaning | Default |
|---|---|---:|
| `takeoff_speed` | vertical command during takeoff | 0.30 m/s |
| `takeoff_altitude` | height increase from initial z | 0.45 m |
| `hover_time` | stabilization interval | 3.0 s |
| `forward_speed` | commanded forward speed | 0.50 m/s |
| `travel_distance` | longitudinal capture distance | 2.0 m |
| `data_root` | root directory for generated runs | `~/ttc_gazebo_drone_data` |

## Output

Runs are grouped by commanded speed, for example:

```text
~/ttc_gazebo_drone_data/
└── 0.5mps/
    └── run_01/
        ├── frames.csv
        ├── experiment_summary.txt
        └── images/
```

The CSV associates each saved image with the latest available simulator
odometry and records longitudinal displacement from the capture start point.
