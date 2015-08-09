#!/usr/bin/env python

###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

"""

"""

__author__ = 'Donovan Parks'
__copyright__ = 'Copyright 2015'
__credits__ = ['Donovan Parks']
__license__ = 'GPL3'
__version__ = '1.0.0'
__maintainer__ = 'Donovan Parks'
__email__ = 'donovan.parks@gmail.com'
__status__ = 'Development'

import os
import math
import random

import svgwrite
from svgwrite import cm, mm  

import numpy as np
from PIL import Image


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def list(self):
        return (self.x, self.y)
 
class Rhino:
    def __init__(self, outputFile):    
        self.canvasWidth = 24 * 150
        self.canvasHeight = 36 * 150
        self.border = int(self.canvasWidth * 0.05)
        
        self.numPolygons = 200
        self.minLength = self.canvasWidth * 0.1
        self.maxLength = self.canvasWidth * 0.1
        
        self.blood = [(123,5,13),(165,15,21),(203,24,29)]

        self.palette = self.blood

        self.background = "rgb(" + str(self.palette[0][0]) + "," + str(self.palette[0][1]) + "," + str(self.palette[0][2]) + ")"

        self.dwg = svgwrite.Drawing(filename=outputFile, size=(self.canvasWidth, self.canvasHeight), profile='tiny')
        self.dwg.set_desc(title='Rhino, DHP 2015', desc='Generative art inspired by the illegal trade in rhino horns.')
        
    def fractalLine(self, iterations=8):
        """Generate points along a fractal line."""

        minRatio = 0.33
        minY = 1
        maxY = 1

        pointList = []
        pointList.append(Point(0.0, 1.0))
        pointList.append(Point(1.0, 1.0))
        for i in xrange(0, iterations):
            newPointList = []
            for j in xrange(0, len(pointList)-1):
                pt = pointList[j]
                nextPt = pointList[j+1]
                
                newPointList.append(pt)
                
                ratio = random.uniform(minRatio, 2 * minRatio)

                newX = pt.x + ratio*(nextPt.x - pt.x)

                # find distance to closest point
                dx = min(newX - pt.x, nextPt.x - newX)

                # create new point
                newY = pt.y + ratio*(nextPt.y - pt.y);
                newY += dx * random.uniform(-1, 1);

                # track upper and lower bounds
                maxY = max(newY, maxY)
                minY = min(minY, newY)

                # add new point
                newPointList.append(Point(newX, newY))
                
            pointList = newPointList
            pointList.append(Point(1.0, 1.0))

        # normalize to values between 0 and 1
        if maxY != minY:
            normalizeRate = 1.0 / (maxY - minY)
            for pt in pointList:
                pt.y = normalizeRate * (pt.y - minY)
        else:
            # max = min, so set all points equal to 1
            for pt in pointList:
                pt.y = 1

        return pointList
                
    def drawImperfectPolygon(self, x0, y0, 
                                    w, h, 
                                    r, g, b, alpha,
                                    cornerDrift=3,
                                    drawDriftX=3,
                                    drawDriftY=3,
                                    rotation=0,
                                    iterations=8):
        """Draw imperfect polygon with fractal fill."""
        
        # generate imperfect polygon
        corner = []
        corner.append(Point(x0 + cornerDrift*random.uniform(-1, 1), y0 + cornerDrift*random.uniform(-1, 1)))
        corner.append(Point(x0 + w + cornerDrift*random.uniform(-1, 1), y0 + cornerDrift*random.uniform(-1, 1)))
        corner.append(Point(x0 + w + cornerDrift*random.uniform(-1, 1), y0 + h + cornerDrift*random.uniform(-1, 1)))
        corner.append(Point(x0 + cornerDrift*random.uniform(-1, 1), y0 + h + cornerDrift*random.uniform(-1, 1)))

        driftVector = []
        driftVector.append(Point(0, drawDriftY))
        driftVector.append(Point(drawDriftX, 0))
        driftVector.append(Point(0, drawDriftY))
        driftVector.append(Point(drawDriftX, 0))
        
        points = [corner[0].list()]
        for i in xrange(0, 4):
            nextCorner = corner[(i + 1) % 4]
            pointList = self.fractalLine()
            endpointY = pointList[0].y

            for pt in pointList:
                nextX = corner[i].x + pt.x*(nextCorner.x - corner[i].x)
                nextY = corner[i].y + pt.x*(nextCorner.y - corner[i].y)
                nextX += driftVector[i].x*(pt.y - endpointY)
                nextY += driftVector[i].y*(pt.y - endpointY)
                points.append((nextX, nextY))

        polygon = self.dwg.add(self.dwg.polygon())
        polygon.points.extend(points)
        polygon.stroke(color='none')
            
        if rotation != 0:
            polygon.rotate(rotation, (x0+w/2.0, y0+h/2.0))

        fillColor = "rgb(" + str(r) + "," + str(g) + "," + str(b) + ")"
        polygon.fill(color=fillColor, opacity=alpha)
            
    def generate(self):
        self.dwg.add(self.dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill=self.background, stroke='none'))

        boundingBoxes = []
        for i in xrange(self.numPolygons): 

            #r = random.randint(self.palette[0][0], self.palette[1][0])
            #g = random.randint(self.palette[0][1], self.palette[1][1])
            #b = random.randint(self.palette[0][2], self.palette[1][2])
            r = int(self.palette[0][0] + self.palette[0][0] * random.uniform(-0.1, 0.1))
            g = int(self.palette[0][1] + self.palette[0][1] * random.uniform(-0.1, 0.1))
            b = int(self.palette[0][2] + self.palette[0][2] * random.uniform(-0.1, 0.1))
   
            w = random.randint(self.minLength, self.maxLength)
            h = random.randint(self.minLength, self.maxLength)
            x0 = random.randint(0, self.canvasWidth - w)
            y0 = random.randint(0, self.canvasHeight - h)
            
            cornerDrift = random.randint(0, int(min(w, h)*0.7))
            drawDrift = random.randint(int(min(w, h)*0.3), int(min(w, h)*0.9))
            rotationDrift = random.randint(0, 180)

            self.drawImperfectPolygon(x0, y0, w, h, 
                                        r, g, b, 1.0,
                                        cornerDrift=cornerDrift,
                                        drawDriftX=drawDrift,
                                        drawDriftY=drawDrift,
                                        rotation=rotationDrift,
                                        iterations=9)
                                        
            horn = self.dwg.add(self.dwg.polygon())
            points = ((0.97*self.canvasWidth, self.canvasHeight*0.98), (0.93*self.canvasWidth, self.canvasHeight*0.98), (0.95*self.canvasWidth, 0.90*self.canvasHeight))
            
            horn.points.extend(points)
            horn.stroke(color='none')
            #horn.rotate(rotation, (x0+w/2.0, y0+h/2.0))

            fillColor = "rgb(" + str(255) + "," + str(255) + "," + str(255) + ")"
            horn.fill(color=fillColor, opacity=1.0)
            
        self.dwg.save()
        
if __name__ == "__main__":
    for i in xrange(10):
        print i
        output_file = './images/rhino.still_%d.svg' % (i+1)
        rhino = Rhino(output_file)
        rhino.generate()
        
        os.system('"C:\Program Files\Inkscape\inkscape.exe" -z -e %s -w %d -h %d %s' % ('./images/rhino.still_%d.png' % (i+1), rhino.canvasWidth, rhino.canvasHeight, output_file))
        