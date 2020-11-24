# Cityscapes Import

>The Cityscapes Dataset is intended for
> - assessing the performance of vision algorithms for two major tasks of semantic urban scene understanding: pixel-level and instance-level semantic labeling;
> - supporting research that aims to exploit large volumes of (weakly) annotated data, e.g. for training deep neural networks.

# HOWTO Video

<a href="https://youtu.be/lFs5-zgPulY" target="_blank">![How to import Cityscapes](http://img.youtube.com/vi/lFs5-zgPulY/0.jpg)</a>


#### Usage steps:

1) Download `Cityscapes` dataset from [official site](https://www.cityscapes-dataset.com/)

2) Unpack archive

3) Directory structure have to be the following:
    
```
.
├── gtFine
│   ├── test
│   │   ├── ...
│   ├── train
│   │   ├── ...
│   └── val
│       ├── ...
└── leftImg8bit
    ├── test
    │   ├── ...
    ├── train
    │   ├── ...
    └── val
        └── ...
   
```

4) Open [Supervisely Import](supervise.ly/import) page. Choose `Cityscapes` import plugin.

5) Select one or more subdirectories (`gtFine`, `leftImg8bit`) and drag and drop them to browser.
    
6) Define new project name and click on `START IMPORT` button.

7) After import task finish, you can view created project:

    ![](https://i.imgur.com/aJELl7l.jpg)

8) Also you can find more detailed information about project on `Statistics`, `Classes` and `Tags` tabs:
    
    ![](https://i.imgur.com/C6yW0Rw.jpg)

    ![](https://i.imgur.com/D4a1RI1.png)


## Notes:

* If you will drag and drop parent directory instead of its content, import will crash.

* Supervisely [import documentation](https://docs.supervise.ly/import/).