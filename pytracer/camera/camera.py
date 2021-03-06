"""
camera.py

The base class to model cameras.

Created by Jiayao on July 31, 2017
Modified on Aug 13, 2017
"""
from __future__ import absolute_import
from abc import (ABCMeta, abstractmethod)
from pytracer import *
import pytracer.geometry as geo
import pytracer.transform as trans

__all__ = ['Camera']


class Camera(object, metaclass=ABCMeta):
	"""
	Camera Class
	"""
	def __init__(self, c2w: 'trans.Animatedtrans.Transform', s_open: FLOAT,
				 s_close: FLOAT, film: 'Film'):
		self.c2w = c2w
		self.s_open = s_open
		self.s_close = s_close
		self.film = film

	def __repr__(self):
		return "{}\nShutter: {} - {}".format(self.__class__, self.s_open, self.s_close)

	@abstractmethod
	def generate_ray(self, sample: 'CameraSample') -> [FLOAT, 'geo.Ray']:
		"""
		Generate ray based on image sample.
		Returned ray direction is normalized

		@param
			- sample: instance of `CameraSample` class
		@return
			- FLOAT: light weight
			- geo.Ray: generated `geo.Ray` object
		"""
		raise NotImplementedError('src.core.camera.{}.generate_ray: abstract method called' \
								  .format(self.__class__))

	def generate_ray_differential(self, sample: 'CameraSample') -> [FLOAT, 'geo.RayDifferential']:
		"""
		Generate ray differential.
		"""
		wt, rd = self.generate_ray(sample)
		rd = geo.RayDifferential.from_ray(rd)

		# find ray shift along x
		from pytracer.sampler import CameraSample
		
		xshift = sample.duplicate(1)[0]
		xshift.imageX += 1
		wtx, rx = self.generate_ray(xshift)
		rd.rxOrigin = rx.o
		rd.rxDirection = rx.d

		# find ray shift along y
		yshift = sample.duplicate(1)[0]
		yshift.imageY += 1
		wty, ry = self.generate_ray(yshift)
		rd.ryOrigin = ry.o
		rd.ryDirection = ry.d

		if wtx == 0. or wty == 0.:
			return [0., rd]

		rd.has_differentials = True
		return [wt, rd]

