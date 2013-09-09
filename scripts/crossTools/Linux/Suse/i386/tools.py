from SCons.Tool import gcc
import SCons.Util
import RimUtils
"""
	Include gcc and overide the bin paths to point to our cross build location
"""
bins=[ "CC", "LINK", "AS", "AR", "CXX" ]

def generate(env, toolsPath):
	gcc.generate(env)
