# encoding: utf-8
"""
Dataset processing pipeline. 

This script downloads the Noisy-VCTK-Corpus
if it is not available in the specified directory
and produces the metadata files required to further
train and evaluate the deepMultiSpeech package.

Clean and noisy parallel speech database. The database 
was designed to train and test speech enhancement methods 
that operate at 48kHz. A more detailed description can be 
found in the papers associated with the database. For the 
28 speaker dataset, details can be found in: C. 
Valentini-Botinhao, X. Wang, S. Takaki & J. Yamagishi, 
"Speech Enhancement for a Noise-Robust Text-to-Speech 
Synthesis System using Deep Recurrent Neural Networks", 
In Proc. Interspeech 2016. For the 56 speaker dataset: 
C. Valentini-Botinhao, X. Wang, S. Takaki & J. Yamagishi,
"Investigating RNN-based speech enhancement methods for 
noise-robust Text-to-Speech”, In Proc. SSW 2016. Some of 
the noises used to create the noisy speech were obtained 
from the Demand database, available here: http://parole.loria.fr/DEMAND/ . 
The speech database was obtained from the CSTR VCTK Corpus, 
available here: http://dx.doi.org/10.7488/ds/1994. The 
speech-shaped and babble noise files that were used to 
create this dataset are available here: 
http://homepages.inf.ed.ac.uk/cvbotinh/se/noises/.

usage: preprocess.py [options] <data_dir>

options:
    --num_workers=<n>        Num workers.
    --hparams=<params>       Hyper parameters [default: ].
    -h, --help               Show help message.
"""

import os
import importlib
import urllib
import shutil
import urllib
import zipfile

from os.path import join, exists
from docopt import docopt
from multiprocessing import cpu_count
from tqdm import tqdm
from hparams import hparams


URLS = {'train': ('https://datashare.is.ed.ac.uk/bitstream/handle/10283/2791/clean_trainset_28spk_wav.zip?sequence=2&isAllowed=y',
	'https://datashare.is.ed.ac.uk/bitstream/handle/10283/2791/noisy_trainset_28spk_wav.zip?sequence=6&isAllowed=y',
	'https://datashare.is.ed.ac.uk/bitstream/handle/10283/2791/trainset_28spk_txt.zip?sequence=9&isAllowed=y'),
	'test': ('https://datashare.is.ed.ac.uk/bitstream/handle/10283/2791/clean_testset_wav.zip?sequence=1&isAllowed=y',
		'https://datashare.is.ed.ac.uk/bitstream/handle/10283/2791/noisy_testset_wav.zip?sequence=5&isAllowed=y',
		'https://datashare.is.ed.ac.uk/bitstream/handle/10283/2791/testset_txt.zip?sequence=8&isAllowed=y')}


def _rm_hidden(files):
		return [file for file in files if not file.startswith('.')]


def _extract_name(string):
	string = string.split("/")[-1].split("?")[0]
	return string


def _download_dir(url, path):
	filename = wget.download(url, out=path)


def _download_data(data_dir):
	"""Download both train and test data and store them in data_dir."""
	os.makedirs(data_dir, exist_ok=True)
	for phase in URLS:
		for data in URLS[phase]:
			file = _extract_name(data)
			print('Downloading %s' % file)
			urllib.request.urlretrieve(data, os.path.join(data_dir, file))


def _maybe_download(path):
	if exists(path):
		try:
			os.rmdir(path)
			empty = True
		except OSError:
			empty = False
	else:
		os.mkdir(path)
		empty = True
	return empty


def extract_zip(zip_path, dst_path):
	assert zipfile.is_zipfile(zip_path)
	print('Extracting %s' % os.path.basename(zip_path))
	zf = zipfile.ZipFile(zip_path)
	zf_files = _rm_hidden(zf.namelist())
	for file in zf_files:
		zf.extract(file, path=dst_path)


if __name__ == '__main__':
	args = docopt(__doc__)
	data_dir = args["<data_dir>"]
	num_workers = args["--num_workers"]
	num_workers = cpu_count() if num_workers is None else int(num_workers)

	# Override hyper parameters
	hparams.parse(args["--hparams"])
	assert hparams.name == "wavenet_vocoder"

	# Presets
	if hparams.preset is not None and hparams.preset != "":
		preset = hparams.presets[hparams.preset]
		import json
		hparams.parse_json(json.dumps(preset))
		print("Override hyper parameters with preset \"{}\": {}".format(
			hparams.preset, json.dumps(preset, indent=4)))

	download = _maybe_download(data_dir)

	if download:
		zip_dir = join(data_dir, 'zip')
		_download_data(zip_dir)
		data_dirs = _rm_hidden(os.listdir(zip_dir))
		unzip_dir = join(data_dir, 'unzip')
		for d in data_dirs:
			extract_zip(join(zip_dir, d), unzip_dir)
	
	print('Finished')



