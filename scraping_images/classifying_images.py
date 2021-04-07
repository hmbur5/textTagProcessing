import os
import csv


import os
from google.cloud.vision import types
from google.cloud import vision
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "google_keys.json"
client = vision.ImageAnnotatorClient()
def google_object_detection(image_url):
    source = types.ImageSource(image_uri=image_url)
    image = types.Image(source=source)

    # if cannot get image from url, try downloading image and reuploading
    if image=='problem':
        img = urllib.request.urlopen(image_url)
        img = Image.open(img)
        content = img.read()
        image = types.Image(content=content)
    # Performs label detection on the image file
    response = client.object_localization(image=image)

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
    # if cannot get image from url, try downloading image and reuploading
    if image=='problem':
        img = urllib.request.urlopen(image_url)
        img = Image.open(img)
        content = img.read()
        image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)

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
    try:
        url_file = 'current_image'
        fname = mx.test_utils.download(image_url, fname='thumbnails/' + url_file, overwrite=True)
    except Exception as e:
        print(e)
        print(image_url)
    try:
        img = mx.ndarray.array(cv2.cvtColor(cv2.imread(fname), cv2.COLOR_BGR2RGB))
    except Exception as e:
        print(e)
        print(image_url)

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

        try:
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
        except urllib.error.HTTPError:
            print(image_url)
        except Exception as e:
            print(e)
            print(image_url)

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
    if filename.endswith(".csv"):
        files.append(filename.replace('.csv',''))
    else:
        continue

for filename in files:

    with open(directory+filename+'.csv', "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []
        for lines in csv_reader:
            new_row=[]
            image_url = lines[0]
            if 'image url' not in image_url and 'image_url' not in image_url:
                print(image_url)
                new_row.append(lines[0])
                new_row.append(azure_labels(image_url))
                new_row.append(gluon_labels(image_url))
                new_row.append(google_label(image_url))
                new_row.append(google_object_detection(image_url))
                new_rows.append(new_row)
            else:
                new_row = ['image url','microsoft azure labels','gluon labels','google label description','google object detection']
                new_rows.append(new_row)


    with open(directory + 'classified/' +filename + '.csv', "w") as csv_file:
        wr = csv.writer(csv_file, delimiter=',')
        wr.writerows(new_rows)