##
## This is original Koen from dutchpinball.com's Transition helper
## I'm not using the bulk of his extensions, so I copied this one into my own subset of
## the stuff from his that I am using
##

from procgame import *
import ep
import sys

class EP_Transition(object):
	
	# Constants
	TYPE_EXPAND = "ExpandTransition"
	TYPE_PUSH = "PushTransition"
	TYPE_SLIDEOVER = "SlideOverTransition"
	TYPE_WIPE = "WipeTransition"
	TYPE_CROSSFADE = "CrossFadeTransition"
	
	PARAM_HORIZONTAL = "horizontal"
	PARAM_VERTICAL = "vertical"
	PARAM_NORTH = "north"
	PARAM_SOUTH = "south"
	PARAM_WEST = "west"
	PARAM_EAST = "east"
	
	LENGTH_IN_FRAMES = 25.0
		
	def __init__(self, mode, layerA=None, layerB=None, transitionType=TYPE_PUSH, transitionParameter=None, lengthInFrames=LENGTH_IN_FRAMES):
		self.mode = mode
		if layerA == None: layerA = dmd.FrameLayer(False,dmd.Frame(128,32))
		self.layerA = layerA
		if layerB == None: layerB = dmd.FrameLayer(False,dmd.Frame(128,32))
		self.layerB = layerB
		self.callback = None
		
		transition_class = self.get_class("procgame.dmd.transitions." + transitionType)
		if transitionParameter:
			self.transition = transition_class(transitionParameter)
		else:
			self.transition = transition_class()
		self.transition.progress_per_frame = 1.0 / lengthInFrames
		self.transition.completed_handler = self.finished
		self.transition.start()
		
		self.update()
	
	def get_class(self, class_path):
		paths = class_path.split('.')
		modulename = '.'.join(paths[:-1])
		classname = paths[-1]
		return getattr(sys.modules[modulename], classname)

	def update(self):
		#Wrapping the layers in group layers, to maintain the positioning of text layers
		layer_A_wrapped = dmd.GroupedLayer(128, 32, [self.layerA])
		layer_A_wrapped.composite_op = self.layerA.composite_op
		layer_B_wrapped = dmd.GroupedLayer(128, 32, [self.layerB])
		layer_B_wrapped.composite_op = self.layerB.composite_op
		
		layers = [
			dmd.FrameLayer(False,self.transition.next_frame(layer_A_wrapped.next_frame(),layer_B_wrapped.next_frame())),
			ep.EP_UpdateLayer(self.update)
		]
		self.mode.layer = dmd.GroupedLayer(128, 32, layers)
		self.mode.layer.composite_op = self.layerB.composite_op
		
	def finished(self):
		# The transition keeps calling the completed_handler, which we probably don't want, so we clear the reference 
		self.transition.completed_handler = None
		
		self.transition.pause()
		self.mode.layer = self.layerB
		
		if self.callback:
			self.callback()