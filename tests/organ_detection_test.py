#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Enable Python3 code in Python2 - Must be first in file!
from __future__ import print_function   # print("text")
from __future__ import division         # 2/3 == 0.666; 2//3 == 0
from __future__ import absolute_import  # 'import submodule2' turns into 'from . import submodule2'
from builtins import range              # replaces range with xrange

import logging
logger = logging.getLogger(__name__)

import unittest
from nose.plugins.attrib import attr

import os
import os.path as op
import numpy as np
import skimage.measure

import io3d
import io3d.datasets
from bodynavigation.organ_detection import OrganDetection
import bodynavigation.metrics as metrics

import sed3 # for testing

# http://www.ircad.fr/softwares/3Dircadb/3Dircadb1/3Dircadb1.1.zip
TEST_DATA_DIR = "3Dircadb1.1"

class OrganDetectionTest(unittest.TestCase):
    """
    Run only this test class:
        nosetests -v -s tests.organ_detection_test
        nosetests -v -s --logging-level=DEBUG tests.organ_detection_test
    Run only single test:
        nosetests -v -s tests.organ_detection_test:OrganDetectionTest.getBody_test
        nosetests -v -s --logging-level=DEBUG tests.organ_detection_test:OrganDetectionTest.getBody_test
    """

    # Minimal dice coefficients
    GET_BODY_DICE = 0.95
    GET_LUNGS_DICE = 0.95
    GET_BONES_DICE =  0.75 # test data don't have segmented whole bones, missing center volumes
    GET_KIDNEYS_DICE = 0.75
    GET_AORTA_DICE = 0.25 # TODO - used test data has smaller vessels connected to aorta => that's why the big error margin
    GET_VENACAVA_DICE = 0.25 # TODO - used test data has smaller vessels connected to aorta => that's why the big error margin


    @classmethod
    def setUpClass(cls):
        datap = io3d.read(
            io3d.datasets.join_path(TEST_DATA_DIR, "PATIENT_DICOM"),
            dataplus_format=True)
        cls.obj = OrganDetection(datap["data3d"], datap["voxelsize_mm"])

    @classmethod
    def tearDownClass(cls):
        cls.obj = None

    def getBody_test(self):
        # get segmented data
        body = self.obj.getBody()

        # get preprocessed test data
        datap = io3d.read(
            io3d.datasets.join_path(TEST_DATA_DIR, "MASKS_DICOM", "skin"),
            # io3d.datasets.join_path("PATIENT_DICOM/MASKS_DICOM/skin"),
            dataplus_format=True)
        test_body = datap["data3d"] > 0 # reducing value range to <0,1> from <0,255>

        # ed = sed3.sed3(test_body.astype(np.uint8), contour=body.astype(np.uint8))
        # ed.show()

        # There must be only one object (body) in segmented data
        test_body_label = skimage.measure.label(test_body, background=0)
        self.assertEqual(np.max(test_body_label), 1)

        # Test requires at least ??% of correct segmentation
        dice = metrics.dice(test_body, body)
        print("getBody(), Dice coeff: %s" % str(dice))
        self.assertGreater(dice, self.GET_BODY_DICE)

    def getLungs_test(self):
        # get segmented data
        lungs = self.obj.getLungs()

        # get preprocessed test data
        datap1 = io3d.read(
            io3d.datasets.join_path(TEST_DATA_DIR, "MASKS_DICOM", "leftlung"),
            dataplus_format=True)
        datap2 = io3d.read(
            io3d.datasets.join_path(TEST_DATA_DIR, "MASKS_DICOM", "rightlung"),
            dataplus_format=True)
        test_lungs = (datap1["data3d"]+datap2["data3d"]) > 0 # reducing value range to <0,1> from <0,255>

        # ed = sed3.sed3(test_lungs.astype(np.uint8), contour=lungs.astype(np.uint8))
        # ed.show()

        # Test requires at least ??% of correct segmentation
        dice = metrics.dice(test_lungs, lungs)
        print("getLungs(), Dice coeff: %s" % str(dice))
        self.assertGreater(dice, self.GET_LUNGS_DICE)

    def getAorta_test(self):
        # get segmented data
        aorta = self.obj.getAorta()

        # get preprocessed test data
        datap = io3d.read(io3d.datasets.join_path(TEST_DATA_DIR, "MASKS_DICOM", "artery"), dataplus_format=True)
        test_aorta = datap["data3d"] > 0 # reducing value range to <0,1> from <0,255>

        # ed = sed3.sed3(test_aorta.astype(np.uint8), contour=aorta.astype(np.uint8))
        # ed.show()

        # Test requires at least ??% of correct segmentation
        dice = metrics.dice(test_aorta, aorta)
        print("getAorta(), Dice coeff: %s" % str(dice))
        self.assertGreater(dice, self.GET_AORTA_DICE)
        # TODO - better -> segment smaller connected vessels OR trim test mask

    def getVenaCava_test(self):
        # get segmented data
        venacava = self.obj.getVenaCava()

        # get preprocessed test data
        datap = io3d.read(io3d.datasets.join_path(TEST_DATA_DIR, "MASKS_DICOM", "venoussystem"), dataplus_format=True)
        test_venacava = datap["data3d"] > 0 # reducing value range to <0,1> from <0,255>

        # ed = sed3.sed3(test_venacava.astype(np.uint8), contour=venacava.astype(np.uint8))
        # ed.show()

        # Test requires at least ??% of correct segmentation
        dice = metrics.dice(test_venacava, venacava)
        print("getVenaCava(), Dice coeff: %s" % str(dice))
        self.assertGreater(dice, self.GET_VENACAVA_DICE)
        # TODO - better -> segment smaller connected vessels OR trim test mask

    def getBones_test(self):
        # get segmented data
        bones = self.obj.getBones()

        # get preprocessed test data
        datap = io3d.read(io3d.datasets.join_path(TEST_DATA_DIR, "MASKS_DICOM", "bone"), dataplus_format=True)
        test_bones = datap["data3d"] > 0 # reducing value range to <0,1> from <0,255>

        # ed = sed3.sed3(test_bones.astype(np.uint8), contour=bones.astype(np.uint8))
        # ed.show()

        # Test requires at least ??% of correct segmentation
        dice = metrics.dice(test_bones, bones)
        print("getBones(), Dice coeff: %s" % str(dice))
        self.assertGreater(dice, self.GET_BONES_DICE)

    def getKidneys_test(self):
        # get segmented data
        kidneys = self.obj.getKidneys()

        # get preprocessed test data
        datap1 = io3d.read(
            io3d.datasets.join_path(TEST_DATA_DIR, "MASKS_DICOM", "leftkidney"),
            dataplus_format=True)
        datap2 = io3d.read(
            io3d.datasets.join_path(TEST_DATA_DIR, "MASKS_DICOM", "rightkidney"),
            dataplus_format=True)
        test_kidneys = (datap1["data3d"]+datap2["data3d"]) > 0 # reducing value range to <0,1> from <0,255>

        # ed = sed3.sed3(test_kidneys.astype(np.uint8), contour=kidneys.astype(np.uint8))
        # ed.show()

        # Test requires at least ??% of correct segmentation
        dice = metrics.dice(test_kidneys, kidneys)
        print("getKidneys(), Dice coeff: %s" % str(dice))
        self.assertGreater(dice, self.GET_KIDNEYS_DICE)


