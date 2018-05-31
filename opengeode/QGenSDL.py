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
import subprocess
import shutil
import logging

LOG = logging.getLogger(__name__)

def call_qgensdl(options):

    ''' Call QGen-SDL tool with the required arguments '''

    lang=''
    if options.toC:
        lang = 'c'
    elif options.toAda:
        lang = 'ada'

    LOG.debug('Generating ' + lang + ' code using QGen from ' + str(options.files))

    outfolder = 'qgen_generated_' + lang
    cmd = ["qgen-sdl", '--language', lang,
            '--output', outfolder,
             '--type-prefix', 'asn1Scc',
             options.files[0]]

    if os.path.exists(outfolder):
            shutil.rmtree(outfolder, ignore_errors=True)

    LOG.debug('QGen-sdl command: ' + str(cmd))
    try:
        p1 = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        errcode = p1.wait()
        stdout, stderr = p1.communicate()
        if errcode:
            LOG.error(stderr)
        LOG.info(stdout)
    except OSError as e:
        errcode = 1
        if e.errno == os.errno.ENOENT:
            LOG.error ('QGen-SDL tool is not found on your path')
        else:
            raise

    return (errcode)