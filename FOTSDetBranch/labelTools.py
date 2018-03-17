#! /usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python version: 3.6.1 -*-

import os
import numpy as np

class labelReader:
    def readSTV2kLabel(self, labelPath):
        '''
        Load the new STV2k label file into arrays.
        @return *xAxis*, *yAxis* and *content*.

        The label file ought to be encoded with GB2312 and organized as:
            [Line 1] x1, y1, x2, y2, x3, y3, x4, y4 (all integers with origin on the top left)
                   (TopRight)(BtmR)  (BtmL) (TopLeft)
            [Line 2] Text contents or blank line if unrecognizable
            [Line 3] Blank line
            [Repeat for other bounding boxes]

        NOTICE: Some indices in the label files may be out of boundary, which are NOT tackled here.
        '''
        xAxis = []
        yAxis = []
        content = []
        with open(labelPath, "r", encoding = "GB2312") as lf:
            count = 0
            for line in lf:
                if (count % 3 == 0 and line != ""):
                    line = line.strip().split(",")
                    xAxis.append(list(map(int, line[0:-1:2])))
                    yAxis.append(list(map(int, line[1::2])))
                if (count % 3 == 1):
                    content.append(line.strip())
                count += 1
        return (np.array(xAxis).astype(int), np.array(yAxis).astype(int), content)


class labelTransformer:
    def transSTV2ktoFOTS(self, labelPath):
        '''
        Transform STV2k labels to FOTS style notations:
        1/4 sized pixel-wise six-channel output, 
        describing probability, relative distance to top/bottom/left/right and orientation.
        @return *outmap*, a float array of size 6 * (w/4) * (h/4)

        @todo + Is the distance relative or absolute?
                I think rela_dist may be better since it is independent from the img size but not sure: ( 
        '''
        pass