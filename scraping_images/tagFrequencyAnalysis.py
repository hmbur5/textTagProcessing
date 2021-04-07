import random
import csv
import numpy as np
import matplotlib.pyplot as plt

def getTagFreq(images):
    '''

    :param images: List of elements in form [image url, tags]
    :return: list of tags and list of their corresponding frequencies
    '''

    allTags = []
    for item in images:

        tags = item[1]

        tags = tags[1:-1]  # remove [ and ] from string
        if len(tags) == 0:
            newTags = []
        else:
            tags = list(tags.split(", "))  # convert back to list
            # remove quotation marks from each string
            newTags = []
            for tag in tags:
                newTags.append(tag[1:-1])
        allTags+=newTags

    # get tag frequency
    labels, counts = np.unique(allTags, return_counts=True)
    counts = counts/len(images)
    sorted_indices = np.argsort(-counts)
    counts = counts[sorted_indices]
    labels = labels[sorted_indices]

    return(labels,counts)

def tagFrequencyDifference(tags1, freq1, tags2, freq2):
    sumOfDifference = 0
    for index1,tag1 in enumerate(tags1):
        if tag1 in tags2:
            index2 = list(tags2).index(tag1)
            difference = freq1[index1]-freq2[index2]
            sumOfDifference+=np.abs(difference)
        else:
            difference = freq1[index1]
            sumOfDifference+=np.abs(difference)
    for index2,tag2 in enumerate(tags2):
        if tag2 in tags1:
            difference = freq1[index2]
            sumOfDifference+=np.abs(difference)
    return(sumOfDifference)

def tagFrequencyAnalysis(authoritativeFile, randomFile, comparisonFiles):
    '''

    :param authoritativeFile: csv file of authoritative source of desired images, in form [image url, tags]
    :param randomFile:  csv file of random images, in same form
    :param comparisonFiles: list of csv files of comparison images in same form
    :return:
    '''

    authoritativeImages = []
    with open(authoritativeFile, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []
        for lines in csv_reader:
            authoritativeImages.append(lines)

    # split authoritative into two randomly
    authoritativeImagesReference = random.sample(authoritativeImages, int(len(authoritativeImages)/2))
    authoritativeImagesComparison = [item for item in authoritativeImages if item not in authoritativeImagesReference]

    tagsRef,freqRef = getTagFreq(authoritativeImagesReference)
    tagsAuth,freqAuth = getTagFreq(authoritativeImagesComparison)

    print(tagFrequencyDifference(tagsRef, freqRef, tagsAuth, freqAuth))



tagFrequencyAnalysis('image_metadata/classified/ala camel.csv',
                     'image_metadata/classified/random.csv',['image_metadata/classified/flickr camel.csv'])