##
# \file application_test.py
#  \brief  Unit tests based on fetal brain case study
#
#  \author Michael Ebner (michael.ebner.14@ucl.ac.uk)
#  \date November 2017


import os
import unittest
import numpy as np
import re
import SimpleITK as sitk

import pysitk.python_helper as ph
import pysitk.simple_itk_helper as sitkh

import simplereg.data_reader as dr
from simplereg.definitions import DIR_TMP, DIR_TEST, DIR_DATA


class ApplicationTest(unittest.TestCase):

    def setUp(self):
        self.precision = 7
        self.dir_output = os.path.join(DIR_TMP, "simplereg-application")

        self.image_2D = os.path.join(DIR_DATA, "2D_Brain_Target.nii.gz")
        self.image_3D = os.path.join(DIR_DATA, "3D_Brain_Target.nii.gz")

        self.transform_2D_sitk = os.path.join(
            DIR_TEST, "2D_sitk_Target_Source.txt")
        self.transform_3D_sitk = os.path.join(
            DIR_TEST, "3D_sitk_Target_Source.txt")

        self.transform_2D_nreg = os.path.join(
            DIR_TEST, "2D_regaladin_Target_Source.txt")
        self.transform_3D_nreg = os.path.join(
            DIR_TEST, "3D_regaladin_Target_Source.txt")

        self.landmarks_3D = os.path.join(
            DIR_TEST, "3D_Brain_Template_landmarks.txt")

        self.output_transform = os.path.join(self.dir_output, "transform.txt")
        self.output_landmarks = os.path.join(self.dir_output, "landmarks.txt")
        self.output_image = os.path.join(self.dir_output, "image.nii.gz")

    def test_transform_image(self):

        cmd_args = ["simplereg_transform"]
        cmd_args.append("-i %s %s %s" % (
            self.image_3D, self.transform_3D_sitk, self.output_image))
        self.assertEqual(ph.execute_command(" ".join(cmd_args)), 0)

    def test_transform_invert_transform(self):
        cmd_args = ["simplereg_transform"]
        cmd_args.append("-inv %s %s" % (
            self.transform_3D_sitk, self.output_transform))
        self.assertEqual(ph.execute_command(" ".join(cmd_args)), 0)

        transform_sitk = dr.DataReader.read_transform(
            self.transform_3D_sitk)
        transform_inv_sitk = dr.DataReader.read_transform(
            self.output_transform)
        ref_nda = np.array(transform_sitk.GetInverse().GetParameters())
        res_nda = np.array(transform_inv_sitk.GetParameters())
        self.assertAlmostEqual(
            np.linalg.norm(ref_nda - ref_nda), 0, places=self.precision)

    def test_transform_landmarks(self):
        cmd_args = ["simplereg_transform"]
        cmd_args.append("-l %s %s %s" % (
            self.landmarks_3D, self.transform_3D_sitk, self.output_landmarks))
        self.assertEqual(ph.execute_command(" ".join(cmd_args)), 0)

    def test_transform_sitk_to_nreg(self):
        cmd_args = ["simplereg_transform"]
        cmd_args.append("-sitk2nreg %s %s" % (
            self.transform_3D_sitk, self.output_transform))
        self.assertEqual(ph.execute_command(" ".join(cmd_args)), 0)

        res_nda = dr.DataReader.read_transform_nreg(self.output_transform)
        ref_nda = dr.DataReader.read_transform_nreg(self.transform_3D_nreg)
        self.assertAlmostEqual(
            np.linalg.norm(ref_nda - ref_nda), 0, places=self.precision)

    def test_transform_nreg_to_sitk(self):
        cmd_args = ["simplereg_transform"]
        cmd_args.append("-nreg2sitk %s %s" % (
            self.transform_3D_nreg, self.output_transform))
        self.assertEqual(ph.execute_command(" ".join(cmd_args)), 0)

        res_sitk = dr.DataReader.read_transform(self.output_transform)
        ref_sitk = dr.DataReader.read_transform(self.transform_3D_sitk)
        res_nda = np.array(res_sitk.GetParameters())
        ref_nda = np.array(ref_sitk.GetParameters())
        self.assertAlmostEqual(
            np.linalg.norm(ref_nda - ref_nda), 0, places=self.precision)

    def test_transform_nreg_to_sitk(self):
        cmd_args = ["simplereg_transform"]
        cmd_args.append("-sitk2nii %s %s" % (
            self.landmarks_3D, self.output_landmarks))
        self.assertEqual(ph.execute_command(" ".join(cmd_args)), 0)

        res_nda = dr.DataReader.read_landmarks(self.output_landmarks)
        ref_nda = dr.DataReader.read_landmarks(self.landmarks_3D)
        ref_nda[:,0:2] *= -1
        self.assertAlmostEqual(
            np.linalg.norm(ref_nda - ref_nda), 0, places=self.precision)

    # TODO
    def test_transform_split_labels(self):
        pass

    # TODO
    def test_transform_mask_to_landmark(self):
        pass

