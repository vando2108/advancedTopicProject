# DIRECTORY STRUCTURE:

----quick-draw-doodle-recognition
--------+ data
----------------+ csv: 
                    *.csv
        
----------------+ processed-1:
                    *.npy (4 classes: triangle, square, circle, others, 30000 files each class)
            
--------+ meta
----------------+ processed-1:
                    partitions.bin
                    labels.bin
    
--------+ models
                     ...
 
 
--------*.ipynb files

--------*.py files


# REQUIREMENTS:
    * python 3.8.3
    * tensorflow 2.2.0
    * pandas 1.0.5
    * numpy 1.19.0

# NOTE: 
  * To increase accuracy, if the maximum score of all classes less than 0.99999, let the label be "others".
