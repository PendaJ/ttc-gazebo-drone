# Public release validation checklist

Repository preparation and release checks:

- [x] Replace the maintainer-email placeholder in the ROS package metadata.
- [x] Replace `REPLACE_USERNAME` in `CITATION.cff`.
- [x] Verify and document the upstream X3 UAV license in `THIRD_PARTY.md`.
- [x] Confirm `git status` contains no generated data, `build/`, `install/`, or `log/` files tracked by Git.
- [ ] Confirm all Gazebo Fuel model links still resolve.
- [ ] Run a clean `colcon build --symlink-install`.
- [ ] Launch the simulator from a fresh shell and verify all three ROS topics.
- [ ] Run one 0.5 m/s experiment from the installed packages.
- [ ] Consider adding screenshots/GIFs after final runtime validation.

The current public software archive is version `v0.1.0`. Complete the remaining
runtime checks before freezing the paper-associated `v1.0.0` release.
