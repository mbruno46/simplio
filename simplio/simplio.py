#################################################################################
#
# simplio.py: definition of main class file
# Copyright (C) 2020 Mattia Bruno
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#################################################################################

from .otypes import *
import os, numpy, zlib

class SimplioErr(Exception):
    pass

def hs(nb):
    n = numpy.int(numpy.log(nb)/numpy.log(1024.)) // 3
    if n==1:
        return f'{nb/1024.**3:8.0f} KB'
    elif n==2:
        return f'{nb/1024.**6:8.0f} MB'
    elif n==3:
        return f'{nb/1024.**3:8.0f} GB'
    return f'{nb:8.0f} B'


def recursive_dict(rdict,key,val):
    tmp=key.split('/')
    if len(tmp)>1:
        if not tmp[0] in rdict:
            rdict[tmp[0]] = {}
        rdict[tmp[0]] = recursive_dict(rdict[tmp[0]],'/'.join(tmp[1:]),val)            
    else:
        if not key in rdict:
            rdict[key] = val
        else:
            raise
    return rdict


class file:
    def __init__(self,fname):
        self.fname = f'{fname}.simplio'
        self.index = f'{fname}.index.simplio'
        self.MAX_SHAPE = 8
        self.MAX_TAG = 64
        self.HEADER_SIZE = self.MAX_TAG + self.MAX_SHAPE + 4 + 1 + 8
        self.data = {}
        self.pwd = '/'
        
        if os.path.isfile(self.index):
            self.__load_index__()
       
    def __write__(self,tag,field):
        if tag in self.data:
            raise SimplioErr(f'Tag {tag} already present. Writing not allowed')
        sz=field.nbytes
        tp=get_numpy_otype(field)
        sh=list(field.shape)
        if not sh:
            sh=[1]
        crc32 = f'{zlib.crc32(field.tobytes("C")):8X}'
        with open(self.index,'a') as f:
            line=f'{tag} ;; {sh} ;; {sz} ;; {crc32} ;; {tp}\n'
            f.write(line)
            
        with open(self.fname,'ab') as f:
            f.write(field.tobytes('C'))
        
        self.data[tag] = [sz, tp, crc32] + sh
            
    def __read__(self,tag):
        self.__load_index__()
        if not os.path.isfile(self.fname):
            raise SimplioErr('File not found')
        if tag not in self.data:
            raise SimplioErr(f'Field with tag {tag} not found in {self.index}')
        dt=set_numpy_otype(self.data[tag][1])
        crc=self.data[tag][2]
        sh=tuple(self.data[tag][3:])
        f=open(self.fname,'rb')
        for key in self.data:
            sz=self.data[key][0]
            if key==tag:
                b = f.read(sz)
                f.close()
                crc32 = f'{zlib.crc32(b):8X}'
                if crc32!=crc:
                    raise SimplioErr(f'Checksum failed')
                return numpy.reshape(numpy.frombuffer(b,dtype=dt), sh)
            else:
                f.seek(sz,1) # 1: relative to current
    
        
    def __full_read__(self):
        self.__load_index__()
        if not os.path.isfile(self.fname):
            raise SimplioErr('File not found')
        out={}
        f=open(self.fname,'rb')
        for key in self.data:
            sz=self.data[key][0]
            dt=set_numpy_otype(self.data[key][1])
            crc=self.data[key][2]
            sh=tuple(self.data[key][3:])
            b=f.read(sz)
            crc32 = f'{zlib.crc32(b):8X}'
            if crc32!=crc:
                raise SimplioErr(f'Checksum failed')
            if sh==(1,):
                out = recursive_dict(out,key[1:],numpy.frombuffer(b,dtype=dt)[0])
            else:
                out = recursive_dict(out,key[1:],numpy.reshape(numpy.frombuffer(b,dtype=dt), sh))
        return out

    def __load_index__(self):
        if self.data:
            return
        
        #if not os.path.isfile(self.index):
        #    raise SimplioErr(f'File {self.index} not found')
            
        with open(self.index,'r') as f:
            for line in f.readlines():
                tmp = line.split(' ;; ')
                _tag = tmp[0]
                _sh = [int(e) for e in tmp[1].strip('][').split(', ')]
                _nb = int(tmp[2])
                _crc = tmp[3]
                _tp=int(tmp[4])
                if _tag in self.data:
                    print(f'WARNING: more than one instance of {_tag} found')
                    print(_tag,self.data)
                self.data[_tag] = [_nb, _tp, _crc] + _sh
    
    # main functions
    def cd(self,arg=None):
        self.__load_index__()
        if arg is None:
            self.pwd = '/'
        else:
            path=os.path.join(self.pwd,arg)
            for key in self.data:
                if path in key:
                    self.pwd=path
                    return
            print(f'Directory {path} not found')
            
    def ls(self,arg=None):
        self.__load_index__()
        if arg is None:
            path=self.pwd
        else:
            path=os.path.join(self.pwd,arg)
        for key in self.data:
            if (path!=key[0:len(path)]):
                continue
            sh=tuple(self.data[key][2:])
            sz=self.data[key][0]
            print(f'{hs(sz)} {key}')

    def save(self,tag,field):
        if tag[0]=='/':
            _tag=tag
        else:
            _tag=os.path.join(self.pwd,tag)
            
        if len(_tag)>self.MAX_TAG:
            print(f'WARNING: Tag contains too many charactes, cutting to {self.MAX_TAG}')
            _tag = _tag[0:self.MAX_TAG]
        
        if self.data:
            if _tag in self.data:
                print(f'Field with tag {_tag} already saved')
                return
        
        if type(field) is numpy.ndarray:
            self.__write__(_tag,field)
        else:
            self.__write__(_tag,numpy.array(field))
        
    def cwd(self,arg):
        if arg[0]=='/':
            self.pwd = arg
        else:
            self.pwd = os.path.join(self.pwd,arg)
        
    def load(self,tag=None):
        if not tag is None:
            if tag[0]=='/': #absolute path
                return self.__read__(tag)
            else:
                return self.__read__(os.path.join(self.pwd,tag))
        else:
            return self.__full_read__()
