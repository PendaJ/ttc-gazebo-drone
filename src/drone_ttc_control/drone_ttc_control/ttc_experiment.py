#!/usr/bin/env python3

from pathlib import Path
import csv
import time

import cv2
import rclpy

from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class TTCExperiment(Node):

    def __init__(self):
        super().__init__('ttc_experiment')

        # ==========================================================
        # PARAMETERS
        # ==========================================================

        self.declare_parameter('takeoff_speed', 0.30)
        self.declare_parameter('takeoff_altitude', 1.50)
        self.declare_parameter('hover_time', 2.0)

        self.declare_parameter('forward_speed', 0.50)
        self.declare_parameter('travel_distance', 2.0)

        self.declare_parameter(
            'data_root',
            str(Path.home() / 'ttc_gazebo_drone_data')
        )

        self.declare_parameter('run_name', 'auto')

        self.declare_parameter(
            'cmd_topic',
            '/X3/gazebo/command/twist'
        )
        self.declare_parameter(
            'image_topic',
            '/drone/camera/image_raw'
        )
        self.declare_parameter(
            'odom_topic',
            '/model/x3/odometry'
        )

        # ----------------------------------------------------------
        # Read parameters
        # ----------------------------------------------------------

        self.takeoff_speed = float(
            self.get_parameter('takeoff_speed').value
        )

        self.takeoff_altitude = float(
            self.get_parameter('takeoff_altitude').value
        )

        self.hover_time = float(
            self.get_parameter('hover_time').value
        )

        self.forward_speed = float(
            self.get_parameter('forward_speed').value
        )

        self.travel_distance = float(
            self.get_parameter('travel_distance').value
        )

        self.data_root = Path(
            self.get_parameter('data_root').value
        ).expanduser()

        self.run_name = str(
            self.get_parameter('run_name').value
        )

        self.cmd_topic = str(
            self.get_parameter('cmd_topic').value
        )
        self.image_topic = str(
            self.get_parameter('image_topic').value
        )
        self.odom_topic = str(
            self.get_parameter('odom_topic').value
        )

        # ==========================================================
        # PARAMETER VALIDATION
        # ==========================================================

        if self.takeoff_speed <= 0.0:
            raise ValueError('takeoff_speed must be > 0.')

        if self.takeoff_altitude <= 0.0:
            raise ValueError('takeoff_altitude must be > 0.')

        if self.hover_time < 0.0:
            raise ValueError('hover_time cannot be negative.')

        if self.forward_speed <= 0.0:
            raise ValueError('forward_speed must be > 0.')

        if self.travel_distance <= 0.0:
            raise ValueError('travel_distance must be > 0.')

        # ==========================================================
        # AUTOMATIC RUN DIRECTORY
        # ==========================================================

        speed_name = f'{self.forward_speed:.1f}mps'

        speed_dir = self.data_root / speed_name

        speed_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        if self.run_name.lower() == 'auto':

            run_number = 1

            while True:

                candidate = (
                    speed_dir /
                    f'run_{run_number:02d}'
                )

                if not candidate.exists():
                    self.output_dir = candidate
                    break

                run_number += 1

        else:

            self.output_dir = (
                speed_dir /
                self.run_name
            )

            if self.output_dir.exists():

                raise RuntimeError(
                    f'Run already exists: {self.output_dir}'
                )

        # ==========================================================
        # OUTPUT DIRECTORY
        # ==========================================================

        self.image_dir = (
            self.output_dir /
            'images'
        )

        self.image_dir.mkdir(
            parents=True,
            exist_ok=False
        )

        # Match the original TTC Gazebo dataset naming.
        self.csv_path = (
            self.output_dir /
            'frames.csv'
        )

        self.summary_path = (
            self.output_dir /
            'experiment_summary.txt'
        )

        # ==========================================================
        # CSV FILE
        #
        # EXACT SAME STRUCTURE AS TURTLEBOT FILE
        # ==========================================================

        self.csv_file = open(
            self.csv_path,
            'w',
            newline=''
        )

        self.csv_writer = csv.writer(
            self.csv_file
        )

        self.csv_writer.writerow([
            'frame_index',
            'filename',
            'ros_sec',
            'ros_nanosec',
            'timestamp_ns',
            'timestamp_s',
            'robot_x_m',
            'robot_y_m',
            'displacement_m'
        ])

        # ==========================================================
        # ROS INTERFACES
        # ==========================================================

        self.cmd_pub = self.create_publisher(
            Twist,
            self.cmd_topic,
            10
        )

        self.image_sub = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            qos_profile_sensor_data
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            self.odom_topic,
            self.odom_callback,
            qos_profile_sensor_data
        )

        self.cv_bridge = CvBridge()

        # ==========================================================
        # STATE VARIABLES
        # ==========================================================

        self.latest_odom = None

        self.state = 'WAITING_FOR_ODOMETRY'

        self.initial_z = None
        self.target_z = None

        self.hover_start_time = None

        # Position at the instant recording begins
        self.record_start_x = None
        self.record_start_y = None

        self.recording = False

        self.frame_index = 0

        # Capture statistics used for experiment_summary.txt
        self.first_frame_timestamp_ns = None
        self.last_frame_timestamp_ns = None
        self.last_recorded_x = None
        self.last_recorded_y = None
        self.last_recorded_displacement = None

        self.finished = False

        self.last_progress_time = 0.0

        # ==========================================================
        # CONTROL TIMER — 20 Hz
        # ==========================================================

        self.control_timer = self.create_timer(
            0.05,
            self.control_loop
        )

        # ==========================================================
        # STARTUP MESSAGE
        # ==========================================================

        self.get_logger().info(
            '========================================'
        )

        self.get_logger().info(
            'Drone TTC capture-motion experiment'
        )

        self.get_logger().info(
            f'Forward speed: '
            f'{self.forward_speed:.3f} m/s'
        )

        self.get_logger().info(
            f'Travel distance: '
            f'{self.travel_distance:.3f} m'
        )

        self.get_logger().info(
            f'Output: {self.output_dir}'
        )

        self.get_logger().info(
            '========================================'
        )

    # ==============================================================
    # TIMESTAMP UTILITIES
    # ==============================================================

    @staticmethod
    def stamp_to_ns(stamp):

        return (
            int(stamp.sec) * 1_000_000_000
            + int(stamp.nanosec)
        )

    @staticmethod
    def stamp_to_seconds(stamp):

        return (
            float(stamp.sec)
            + float(stamp.nanosec) * 1e-9
        )

    # ==============================================================
    # VELOCITY CONTROL
    # ==============================================================

    def publish_velocity(
        self,
        vx=0.0,
        vy=0.0,
        vz=0.0,
        yaw_rate=0.0
    ):

        msg = Twist()

        msg.linear.x = float(vx)
        msg.linear.y = float(vy)
        msg.linear.z = float(vz)

        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = float(yaw_rate)

        self.cmd_pub.publish(msg)

    def stop_drone(self):

        self.publish_velocity(
            vx=0.0,
            vy=0.0,
            vz=0.0,
            yaw_rate=0.0
        )

    # ==============================================================
    # ODOMETRY CALLBACK
    # ==============================================================

    def odom_callback(self, msg):

        # Store most recent Gazebo ground-truth odometry.
        #
        # It will be associated with the next arriving image.

        self.latest_odom = msg

    # ==============================================================
    # IMAGE CALLBACK
    #
    # ONE IMAGE = ONE CSV ROW
    # ==============================================================

    def image_callback(self, msg):

        if not self.recording:
            return

        if self.latest_odom is None:
            return

        # ----------------------------------------------------------
        # IMAGE TIMESTAMP
        # ----------------------------------------------------------

        stamp = msg.header.stamp

        ros_sec = int(stamp.sec)
        ros_nanosec = int(stamp.nanosec)

        timestamp_ns = self.stamp_to_ns(
            stamp
        )

        timestamp_s = self.stamp_to_seconds(
            stamp
        )

        # ----------------------------------------------------------
        # CURRENT DRONE POSITION
        # ----------------------------------------------------------

        position = (
            self.latest_odom
            .pose
            .pose
            .position
        )

        drone_x = float(position.x)
        drone_y = float(position.y)

        # ----------------------------------------------------------
        # FORWARD DISPLACEMENT
        #
        # Same role as displacement_m in TurtleBot dataset.
        #
        # For this drone experiment, longitudinal x displacement
        # is used rather than total 3-D distance.
        # ----------------------------------------------------------

        if self.record_start_x is None:

            displacement = 0.0

        else:

            displacement = abs(
                drone_x
                - self.record_start_x
            )

        # ----------------------------------------------------------
        # CONVERT ROS IMAGE TO OPENCV
        # ----------------------------------------------------------

        try:

            image = self.cv_bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

        except Exception as exc:

            self.get_logger().error(
                f'Image conversion failed: {exc}'
            )

            return

        # ----------------------------------------------------------
        # SAME FILE-NAMING STYLE AS TURTLEBOT
        # ----------------------------------------------------------

        filename = (
            f'frame_{self.frame_index:06d}_'
            f'{timestamp_ns}.png'
        )

        filepath = (
            self.image_dir /
            filename
        )

        # ----------------------------------------------------------
        # SAVE IMAGE
        # ----------------------------------------------------------

        success = cv2.imwrite(
            str(filepath),
            image
        )

        if not success:

            self.get_logger().error(
                f'Failed to save image: {filepath}'
            )

            return

        # ----------------------------------------------------------
        # WRITE EXACT TURTLEBOT-STYLE CSV ROW
        # ----------------------------------------------------------

        self.csv_writer.writerow([
            self.frame_index,
            filename,
            ros_sec,
            ros_nanosec,
            timestamp_ns,
            timestamp_s,
            drone_x,
            drone_y,
            displacement
        ])

        self.csv_file.flush()

        # Keep capture statistics for experiment_summary.txt.
        if self.first_frame_timestamp_ns is None:
            self.first_frame_timestamp_ns = timestamp_ns

        self.last_frame_timestamp_ns = timestamp_ns
        self.last_recorded_x = drone_x
        self.last_recorded_y = drone_y
        self.last_recorded_displacement = displacement

        self.frame_index += 1

    # ==============================================================
    # EXPERIMENT STATE MACHINE
    # ==============================================================

    def control_loop(self):

        # ----------------------------------------------------------
        # Finished
        # ----------------------------------------------------------

        if self.finished:

            self.stop_drone()
            return

        # ----------------------------------------------------------
        # Wait until ground-truth odometry is available
        # ----------------------------------------------------------

        if self.latest_odom is None:
            return

        position = (
            self.latest_odom
            .pose
            .pose
            .position
        )

        # ==========================================================
        # WAIT FOR ODOMETRY
        # ==========================================================

        if self.state == 'WAITING_FOR_ODOMETRY':

            self.initial_z = float(
                position.z
            )

            self.target_z = (
                self.initial_z
                + self.takeoff_altitude
            )

            self.get_logger().info(
                f'Initial altitude: '
                f'{self.initial_z:.3f} m'
            )

            self.get_logger().info(
                f'Target altitude: '
                f'{self.target_z:.3f} m'
            )

            self.get_logger().info(
                'Takeoff started.'
            )

            self.state = 'TAKEOFF'

            return

        # ==========================================================
        # TAKEOFF
        # ==========================================================

        if self.state == 'TAKEOFF':

            altitude_error = (
                self.target_z
                - position.z
            )

            if altitude_error > 0.02:

                self.publish_velocity(
                    vx=0.0,
                    vy=0.0,
                    vz=self.takeoff_speed
                )

                return

            # Desired altitude reached
            self.stop_drone()

            self.get_logger().info(
                f'Takeoff complete at '
                f'z={position.z:.3f} m'
            )

            self.get_logger().info(
                f'Hovering for '
                f'{self.hover_time:.1f} s.'
            )

            self.hover_start_time = (
                time.monotonic()
            )

            self.state = 'HOVER'

            return

        # ==========================================================
        # HOVER
        # ==========================================================

        if self.state == 'HOVER':

            self.stop_drone()

            elapsed = (
                time.monotonic()
                - self.hover_start_time
            )

            if elapsed < self.hover_time:
                return

            # ------------------------------------------------------
            # Establish capture-motion reference position.
            # ------------------------------------------------------

            self.record_start_x = float(
                position.x
            )

            self.record_start_y = float(
                position.y
            )

            # Start image capture before the forward command.
            self.recording = True

            self.get_logger().info(
                'Recording started.'
            )

            self.get_logger().info(
                'Capture reference position: '
                f'x={self.record_start_x:.6f}, '
                f'y={self.record_start_y:.6f}'
            )

            self.get_logger().info(
                f'Commanding vx = '
                f'{self.forward_speed:.3f} m/s'
            )

            self.state = 'FORWARD'

            return

        # ==========================================================
        # FORWARD MOTION
        # ==========================================================

        if self.state == 'FORWARD':

            current_x = float(
                position.x
            )

            displacement = abs(
                current_x
                - self.record_start_x
            )

            # ------------------------------------------------------
            # Display progress approximately once per second.
            # ------------------------------------------------------

            now = time.monotonic()

            if (
                now
                - self.last_progress_time
                >= 1.0
            ):

                self.get_logger().info(
                    f'Distance: '
                    f'{displacement:.3f} / '
                    f'{self.travel_distance:.3f} m'
                )

                self.last_progress_time = now

            # ------------------------------------------------------
            # Continue forward
            # ------------------------------------------------------

            if displacement < self.travel_distance:

                self.publish_velocity(
                    vx=self.forward_speed,
                    vy=0.0,
                    vz=0.0
                )

                return

            # ======================================================
            # TARGET DISTANCE REACHED
            # ======================================================

            self.stop_drone()

            # Stop accepting new camera frames.
            self.recording = False

            self.finished = True
            self.state = 'FINISHED'

            # Write one human-readable metadata file for the run.
            self.write_experiment_summary(
                status='completed',
                final_displacement=displacement,
                final_x=float(position.x),
                final_y=float(position.y),
                final_z=float(position.z)
            )

            self.get_logger().info(
                '========================================'
            )

            self.get_logger().info(
                'Experiment complete.'
            )

            self.get_logger().info(
                f'Distance travelled: '
                f'{displacement:.3f} m'
            )

            self.get_logger().info(
                f'Saved frames: '
                f'{self.frame_index}'
            )

            self.get_logger().info(
                f'Images: '
                f'{self.image_dir}'
            )

            self.get_logger().info(
                f'Frames CSV: '
                f'{self.csv_path}'
            )

            self.get_logger().info(
                f'Experiment summary: '
                f'{self.summary_path}'
            )

            self.get_logger().info(
                '========================================'
            )

    # ==============================================================
    # EXPERIMENT SUMMARY
    # ==============================================================

    def write_experiment_summary(
        self,
        status,
        final_displacement=None,
        final_x=None,
        final_y=None,
        final_z=None
    ):

        if final_displacement is None:
            final_displacement = self.last_recorded_displacement

        if final_x is None:
            final_x = self.last_recorded_x

        if final_y is None:
            final_y = self.last_recorded_y

        if (
            self.first_frame_timestamp_ns is not None
            and self.last_frame_timestamp_ns is not None
        ):
            capture_duration_s = (
                self.last_frame_timestamp_ns
                - self.first_frame_timestamp_ns
            ) * 1e-9
        else:
            capture_duration_s = 0.0

        if self.frame_index > 1 and capture_duration_s > 0.0:
            measured_fps_hz = (
                (self.frame_index - 1)
                / capture_duration_s
            )
        else:
            measured_fps_hz = 0.0

        def value_or_na(value, precision=6):
            if value is None:
                return 'N/A'
            return f'{float(value):.{precision}f}'

        lines = [
            'TTC EXPERIMENT SUMMARY',
            '======================',
            f'status: {status}',
            f'forward_speed_mps: {self.forward_speed:.6f}',
            f'travel_distance_m: {self.travel_distance:.6f}',
            f'takeoff_speed_mps: {self.takeoff_speed:.6f}',
            f'takeoff_altitude_m: {self.takeoff_altitude:.6f}',
            f'hover_time_s: {self.hover_time:.6f}',
            f'cmd_topic: {self.cmd_topic}',
            f'image_topic: {self.image_topic}',
            f'odom_topic: {self.odom_topic}',
            f'record_start_x_m: {value_or_na(self.record_start_x)}',
            f'record_start_y_m: {value_or_na(self.record_start_y)}',
            f'final_x_m: {value_or_na(final_x)}',
            f'final_y_m: {value_or_na(final_y)}',
            f'final_z_m: {value_or_na(final_z)}',
            f'distance_travelled_m: {value_or_na(final_displacement)}',
            f'saved_frames: {self.frame_index}',
            f'first_timestamp_ns: {self.first_frame_timestamp_ns if self.first_frame_timestamp_ns is not None else "N/A"}',
            f'last_timestamp_ns: {self.last_frame_timestamp_ns if self.last_frame_timestamp_ns is not None else "N/A"}',
            f'capture_duration_s: {capture_duration_s:.9f}',
            f'measured_frame_rate_hz: {measured_fps_hz:.6f}',
            'frames_csv: frames.csv',
            'images_directory: images',
        ]

        with open(
            self.summary_path,
            'w',
            encoding='utf-8'
        ) as summary_file:
            summary_file.write('\n'.join(lines) + '\n')

    # ==============================================================
    # FILE CLEANUP
    # ==============================================================

    def close_files(self):

        if (
            hasattr(self, 'csv_file')
            and not self.csv_file.closed
        ):

            self.csv_file.flush()
            self.csv_file.close()

    def destroy_node(self):

        self.close_files()

        super().destroy_node()


# ==================================================================
# MAIN
# ==================================================================

def main(args=None):

    rclpy.init(args=args)

    node = TTCExperiment()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        if rclpy.ok():

            node.get_logger().info(
                'Experiment interrupted.'
            )

            node.get_logger().info(
                'Stopping drone.'
            )

            # Stop accepting new camera frames before writing metadata.
            node.recording = False

            # Send stop while ROS is still alive.
            node.stop_drone()

            # Save a partial summary for an interrupted run.
            final_x = None
            final_y = None
            final_z = None
            final_displacement = node.last_recorded_displacement

            if node.latest_odom is not None:
                position = node.latest_odom.pose.pose.position
                final_x = float(position.x)
                final_y = float(position.y)
                final_z = float(position.z)

                if node.record_start_x is not None:
                    final_displacement = abs(
                        final_x - node.record_start_x
                    )

            node.write_experiment_summary(
                status='interrupted',
                final_displacement=final_displacement,
                final_x=final_x,
                final_y=final_y,
                final_z=final_z
            )

            # Allow command to reach ros_gz_bridge.
            time.sleep(0.2)

    finally:

        node.close_files()

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()