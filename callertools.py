""" Tools for organizing the output from each caller """
import os
import re
from pprint import pprint
if os.name == 'nt':
	GITHUB_FOLDER = os.path.join(os.getenv('USERPROFILE'), 'Documents', 'Github')
else:
	GITHUB_FOLDER = os.path.join(os.getenv('HOME'), 'Documents', 'Github')

import sys
sys.path.append(GITHUB_FOLDER)
import pytools.filetools as filetools


def getOutputCaller(filename):
	if   isMuseOutput( 			filename): result = 'muse'
	elif isMutectOutput(		filename): result = 'mutect'
	elif isSomaticSniperOutput(	filename): result = 'somaticsniper'
	elif isStrelkaSnvOutput(		filename): result = 'strelka'
	elif isVarscanSnvOutput(		filename): result = 'varscan'
	#elif isCnvKitOutput(		filename): result = 'cnvkit'
	else: result = None
	return result

class CallerOutputClassifier:
	"""
		Searches a patient's folder for the relevant caller outputs.
		Keyword Arguments
		-----------------
			'reduce': bool; default False
				if 'True', will only return a single result.
			'verbose': bool; default False
		Returns
		-------
			outputs: dict<>
				* 'muse': 			filename
				* 'mutect2': 		filename
				* 'somaticsniper': 	filename
				* 'strelka-indel': 	filename
				* 'strelka-snv': 	filename
				* 'varscan-indel': 	filename
				* 'varscan-snv': 	filename
		Usage
		-----
			classifier = CallerOutputClassifier()
			result = classifier(patient_folder)
	"""
	def __init__(self, **kwargs):
		self.return_single_result = kwargs.get('reduce', False)
		self.verbose = kwargs.get('verbose', False)
		self.suffixes = self._defineCallerIdentifiers()
	def __call__(self, folder, **kwargs):
		""" Parameters
			----------
				folder: the patient's folder
		"""
		file_list = filetools.listAllFiles(folder, **kwargs)

		caller_outputs = self._searchFolder(file_list)
		if self.return_single_result:
			caller_outputs = self._reduce(caller_outputs)
		if self.verbose:
			pprint(caller_outputs)
		return caller_outputs
	def _reduce(self, outputs):
		outputs = {k:(v if isinstance(v, str) else v[0]) for k, v in outputs.items()}
		return outputs
	def _checkSuffixes(self, filename, suffixes):
		""" Checks the suffixes to see if they're a match """
		is_caller = any(filename.endswith(s) for s in suffixes)
		return is_caller

	def _defineCallerIdentifiers(self):
		""" Defines the suffixes for each caller's expected output """
		suffixes = {
			'muse': 			['.Muse.vcf'],
			'mutect2': 			['.mutect2.vcf'],
			'somaticsniper': 	['.somaticsniper.vcf'],
			'strelka-indel': 	['.passed.somatic.indels.vcf.strelka.vcf'],
			'strelka-snp': 		['.passed.somatic.snvs.vcf.strelka.vcf'],
			'varscan-snp': 		['.raw.indel.vcf'],
			'varscan-indel': 	['.raw.snp.vcf']
		}
		return suffixes

	def _getOutputCallers(self, filename):
		""" returns the name of the caller a specific filename was generated by """
		results = dict()
		for caller, suffixes in self.suffixes.items():
			result = self._checkSuffixes(filename, suffixes)
			if result: return caller

	def _searchFolder(self, file_list):
		""" Classifies all files within a folder. Files
			that do not match any callers are excluded.
		"""
		result = dict()
		for filename in file_list:
			caller = self._getOutputCallers(filename)
			#print(caller, '\t', filename)
			if caller is None: continue
			elif caller in result:
				result[caller].append(filename)
			else:
				result[caller] = [filename]


		return result

if __name__ == "__main__":
	folder = "/home/upmc/Documents/Genomic_Analysis/1_input_vcfs/original_callsets/TCGA-2H-A9GF"
	_test = CallerOutputClassifier()
	result = _test(folder, exclude = ['strelka', 'chromosome'], logic = 'and')
	pprint(result)
	print("Finished!")