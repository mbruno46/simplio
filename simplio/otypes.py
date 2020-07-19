#################################################################################
#
# otypes.py: definition of basic types and type-related functions
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

import numpy, struct

class otypes:
    CHAR = 1
    INT4 = 2
    INT8 = 3
    FLOAT4 = 4
    FLOAT8 = 5
    
def get_numpy_otype(dat):
    dt = dat.dtype
    if dt == numpy.int32:
        return otypes.INT4
    elif dt == numpy.int64:
        return otypes.INT8
    elif dt == numpy.float32:
        return otypes.FLOAT4
    elif dt == numpy.float64:
        return otypes.FLOAT8
    else:
        raise Exception(f'Numpy data type not supported')

def get_python_otype(dat):
    dt = type(dat)
    if dt is int:
        try:
            dat.to_bytes(4,byteorder='little')
            return otypes.INT4
        except:
            return otypes.INT8
    elif dt is float:
        return otypes.FLOAT8
    else:
        raise Exception(f'Python data type not supported')
        
def set_numpy_otype(dt):
    if dt == otypes.INT4:
        return numpy.int32
    elif dt == otypes.INT8:
        return numpy.int64
    elif dt == otypes.FLOAT4:
        return numpy.float32
    elif dt == otypes.FLOAT8:
        return numpy.float64
    else:
        raise Exception(f'Numpy data type not supported')
        
def packer(dat,tp):
    if tp == otypes.INT4:
        return struct.pack('<i',dat)
    elif tp == otypes.INT8:
        return struct.pack('<q',dat)
    elif tp == otypes.FLOAT4:
        return struct.pack('<f',dat)
    elif tp == otypes.FLOAT8:
        return struct.pack('<d',dat)
