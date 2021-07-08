import os
from PIL import Image
import urllib
import urllib.request
import csv
import os
import ssl
import sys
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
    print(file_name)
    if file_name!='random_reddit':
        continue

    if 'saved' in file_name:
        continue

    print(file_name)

    try:
        os.mkdir("image_metadata/thumbnails/"+file_name)
    except FileExistsError:
        pass


    with open(directory+file_name+'.csv', "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []

        for lines in csv_reader:
            image_url = lines[0]
            if 'image url' not in image_url and 'image_url' not in image_url:
                print(image_url)
                try:
                    if image_url.endswith(".html"):
                        continue
                    img = urllib.request.urlopen(image_url)
                    img = Image.open(img)

                    size = img.size
                    # add size, dimensions and extension to image metadata if not already found
                    new_row = lines
                    if lines[2] == 'NA':
                        new_row[2] = sys.getsizeof(img.tobytes())
                    if lines[3] == 'NA':
                        new_row[3] = size
                    if lines[4] == 'NA':
                        new_row[4] = img.format
                    img.thumbnail([128,128])


                    image_url = image_url.replace('/','')
                    image_url = image_url.replace(':','')
                    image_url = image_url.replace('.','')
                    image_url = image_url.replace('-', '')

                    # cut file name if too long
                    if len(image_url)>250:
                        image_url = image_url[0:250]

                    img.save("image_metadata/thumbnails/"+file_name.replace('_saved','')+"/"+image_url+'.png')
                    new_rows.append(new_row)
                    #if len(new_rows)>275 and 'ala' not in file_name:
                    #    break
                except Exception as e:
                    print(e)
            else:
                new_rows.append(lines)
    with open(directory + file_name + '_saved.csv', "w") as csv_file:
        wr = csv.writer(csv_file, delimiter=',')
        wr.writerows(new_rows)
