# Third-party assets and licensing

This repository contains original TTC experiment code and configuration under the
BSD 3-Clause License, together with simulation content that is derived from or
references upstream Gazebo assets. The repository-level BSD license does not
replace the licenses that apply to third-party or upstream-derived material.

## X3 UAV

The file
`src/drone_ttc_sim/models/x3_ttc/model.sdf` is adapted from the Open Robotics
**X3 UAV** model, version 4, distributed through Gazebo Fuel:

- Source: https://app.gazebosim.org/OpenRobotics/fuel/models/X3%20UAV
- Fuel resource used by this repository: `OpenRobotics/models/X3 UAV/4`
- Upstream authors: Carlos Aguero and Cole Biesemeyer, Open Robotics
- Upstream license: **Creative Commons Attribution 4.0 International
  (CC BY 4.0)**
- License: https://creativecommons.org/licenses/by/4.0/

CC BY 4.0 permits sharing and adaptation, including for commercial purposes,
provided appropriate attribution is given, the license is linked, and changes
are indicated.

### Changes made in this repository

The upstream X3 model definition was adapted for monocular TTC experiments. The
principal project-specific change is the addition of a forward monocular camera
configured for **640 x 480** images at **30 Hz** and published on
`/drone/camera/image_raw`.

The large upstream X3 mesh files are **not redistributed** in this repository.
The adapted SDF references the upstream Gazebo Fuel mesh resources by URL. The
upstream-derived X3 model definition remains subject to CC BY 4.0; the BSD
3-Clause license covering this repository's original software does not
supersede that license.

Suggested attribution:

> X3 UAV model by Carlos Aguero and Cole Biesemeyer / Open Robotics, licensed
> under CC BY 4.0; adapted by Msuega Iorpenda for monocular TTC experiments.

## Office Chair and Standing Person

The simulation world references Open Robotics Gazebo Fuel models by URL rather
than redistributing their model files in this repository. Their respective
upstream licenses and attribution requirements continue to apply. Before a
paper-version release is frozen, the exact Fuel resources should be checked to
confirm that their URLs still resolve and that any required attribution is
recorded here.

## Refrigerator

The development workspace contained a refrigerator mesh whose model metadata
states that the original geometry is licensed under **CC BY-NC 4.0**. That mesh
is **not included** in this repository. It is replaced by a primitive
`refrigerator_ttc` proxy with approximately the same dimensions and TTC
feature-patch layout.

If the exact original refrigerator appearance is required for reproduction,
obtain the asset from its upstream source under its own license rather than
copying it into this repository without the corresponding attribution and
license terms.

## Release status

The X3 UAV license verification and attribution step is complete. Remaining
release checks concern reproducibility and runtime validation, including Fuel
resource availability, a clean ROS 2 build, topic verification, and a complete
example experiment.
