# Public release checklist

Before creating the public GitHub repository:

- [ ] Replace `replace-before-release@example.com` in both ROS package files.
- [ ] Replace `REPLACE_USERNAME` in `CITATION.cff`.
- [ ] Verify and document the upstream X3 UAV license in `THIRD_PARTY.md`.
- [ ] Confirm all Gazebo Fuel model links still resolve.
- [ ] Run a clean `colcon build --symlink-install`.
- [ ] Launch the simulator from a fresh shell and verify all three ROS topics.
- [ ] Run one 0.5 m/s experiment from the installed packages.
- [ ] Confirm `git status` contains no generated data, `build/`, `install/`, or `log/`.
- [ ] Consider adding screenshots/GIFs after license review.
