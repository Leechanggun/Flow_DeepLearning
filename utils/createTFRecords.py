
import numpy as np 
import tensorflow as tf 
from glob import glob as glb
import re
from tqdm import *
from flow_reader import load_flow, load_boundary

FLAGS = tf.app.flags.FLAGS


tf.app.flags.DEFINE_bool('debug', False,
                            """ this will show the images while generating records. """)

# helper function
def _bytes_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

#def _float32_feature(value):
# return tf.train.Feature(float32_list=tf.train.FloatList(value=[value]))

# create tf writer
record_filename = '../data/train.tfrecords'

writer = tf.python_io.TFRecordWriter(record_filename)

# the stored frames
shape = [128, 256]
frames = np.zeros((shape[0], shape[1], 1))

# list of files
train_filename = glb('../data/fluid_flow_steady_state_128x128_/*') 

for  filename in tqdm(train_filename):  
  filename += "/*"
  filename = glb(filename)
  for run in tqdm(filename):
    print(run)
    # read in images
    flow_name = run + '/fluid_flow_0002.h5'
    boundary = load_boundary(flow_name, shape)
    sflow = load_flow(flow_name, shape)
    vmax = []
    if "0.01" in run:
      v = 0.01
    elif "0.05" in run:
      v = 0.05
    elif "0.1" in run:
      v = 0.1

    for i in range(1024):
      vmax.append(v)
    
    # Display the resulting frame
    if FLAGS.debug == True:
      cv2.imshow('boundary', boundary) 
      cv2.waitKey(0)
      cv2.imshow('sflow', sflow[:,:,0]) 
      cv2.waitKey(0)
    
    # process frame for saving
    boundary = np.uint8(boundary)
    boundary = boundary.reshape([1,shape[0]*shape[1]])
    boundary = boundary.tostring()
    sflow = np.float32(sflow)
    sflow = sflow.reshape([1,shape[0]*shape[1]*2])
    sflow = sflow.tostring()
    
    vmax = np.float32(vmax)
    vmax = vmax.reshape([1,1024])
    vmax = vmax.tostring()
  
    # create example and write it
    example = tf.train.Example(features=tf.train.Features(feature={
      'boundary': _bytes_feature(boundary),
      'sflow': _bytes_feature(sflow),
      'vmax':_bytes_feature(vmax)
      })) 
    writer.write(example.SerializeToString()) 
