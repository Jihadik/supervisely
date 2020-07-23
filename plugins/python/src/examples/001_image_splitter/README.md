# Split and Merge

You can add these custom Python scripts to the Project Context Menu -> Run Python Script list by following [this tutorial](https://docs.supervise.ly/data-manipulation/python-scripts#custom-python-scripts). 

## Split

This scripts divides the images and their annotations in the source dataset into new files according to selected settings. 

![](https://i.imgur.com/5zn2SOH.png)

To run the script, name the resulting project and configure the values. Possible values of SW_BORDER_STRATEGY are the following (please note that you have to manually edit this field):

- "add_padding"

![add_padding](https://i.imgur.com/AXeUBHf.gif)

- "shift_window"

![shift_window](https://i.imgur.com/1WxaxNx.gif)

- "change_size"

![change_size](https://i.imgur.com/Zgm95uW.gif)

## Merge

This script combines the image fragments received from the 'Split' script back together. If padding was added to images at the splitting step, it will be kept during merging.  

Please note that the previosly split annotations are not combined back in this action and instead are copied to the larger image as is, preserving their relative position on the image. 
