"""
                                   Q G E N                                    
                                                                              
                       Copyright (C) 2011-2018, AdaCore                       
                       Copyright (C) 2011-2018, IB Krates                     
                                                                              
   This is free software;  you can redistribute it  and/or modify it  under   
   terms of the  GNU General Public License as published  by the Free Soft-   
   ware  Foundation;  either version 3,  or (at your option) any later ver-   
   sion.  This software is distributed in the hope  that it will be useful,   
   but WITHOUT ANY WARRANTY;  without even the implied warranty of MERCHAN-   
   TABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public   
   License for  more details.  You should have  received  a copy of the GNU   
   General  Public  License  distributed  with  this  software;   see  file   
   COPYING3.  If not, go to http://www.gnu.org/licenses for a complete copy   
   of the license.                                                            
                                                                              
"""
import os
import sys
import logging
import argparse
import subprocess
import unittest
import difflib
import re
import string
import time
import test
import shutil
import glob
import logging

LOG = logging.getLogger(__name__)

def call_qgensdl(options):

    ''' Call QGen-SDL tool with the required arguments '''

    qgen_dir = os.environ.get('QGEN_REPO_ROOT')
    sdl_importer_proj_name = "ee.ibk.sdl.importer"
    sdl_importer_launcher = "qgen-sdl"
    sdl_importer_loc = "gms/eclipse/" + sdl_importer_proj_name + "/target" + \
                    "/sdl-importer/lib/" + sdl_importer_launcher
    sdl_importer_path = os.path.join (qgen_dir,sdl_importer_loc)

    lang=''

    if options.toC:
        lang = 'c'
    elif options.toAda:
        lang = 'ada'
    else:
        # the importer crashes if any other value us used here,
        # for now keep xmi as default value
        lang = 'xmi'

    LOG.debug('Generating ' + lang + ' code using QGen from ' + str(options.files))

    outfolder = 'qgen_generated_' + lang
    cmd = [sdl_importer_path, options.files[1],
            '--language', lang,
            '--output', outfolder,
             '--type-prefix', 'asn1Scc']

    if os.path.exists(outfolder):
            shutil.rmtree(outfolder, ignore_errors=True)

    LOG.debug('Qgen-sdl command: ' + str(cmd))
    p1 = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = p1.communicate()
    errcode = p1.wait()

    LOG.info(stdout)
    LOG.debug(stderr)
    return (errcode)