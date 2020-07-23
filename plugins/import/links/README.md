# Import Images Links 
This plugin allows you to upload remote images by links. Input structure should be the following:

### Flat set of TXT files.
You can drag and drop one or many txt files. Each file corresponds to separate dataset. File name defines the name of dataset that will be created.

```
.
├── dataset_01.txt
├── dataset_02.txt
├── ...
└── dataset_x.txt
```

### Structure of text file with links.
Each line of the text file should contain only on link. For example, here is the content of the text file `dataset_01.txt`:

```
https://m.media-amazon.com/images/M/MV5BMjA0MDIwMDYwNl5BMl5BanBnXkFtZTcwMjY0Mzg4Mw@@._V1_SY1000_CR0,0,1350,1000_AL_.jpg
https://m.media-amazon.com/images/M/MV5BMTc5Njg5Njg2MV5BMl5BanBnXkFtZTgwMjAwMzg5MTE@._V1_SY1000_CR0,0,1332,1000_AL_.jpg
https://m.media-amazon.com/images/M/MV5BMjA5ODU3NTI0Ml5BMl5BanBnXkFtZTcwODczMTk2Mw@@._V1_SX1777_CR0,0,1777,756_AL_.jpg
```
### Image name normalization

Let's consider the following url: `https://m.media-amazon.com/images/M/MV5BMjA0MDIwMDYwNl5BMl5BanBnXkFtZTcwMjY0Mzg4Mw@@._V1_SY1000_CR0,0,1350,1000_AL_.jpg`. 

If flag `"normalize_image_name": true` the resulting image name will be normalized: `MV5BMjA0MDIwMDYwNl5BMl5BanBnXkFtZTcwMjY0Mzg4Mw-V1-SY1000-CR0013501000-AL.jpg`.

If flag `"normalize_image_name": false` the resulting image name will be preserved: `MV5BMjA0MDIwMDYwNl5BMl5BanBnXkFtZTcwMjY0Mzg4Mw@@._V1_SY1000_CR0,0,1350,1000_AL_.jpg`.