# simplio
A simple and flexible IO file format

## Authors

Copyright (C) 2020, Mattia Bruno 

## Features

 * simple to use, designed for Python
 * binary format, for compactness
 * index file for quick inspection with bash commands or editors
 * concatenable file format, just use `cat`
 * hierarchical file format, allowing for directory structure
 
## Examples

A quick example for saving data to a file in `simplio` format

```python
import simplio

f=simplio.file('mytestfile')
f.save('variable1',3.14)
f.save('dir1/field',data[1])
f.save('dir2/field',data[2])
```

A quick example for reading a file in `simplio` format

```python
import simplio

f=simplio.file('mytestfile')
f.ls() # display file content like ls command
var = f.load('variable1')
f.cd('dir1')
dat = f.load('field')
```
