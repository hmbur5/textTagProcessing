import os
import csv
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

import os
from google.cloud.vision import types
from google.cloud import vision
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "google_keys.json"
client = vision.ImageAnnotatorClient()
def google_object_detection(image_url):
    source = types.ImageSource(image_uri=image_url)
    image = types.Image(source=source)

    # Performs label detection on the image file
    response = client.object_localization(image=image)

    if response.error.code!= 0:
        print(type(response.error))
        print(response.error.code)
        raise Exception('Google problem')

    tagNames = []

    for tag in response.localized_object_annotations:
        # some crops that might be cane toads or other frogs
        if tag.name not in tagNames:
            tagNames.append(tag.name)
    print(tagNames)
    return(tagNames)

def google_label(image_url):
    source = types.ImageSource(image_uri=image_url)
    image = types.Image(source=source)

    # Performs label detection on the image file
    response = client.label_detection(image=image)

    if response.error.code!= 0:
        print(type(response.error))
        print(response.error.code)
        raise Exception('Google problem')


    tagNames = []
    labels = response.label_annotations
    for label in labels:
        if label.description not in tagNames:
            tagNames.append(label.description)

    if len(tagNames)==0:
        print(image)
        print(response)
    print(tagNames)
    return(tagNames)


import gluoncv
import cv2
import mxnet as mx
def gluon_labels(image_url):
    model_name = 'ResNet50_v1d'
    # download and load the pre-trained model
    net = gluoncv.model_zoo.get_model(model_name, pretrained=True)
    # load image
    url_file = 'current_image'
    fname = mx.test_utils.download(image_url, fname='thumbnails/' + url_file, overwrite=True)

    img = mx.ndarray.array(cv2.cvtColor(cv2.imread(fname), cv2.COLOR_BGR2RGB))

    # apply default data preprocessing
    transformed_img = gluoncv.data.transforms.presets.imagenet.transform_eval(img)
    # run forward pass to obtain the predicted score for each class
    pred = net(transformed_img)
    # map predicted values to probability by softmax
    prob = mx.nd.softmax(pred)[0].asnumpy()
    # find the 5 class indices with the highest score
    ind = mx.nd.argsort(pred, is_ascend=0)[0].astype('int').asnumpy().tolist()
    # print the class name and predicted probability
    image_labels = []
    for i in range(len(ind)):
        # add all labels with probability >10% then break
        if prob[ind[i]] < 0.1:
            break
        image_labels.append(net.classes[ind[i]])
    print(image_labels)
    return(image_labels)


import urllib
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image
import math
subscription_key = "eb923ba89759461db59d8a5542f54569"
endpoint = "https://canetoadimageclassification1.cognitiveservices.azure.com/"
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
def azure_labels(image_url):
    try:
        labels = computervision_client.tag_image(image_url).tags
    except:

        # resize and try again
        img = urllib.request.urlopen(image_url)
        img = Image.open(img)
        height, width = img.size
        currentSize = len(img.fp.read())
        # these numbers could probably be better
        maxDim = math.floor(max([width, height]) * 4194304 / currentSize / 3)
        img.thumbnail((maxDim, maxDim))

        img.save('resizing' + ".jpg", "JPEG")
        img = open('resizing.jpg', 'rb')

        labels = computervision_client.tag_image_in_stream(img).tags

    label_names = []
    for label in labels:
        if label.name not in label_names:
            label_names.append(label.name)
    print(label_names)
    return(label_names)


# get all csv files
directory = 'image_metadata/'
files = []
for filename in os.listdir(directory):
    if filename.endswith("_saved.csv"):
        files.append(filename.replace('_saved.csv',''))
    else:
        continue

for filename in files:
    print(filename)
    if 'flickr german wasp' not in filename:
        continue

    filename = filename.replace('_saved','')

    existing_rows = []
    try:
        with open(directory + 'classified/' +filename + '.csv', "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for lines in csv_reader:
                existing_rows.append(lines)
    except FileNotFoundError:
        pass

    with open(directory+filename+'_saved.csv', "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []
        for lines in csv_reader:
            new_row=[]
            image_url = lines[0]
            done = False

            for row in existing_rows:
                if image_url == row[0]:
                    #print(image_url)
                    try:
                        # redo any missing tags
                        if row[1]=='[]' or row[1]=='':
                            print('azure')
                            row[1] = azure_labels(image_url)
                        if row[2]=='[]' or row[2]=='':
                            print('gluon')
                            row[2] = gluon_labels(image_url)
                        if row[3]=='[]' or row[3]=='':
                            print('google labels')
                            row[3] = google_label(image_url)
                        if row[4]=='[]' or row[4]=='':
                            print('google objects')
                            row[4] = google_object_detection(image_url)
                        new_rows.append(row)
                        done = True
                    except Exception as e:
                        print('Excluding due to error:')
                        print(image_url)
                        print(e)
                    break

            if not done:

                if 'image url' not in image_url and 'image_url' not in image_url:
                    #print(image_url)
                    try:
                        new_row.append(lines[0])
                        new_row.append(azure_labels(image_url))
                        new_row.append(gluon_labels(image_url))
                        new_row.append(google_label(image_url))
                        new_row.append(google_object_detection(image_url))
                        new_rows.append(new_row)
                    except Exception as e:
                        print('Excluding due to error:')
                        print(e)
                else:
                    new_row = ['image url','microsoft azure labels','gluon labels','google label description','google object detection']
                    new_rows.append(new_row)

            with open(directory + 'classified/' +filename + '.csv', "w") as csv_file:
                wr = csv.writer(csv_file, delimiter=',')
                wr.writerows(new_rows)