<div style="text-align:center"><img src=https://drive.google.com/uc?id=1ESDZn7xXU-BxeDaWwSYVPdHERqm8WZ6e /></div>
![](https://img.shields.io/github/release/pandao/editor.md.svg) 
# AI for space
Implementation of artificial intelligence image processing on Sipeed Maix development board and dataset generator intended for use in space applications.
### Generate training dataset
[Dataset generator for blender](https://github.com/grupacosmo/Dataset_generator_for_blender) allows you to generate images with corresponding annotation files for object detection training. In addition to dataset generator python script cubesat and Earth 3d model used in example is available [here](https://drive.google.com/file/d/1Qk3qYjgNaC1pGa7IhwhDjou38zbyEGih/view?usp=sharing)
<details><summary>**Show Exmaple image**</summary>
<div style="text-align:center"><img src=https://drive.google.com/uc?id=1eM-nqmNBr69SQu6ntxc427t7TKHYRyhM /></div>
</details>
<details><summary>**Show corresponding xml annotation file**</summary>
<pre>
```<annotation verified="yes">
	<folder>imgs</folder>
	<filename>0131.jpg</filename>
	<path>cubesat_detector/imgs</path>
	<source>
		<database>rendered</database>
	</source>
	<size>
		<width>320</width>
		<height>240</height>
		<deph>3</deph>
	</size>
	<segmented>0</segmented>
	<object>
		<name>sat</name>
		<pose>Unspecified</pose>
		<truncated>0</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>125</xmin>
			<ymin>49</ymin>
			<xmax>259</xmax>
			<ymax>177</ymax>
		</bndbox>
	</object>
</annotation>
```
</details>

<pb></pb>
[Dataset calibrator](https://github.com/grupacosmo/Dataset_calibrator) allows you to change hue, saturation, brightness, focus (and many more) of your dataset to mimic real images captured by camera rather than generated by 3D rendering software.

| Image rendered by dataset generator: [A] | Image A captured by camera | Image A modified by dataset calibrator | 
| ------------- | ------------- || ------------- |
|<div style="text-align:center"><img src=https://drive.google.com/uc?id=10Nyu9dvQ_0lsK-NU8srkLg5okPTK_Gly /></div> |<div style="text-align:center"><img src=https://drive.google.com/uc?id=1BVCvRmP7iAEkJ2azVaCL0TaikK6PAlZG />  |<div style="text-align:center"><img src=https://drive.google.com/uc?id=1mS8IPRJQrM6Ho7R5zZ_s1JX_Eufm6DYP /></div>|
### Object detection and tracking
Neural newtork has been trained on generated datased using keras-based framework [aXeleRate](https://github.com/AIWintermuteAI/aXeleRate).  Thanks to MobileNet5_0 NN architecture the size of final model is just 0.8MB.

<details><summary>**Show aXeleRate  config file**</summary>
<pre>
```
config = {
        "model":{
            "type":                 "Detector",
            "architecture":         "MobileNet5_0",
            "input_size":           224,
            "anchors":              [0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828],
           "labels":               ["sat"],
            "coord_scale" : 		1.0,
            "class_scale" : 		1.0,
            "object_scale" : 		5.0,
            "no_object_scale" : 	1.0
        },
        "weights" : {
            #"full":   				"/content/dubesat_detector.h5",
            "full":   				"",
            "backend":   		    "imagenet"
        },
        "train" : {
            "actual_epoch":         150,
            "train_image_folder":   "cubesat_detector/imgs",
            "train_annot_folder":   "cubesat_detector/anns",
            "train_times":          1,
            "valid_image_folder":   "cubesat_detector/imgs_validation",
            "valid_annot_folder":   "cubesat_detector/anns_validation",
            "valid_times":          1,
            "valid_metric":         "mAP",
            "batch_size":           15,
            "learning_rate":        1e-4,
            "saved_folder":   		F"/content/drive/My Drive/pascal20_detection",
            "first_trainable_layer": "",
            "augumentation":				True,
            "is_only_detect" : 		False
        },
        "converter" : {
            "type":   				["k210"]
        }
    }
```
</pre>
</details>

Below are some experimental result:

| Cubesat detection in orbit |
| ------------- | 
|<div style="text-align:center"><img src=https://drive.google.com/uc?id=1yYzplm3KmwdXeQJTMGNtIRBDS9x_orll / width="520" height="402"></div> |

| Setup (camera pointing at monitor)| Cubesat detection from camera|
| ------------- | ------------- |
|<div style="text-align:center"><img src=https://drive.google.com/uc?id=1HFe6IJF0Vjfla79jFlG3fX047fY1YdeV / width="240" height="240"></div> |<div style="text-align:center"><img src=https://drive.google.com/uc?id=1Jze057cmgb3bYsLqoTSnbQ_aKM7pEJWT /> |

###Image classification
For Image classification neural newtork has been trained to detect deforestation through oil palm plantation growth. For this task dataset from [WiDS Datathon 2019](https://www.kaggle.com/c/widsdatathon2019/overview) was used. The size of final model is similar to object detection (about 0.8MB).
Below are results from raw camera data:
![](https://drive.google.com/uc?id=1K1N7CGnCnQSHTUkumZ_dLRZ-IYS3W-Fk)
###Noise reduction
Coming soon...
###UART MCU comunication
MaixPy board can communicate with external module (e.g. satelite obc) through UART interface. To increase data transfer security error detection algorithm is impelemented on top of UART interface.

![](https://drive.google.com/uc?id=1LqJwEI4MolTliAlLVAAZ6BGH2RcNBQzF)

List of supported commands:
- change neural network model (0x73)
- get position of detrected object (0x65)
- get dimension of detected area (0x66)
- get probability of detected object (0x67)
- get class of detected object (0x68)
- get  index of detected object (0x69)
- get number of objects detected (0x6A)
- change module power consumption to low (0x6D)
- change module power consumption to medium (0x6E)
- change module power consumption to high (0x6F)
- reset module (0x6C)