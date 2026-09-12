# Third-party assets and licensing

This repository contains project code and configuration developed for the TTC
experiments, but some simulation content is derived from or references upstream
Gazebo assets.

## X3 UAV

`src/drone_ttc_sim/models/x3_ttc/model.sdf` is adapted from the Open Robotics
X3 UAV model. The large X3 mesh files from the development workspace are **not**
redistributed here. The SDF references the corresponding Gazebo Fuel resources
by URL.

Before making the repository public, verify the license of the exact upstream
X3 UAV model version used and add the required attribution/license notice here.

## Office Chair and Standing Person

The world references the Open Robotics Gazebo Fuel models by URL rather than
redistributing their files. Their upstream licenses still apply.

## Refrigerator

The development workspace contained a refrigerator mesh whose model metadata
states that the original geometry is licensed under CC BY-NC 4.0. That mesh is
**not** included in this public-ready repository. It is replaced by a primitive
`refrigerator_ttc` proxy with approximately the same dimensions and the TTC
feature-patch layout.

If the exact original refrigerator appearance is required for reproduction,
obtain the asset from its upstream source under its own license rather than
copying it into this repository without the corresponding attribution and
license terms.

## Release gate

Do not publish this repository until the X3 upstream license has been checked
and the placeholder maintainer email has been replaced.
