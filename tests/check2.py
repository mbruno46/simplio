import simplio
import numpy, os

fname='test'

f1=simplio.file(fname)
f1.save('val1',1.234)
dat=numpy.random.rand(400)
f1.save('dir1/field',numpy.reshape(dat,(40,10)))

f1.cd('dir1')

dat=numpy.random.rand(500)
f1.save('dir2/field',numpy.reshape(dat,(5,10,10)))

f1.ls()

out=os.popen(f'less {fname}.index.simplio').read()
print(out)

f2=simplio.file(fname)
assert numpy.all(f2.load('dir1/dir2/field')==numpy.reshape(dat,(5,10,10)))

os.popen(f'rm {fname}.*')