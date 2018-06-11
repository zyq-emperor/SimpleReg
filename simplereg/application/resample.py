#!/usr/bin/env python

import os
import argparse
import SimpleITK as sitk

import pysitk.python_helper as ph
import pysitk.simple_itk_helper as sitkh

import simplereg.utilities as utils
from simplereg.niftyreg_to_simpleitk_converter import \
    NiftyRegToSimpleItkConverter as nreg2sitk

ALLOWED_INTERPOLATORS = ["Linear", "NearestNeighbour", "BSpline"]


##
# Apply SimpleITK transform to image
# \date       2018-04-25 11:50:08-0600
#
# \return     exit code
#
def main():

    # Read input
    parser = argparse.ArgumentParser(
        description="Resample image.",
        prog=None,
        epilog="Author: Michael Ebner (michael.ebner.14@ucl.ac.uk)",
    )
    parser.add_argument(
        "-m", "--moving",
        help="Path to moving image",
        type=str,
        required=1,
    )
    parser.add_argument(
        "-f", "--fixed",
        help="Path to fixed image. "
        "Can be 'same' if fixed image space is identical to the moving image "
        "space.",
        type=str,
        required=1,
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to resampled image",
        type=str,
        required=1,
    )
    parser.add_argument(
        "-t", "--transform",
        help="Path to (SimpleITK) transformation (.txt) or displacement "
        "field (.nii.gz) to be applied",
        type=str,
        required=0,
    )
    parser.add_argument(
        "-i", "--interpolator",
        help="Interpolator for image resampling. Can be either name (%s) "
        "or order (0, 1)" % (
            ", ".join(ALLOWED_INTERPOLATORS)),
        type=str,
        required=0,
        default="Linear",
    )
    parser.add_argument(
        "-p", "--padding",
        help="Padding value",
        type=int,
        required=0,
        default=0,
    )
    parser.add_argument(
        "-s", "--spacing",
        help="Set spacing for resampling grid in fixed image space",
        nargs="+",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-atg", "--add-to-grid",
        help="Additional grid extension/reduction in each direction of each "
        "axis in millimeter. If scalar, changes are applied uniformly to grid",
        nargs="+",
        type=float,
        default=None,
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Turn on/off verbose output",
        type=int,
        required=0,
        default=0,
    )
    args = parser.parse_args()

    if args.fixed == "same":
        args.fixed = args.moving

    if args.interpolator.isdigit():
        if int(args.interpolator) == 0:
            interpolator_sitk = sitk.sitkNearestNeighbor
        elif int(args.interpolator) == 1:
            interpolator_sitk = sitk.sitkLinear
        else:
            raise IOError("Interpolator order not known")
    else:
        if args.interpolator in ALLOWED_INTERPOLATORS:
            interpolator_sitk = getattr(sitk, "sitk%s" % args.interpolator)
        else:
            raise IOError("Interpolator not known.")

    # read input
    fixed_sitk = sitk.ReadImage(args.fixed)
    moving_sitk = sitk.ReadImage(args.moving)
    if args.transform:
        type_transform = ph.strip_filename_extension(args.transform)[1]
        if type_transform in ["nii", "nii.gz"]:
            displacement_sitk = sitk.ReadImage(
                args.transform, sitk.sitkVectorFloat64)
            transform_sitk = sitk.DisplacementFieldTransform(
                sitk.Image(displacement_sitk))
        else:
            transform_sitk = sitkh.read_transform_sitk(args.transform)
    else:
        transform_sitk = getattr(
            sitk, "Euler%dDTransform" % fixed_sitk.GetDimension())()

    # resample image
    size, origin, spacing, direction = utils.get_space_resampling_properties(
        image_sitk=fixed_sitk,
        spacing=args.spacing,
        add_to_grid=args.add_to_grid,
        add_to_grid_unit="mm")
    warped_moving_sitk = sitk.Resample(
        moving_sitk,
        size,
        transform_sitk,
        interpolator_sitk,
        origin,
        spacing,
        direction,
        float(args.padding),
        fixed_sitk.GetPixelIDValue(),
    )

    # write resampled image
    sitkh.write_nifti_image_sitk(
        warped_moving_sitk, args.output, verbose=args.verbose)

    if args.verbose:
        ph.show_niftis([args.output, args.fixed])

    return 0


if __name__ == '__main__':
    main()
