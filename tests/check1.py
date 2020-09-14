import simplio
import numpy, os

fname='test'

f1=simplio.file(fname)
f1.save('val1',1.234)
f1.save('cnfg1000/field1',numpy.random.rand(400))
f1.save('cnfg1000/field2',numpy.random.rand(400))
f1.save('cnfg1020/field1',numpy.random.rand(400))
data = numpy.random.rand(400)
f1.save('cnfg1020/field2',data)

f2=simplio.file(fname)
f2.ls()
print(f2.load('val1'))
assert f2.load('val1')==1.234

dat=f2.load()
print(dat['cnfg1000']['field1'])
assert numpy.all(dat['cnfg1020']['field2']==data)

f3=simplio.file(fname)
f3.save('val1',1.456)
f3.ls()
f3.save('val2',1.456)
f3.ls()

os.popen('rm test.*')
