# Import Pointclouds

Just drag and drop the collection of pointcloud PLY files and folders with them. These files will be automatically converted to PCD format and uploaded to Supervisely. The new pointloud project will be created. 
   

## Datasets structure

Plugin creates datasets with names of top-most directories in a hierarchy. Files from root import directory will be placed to dataset with name "ds0".  

Let's consider several examples.
 
### Example 1. Import structure:

```
.
├── xxx.ply
├── ds_ny
│   └── frame.ply
└── ds_sf
    └── kitti_0000000001.ply
```

In this case the following datasets will be created

- `ds_0` with a single file `xxx.ply`
- `ds_ny` with a single file `frame.ply`
- `ds_sf` with a single file `kitti_0000000001.ply`


### Example 2. Import structure:

```
abcd_folder/
├── xxx.ply
├── ds_ny
│   └── frame.ply
└── ds_sf
    └── kitti_0000000001.ply
```

In this case only the one dataset `abcd_folder` will be created with all pointcloud files.


### Example 3. PLY files with photo context:


```
abcd_folder/
└── dir_01
    └── dir_02
        ├── frame.ply
        ├── kitti_0000000001.ply
        └── related_images
            └── kitti_0000000001_ply
                ├── 0000000000.png
                └── 0000000000.png.json
```

if you want to attach photo context to ply file just create a directory `related_images` near the file. Then create directory `<filename_with_ext>` (in this example we name directory `kitti_0000000001_ply` - it's a filename + extension + all symbols `.` are replaced to `_`) and put there images and corresponding `json` files with projection matrix. See example for more info.