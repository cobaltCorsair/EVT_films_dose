# -*- coding: utf-8 -*-
import enum

import numpy as np
import scipy.ndimage

class Filters(enum.Enum):
    No_Filter = 1
    Gaussian_05 = 2
    Gaussian_2 = 3
    Median_20 = 4

class Filter(object):
    def __init__(self, imarray):
        self._originalImage = imarray
        self._parsedImage = np.zeros_like(imarray)
        pass

    def setFilter(self, filter=Filters.No_Filter):
        self._filter = filter

    def parse(self):
        if self._filter == Filters.No_Filter:
            self._parsedImage = self._originalImage
        elif self._filter == Filters.Gaussian_2:
            self._parsedImage = scipy.ndimage.gaussian_filter(self._originalImage, 2.0)
        elif self._filter == Filters.Gaussian_05:
            self._parsedImage = scipy.ndimage.gaussian_filter(self._originalImage, 0.5)
        elif self._filter == Filters.Median_20:
            self._parsedImage = scipy.ndimage.median_filter(self._originalImage, size=(20, 20))

    def get(self):
        return self._parsedImage


