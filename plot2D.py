#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#  Plot spin-polarized LDOS for a 2D surface.
#  Run:
#      ./plot2D.py TBTKResults.h5 theta phi sigma
#
#  @author Kristofer Björnson

import h5py
import numpy
import matplotlib.pyplot
import matplotlib.axes
import matplotlib.cm
import scipy.ndimage.filters
import mpl_toolkits.mplot3d
import sys
import math
import cmath

#Check that the number of input parameters is correct.
if(len(sys.argv) != 5):
	print "Error, the following parameters are needed: .hdf5-file, theta, phi, sigma"
	exit(1)

#Extract input parameters.
filename = sys.argv[1]
theta = float(sys.argv[2])
phi = float(sys.argv[3])
sigma = float(sys.argv[4])

#Read dataset from file.
file = h5py.File(filename, 'r');
dataset = file['SpinPolarizedLDOS']

#Extract data from dataset.
data_dimensions = dataset.shape
physical_dimensions = len(data_dimensions) - 3 #The three last dimensions are for energy, spin components, and real/imaginary decomposition.
energy_resolution = data_dimensions[physical_dimensions];
limits = dataset.attrs['UpLowLimits']
print "Dimensions: " + str(physical_dimensions)
print "Resolution: " + str(energy_resolution)
print "UpLowLimits: " + str(limits)
if(physical_dimensions != 2):
	print "Error, can only plot for 2 physical dimensions"
	exit(0)

size_x = data_dimensions[0]
size_y = data_dimensions[1]
size_e = data_dimensions[2]

#Setup plot mesh.
x = numpy.arange(0, data_dimensions[0], 1)
y = numpy.arange(0, data_dimensions[1], 1)
X, Y = numpy.meshgrid(x, y)

#Setup spin-polarized LDOS data for plotting.
e = data_dimensions[2]/2
fig = matplotlib.pyplot.figure()
Z = numpy.real((dataset[:,:,e,0,0] + 1j*dataset[:,:,e,0,1])*math.cos(theta/2)*math.cos(theta/2) \
		+ (dataset[:,:,e,1,0] + 1j*dataset[:,:,e,1,1])*math.cos(theta/2)*math.sin(theta/2)*cmath.exp(1j*phi) \
		+ (dataset[:,:,e,2,0] + 1j*dataset[:,:,e,2,1])*math.sin(theta/2)*math.cos(theta/2)*cmath.exp(-1j*phi) \
		+ (dataset[:,:,e,3,0] + 1j*dataset[:,:,e,3,1])*math.sin(theta/2)*math.sin(theta/2) \
)

#Apply Gaussin smoothing along the energy direction.
sigma_discrete_units = sigma*energy_resolution/(limits[0] - limits[1])
for xp in range(0, size_x):
	Z[xp,:] = scipy.ndimage.filters.gaussian_filter1d(Z[xp,:], sigma_discrete_units)

#Plot and save spin-polarized LDOS.
ax = fig.gca()
ax.pcolormesh(X.transpose(), Y.transpose(), Z, cmap=matplotlib.cm.coolwarm)
fig.savefig('figures/SpinPolarizedLDOS2D.png')

#Setup LDOS data for plotting.
fig2 = matplotlib.pyplot.figure()
Z = numpy.real((dataset[:,:,e,0,0] + 1j*dataset[:,:,e,0,1]) \
		+ (dataset[:,:,e,3,0] + 1j*dataset[:,:,e,3,1]) \
)


#Apply Gaussin smoothing along the energy direction.
sigma_discrete_units = sigma*energy_resolution/(limits[0] - limits[1])
for xp in range(0, size_x):
	Z[xp,:] = scipy.ndimage.filters.gaussian_filter1d(Z[xp,:], sigma_discrete_units)

#Plot and save spin-polarized LDOS.
ax = fig2.gca()
ax.pcolormesh(X.transpose(), Y.transpose(), Z, cmap=matplotlib.cm.coolwarm)
fig2.savefig('figures/LDOS2D.png')
