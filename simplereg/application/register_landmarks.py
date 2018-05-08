#!/usr/bin/env python

import os
import argparse
import numpy as np
import SimpleITK as sitk

import pysitk.python_helper as ph
import simplereg.point_based_registration as pbr


def main():

    # Read input
    parser = argparse.ArgumentParser(
        description="Perform rigid registration using landmarks",
        prog=None,
        epilog="Author: Michael Ebner (michael.ebner.14@ucl.ac.uk)",
    )
    parser.add_argument(
        "--fixed",
        help="Path to fixed image landmarks.",
        type=str,
        required=1,
    )
    parser.add_argument(
        "--moving",
        help="Path to moving image landmarks.",
        type=str,
        required=1,
    )
    parser.add_argument(
        "--output",
        help="Path for obtained SimpleITK registration transform (.txt)",
        type=str,
        required=1,
    )
    parser.add_argument(
        "--verbose",
        help="Turn on/off verbose output",
        type=int,
        required=0,
        default=0,
    )
    args = parser.parse_args()

    ph.print_subtitle("Register landmarks")
    landmarks_fixed_nda = np.loadtxt(args.fixed)
    landmarks_moving_nda = np.loadtxt(args.moving)

    point_based_registration = pbr.RigidCoherentPointDrift(
        fixed_points_nda=landmarks_fixed_nda,
        moving_points_nda=landmarks_moving_nda,
        verbose=args.verbose,
    )
    point_based_registration.run()

    rotation_matrix_nda, translation_nda = \
        point_based_registration.get_registration_outcome_nda()

    rigid_transform_sitk = sitk.Euler3DTransform()
    rigid_transform_sitk.SetMatrix(rotation_matrix_nda.flatten())
    rigid_transform_sitk.SetTranslation(translation_nda)

    sitk.WriteTransform(rigid_transform_sitk, args.output)
    ph.print_info("Rigid registration transform written to '%s'" % args.output)

    return 0


if __name__ == '__main__':
    main()
