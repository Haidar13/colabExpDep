# -*- coding: utf-8 -*-
# pylint:disable = import-error, no-name-in-module, unnecessary-semicolon

"""
Created on Tue Dec 24 11:36:59 2019

@author: Haidar Almubarak h.almubarak@ieee.org
"""


import os
import sys
import shutil
import subprocess
import json
import warnings
from google.colab import drive
from fastai.core import download_url

class ColabDep():
    """
    This class downlod files used in colab experiments, install/clone github reop,
    and install pip packages
    The dependancies should be stored in a json file
    """
    def __init__(self):

        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', 'gdown']);
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', 'gitpython']);
        import gdown
        from git import Repo
        self.reop = Repo
        self.gdown = gdown

        self.deps = {}
        self.mountg = None
        self.gitdep = None
        self.pipdep = None
        self.compressed_data = None
        self.gdrive_compressed = None
        self.otherdata = None

    def process_git(self, git_entry):
        """
        Process a git repo link by cloning the reop or installing it
        Parameters:
            git_entry: A dictionary cointaining the keys
                       - url:    The github url of the reop
                       - install: boolean indicating if the reop need to be installed using pip
                       - folder: folder to clone the reopo into if the install key is not provided
                                 if a folder name not providedthe last part of the url will be used.
        """
        url = git_entry.get('url', None)
        folder = git_entry.get('folder', None)
        install = git_entry.get('install', None)
        if not url:
            raise ValueError('You need to provide the git URL')

        if install:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'git+'+url]);

        else:
            if not folder:
                folder = url.split('/')[-1]
            shutil.rmtree(folder, ignore_errors=True)
            self.reop.clone_from(url, folder)

    def process_compressed(self, dfile):

        url = dfile.get('url', None)
        folder = dfile.get('folder', None)
        fname = url.split('/')[-1]
        if not url:
            raise ValueError('You need to provide the file URL')
        download_url(url, fname, show_progress=False)
        if not folder:
            folder = url.split('/')[-1].split('.')[0]
        shutil.rmtree(folder, ignore_errors=True)
        self.gdown.extractall(fname, folder);
        os.remove(fname)

    def process_pip(self, pip_entry):

        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', pip_entry]);

    def process_raw_file(self, dfile):

        fname = dfile.split('/')[-1]
        download_url(dfile, fname, show_progress=False)

    def process_gdrive_compressed(self, gdrive_entry):

        url = gdrive_entry.get('url', None)
        file_id = gdrive_entry.get('file_id', None)
        folder = gdrive_entry.get('folder', None)
        fname = gdrive_entry.get('fname', None)

        if not file_id and not url:
            err_msg = """You need to provide the file ID or url
                         as "url":"https://drive.google.com/uc?id=FILE_ID"
                         or "file_id":"FILE_ID"
                      """
            raise ValueError(err_msg)
        if not fname:
            raise ValueError('You need to provide the original file name as "fname:file_name"')
        if not folder:
            folder = fname.split('.')[0]

        if  file_id and url:
            warnings.warn("Both URL and file_ID are provided the file_ID will be used")
        if file_id:
            url = 'https://drive.google.com/uc?id={}'.format(file_id)

        self.gdown.download(url, fname, quiet=True);
        self.gdown.extractall(fname, folder);
        os.remove(fname)

    def parse_json(self, json_file):

        with open(json_file) as file:
            deps = json.loads(file.read())
        self.deps = deps
        self.mountg = deps.get('gdrive', None)
        self.gitdep = deps.get('git', None)
        self.pipdep = deps.get('pip', None)
        self.compressed_data = deps.get('compressed_data', None)
        self.gdrive_compressed = deps.get('gdrive_compressed', None)
        self.otherdata = deps.get('otherdata', None)

    def process_json(self, json_file):

        with open(json_file) as file:
            deps = json.loads(file.read())
        self.deps = deps
        self.mountg = deps.get('gdrive', None)
        self.gitdep = deps.get('git', None)
        self.pipdep = deps.get('pip', None)
        self.compressed_data = deps.get('compressed_data', None)
        self.gdrive_compressed = deps.get('gdrive_compressed', None)
        self.otherdata = deps.get('otherdata', None)

        if self.gitdep:
            for dep in self.gitdep:
                self.process_git(dep)

        if self.pipdep:
            for dep in self.pipdep:
                self.process_pip(dep)

        if self.compressed_data:
            for cfile in self.compressed_data:
                self.process_compressed(cfile)

        if self.gdrive_compressed:
            for gfile in self.gdrive_compressed:
                self.process_gdrive_compressed(gfile)

        if self.otherdata:
            for ofile in self.otherdata:
                self.process_raw_file(ofile)

        if self.mountg:
            drive.mount('/content/drive')

