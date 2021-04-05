import os
from PIL import Image
import urllib
import urllib.request
import csv
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# get all csv files
directory = 'image_metadata/'
files = []
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        files.append(filename.replace('.csv',''))
    else:
        continue

for file_name in files:
    os.mkdir("image_metadata/thumbnails/"+file_name)

    with open(directory+file_name+'.csv', "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for lines in csv_reader:
            image_url = lines[0]
            if 'image' not in image_url:
                print(image_url)

                img = urllib.request.urlopen(image_url)
                img = Image.open(img)
                img.thumbnail([128,128])


                image_url = image_url.replace('/','')
                image_url = image_url.replace(':','')
                image_url = image_url.replace('.','')
                image_url = image_url.replace('-', '')

                img.save("image_metadata/thumbnails/"+file_name+"/"+image_url+'.jpg')
