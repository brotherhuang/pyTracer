"""
diffgeo.py

This module is part of the pyTracer, which
defines differential geometric operations.

v0.0
Created by Jiayao on July 28, 2017
Modified on Aug 13, 2017
"""
from __future__ import absolute_import
from pytracer import *
from pytracer.geometry import (Point, Vector, Normal, RayDifferential)
from pytracer.geometry.utility import normalize


class DifferentialGeometry(object):
	"""
	Differential Geometry class
	"""
	def __init__(self, pnt: 'Point', dpdu: 'Vector', dpdv: 'Vector',
	             dndu: 'Normal', dndv: 'Normal', uu: 'FLOAT',
	             vv: 'FLOAT', shape: 'Shape'):
		self.p = pnt.copy()
		self.dpdu = dpdu.copy()
		self.dpdv = dpdv.copy()
		self.dndu = dndu.copy()
		self.dndv = dndv.copy()

		self.nn = Normal.from_arr(normalize(dpdu.cross(dpdv)))
		self.u = uu
		self.v = vv
		self.shape = shape

		# adjust for handedness
		if shape is not None and \
			(shape.ro ^ shape.transform_swaps_handedness):
			self.nn *= -1.

		# for anti-aliasing
		self.dudx = self.dvdx = self.dudy = self.dvdy = FLOAT(0.)
		self.dpdx = self.dpdy = Vector(0., 0., 0.)

	def __repr__(self):
		return "{}\nNormal Vector: {}\n".format(self.__class__, self.nn)

	def copy(self):
		return DifferentialGeometry(self.p, self.dpdu, self.dpdv, self.dndu, self.dndv, self.u, self.v, self.shape)

	def compute_differential(self, ray: 'RayDifferential'):
		if ray.has_differentials:
			# estimate screen space change in p and (u, v)

			# compute intersections of incremental rays

			d = -self.nn.dot(self.p)

			#  dot product between Normal and Point is defined =D
			tx = -(self.nn.dot(ray.rxOrigin) + d) / (self.nn.dot(ray.rxDirection))
			px = ray.rxOrigin + tx * ray.rxDirection

			ty = -(self.nn.dot(ray.ryOrigin) + d) / (self.nn.dot(ray.ryDirection))
			py = ray.ryOrigin + ty * ray.ryDirection

			self.dpdx = px - self.p
			self.dpdy = py - self.p

			# compute (u, v) offsets

			# init coefficients
			axes = [0, 1]
			if np.fabs(self.nn.x) > np.fabs(self.nn.y) and np.fabs(self.nn.x) > np.fabs(self.nn.z):
				axes = [1, 2]
			elif np.fabs(self.nn.y) > np.fabs(self.nn.z):
				axes = [0, 2]

			A = [[self.dpdu[axes[0]], self.dpdv[axes[0]]],
			     [self.dpdu[axes[1]], self.dpdv[axes[1]]]]
			Bx = [px[axes[0]] - self.p[axes[0]],
			      px[axes[1]] - self.p[axes[1]]]
			By = [py[axes[0]] - self.p[axes[0]],
			      py[axes[1]] - self.p[axes[1]]]

			try:
				[self.dudx, self.dvdx] = np.linalg.solve(A, Bx)
			except np.linalg.linalg.LinAlgError:
				[self.dudx, self.dvdx] = [0., 0.]

			try:
				[self.dudy, self.dvdy] = np.linalg.solve(A, By)
			except np.linalg.linalg.LinAlgError:
				[self.dudy, self.dvdy] = [0., 0.]			

		else:
			self.dudx = self.dvdx = self.dudy = self.dvdy = FLOAT(0.)
			self.dpdx = self.dpdy = Vector(0., 0., 0.)
