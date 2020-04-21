# Story_boarding_data
This repo is unofficial repository for downloading the story boarding dataset accepted at ACL2019 (https://www.aclweb.org/anthology/P19-1606.pdf).  
Although the original download script can be download [here](https://github.com/khyathiraghavi/storyboarding_data), it fails to download the recipes correctly.  

# Requirements
- beautifulSoup4
- requests
- tqdm 

# Usage
Run the following code, then you can get `instructables.json` and `snapguide.json`, which consists of recipes and titles.  
```
python download.py
```
We also release the training scripts for recipe generation from an image sequence [here](https://github.com/misogil0116/recipe_generation_from_an_image_sequence.pytorch).
