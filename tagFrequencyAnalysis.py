import random
import csv
import numpy as np
import matplotlib.pyplot as plt
import os
import numpy as np
import scipy.stats
os.chdir('..')


def getTagFreq(images, classifierIndex):
    '''

    :param images: List of elements in form [image url, tags]
    :return: list of tags and list of their corresponding frequencies
    '''
    allTags = []
    for item in images:

        #print(item)
        #print(classifierIndex)
        tags = item[classifierIndex]

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
        if tag2 not in tags1:
            difference = freq2[index2]
            sumOfDifference+=np.abs(difference)
    return(sumOfDifference)

def tagFrequencyAnalysis(directory, authoritativeFile, randomFile, comparisonFiles, classifierIndex):
    '''
    :param authoritativeFile: csv file of authoritative source of desired images, in form [image url, tags]
    :param randomFile:  csv file of random images, in same form
    :param comparisonFiles: list of csv files of comparison images in same form
    :return:
    '''
    global xyList

    authoritativeImages = []
    with open(directory+authoritativeFile, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []
        for lines in csv_reader:
            if 'image url' in lines or 'image_url' in lines:
                continue
            authoritativeImages.append(lines)
    authoritativeImages = authoritativeImages[1:]

    randomImages = []
    with open(directory+randomFile, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []
        for lines in csv_reader:
            if 'image url' in lines or 'image_url' in lines:
                continue
            randomImages.append(lines)
    randomImages = randomImages[1:]
    print('random')
    print(len(randomImages))

    # split authoritative into two randomly
    authoritativeImagesReference = random.sample(authoritativeImages, int(len(authoritativeImages)/2))
    authoritativeImagesComparison = [item for item in authoritativeImages if item not in authoritativeImagesReference]
    print('author1')
    print(len(authoritativeImagesReference))
    print('author2')
    print(len(authoritativeImagesComparison))


    tagsRef,freqRef = getTagFreq(authoritativeImagesReference, classifierIndex)
    tagsAuth,freqAuth = getTagFreq(authoritativeImagesComparison, classifierIndex)
    tagsRand,freqRand = getTagFreq(randomImages, classifierIndex)


    baseline = tagFrequencyDifference(tagsRef, freqRef, tagsAuth, freqAuth)
    noise = tagFrequencyDifference(tagsRand, freqRand, tagsAuth, freqAuth)

    legend = []

    for comparisonFile in comparisonFiles:
        comparisonImages = []
        with open(directory+comparisonFile, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            new_rows = []
            for lines in csv_reader:
                comparisonImages.append(lines)
        header = comparisonImages[0]
        comparisonImages = comparisonImages[1:251]

        tagsComp, freqComp = getTagFreq(comparisonImages, classifierIndex)
        TFD = tagFrequencyDifference(tagsComp, freqComp, tagsAuth, freqAuth)

        percentage = 1 - (TFD - baseline)/(noise - baseline)
        print(comparisonFile)
        print(len(comparisonImages))

        verified = 0
        unverified = 0
        with open(directory + comparisonFile, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for lines in csv_reader:
                for row in comparisonImages:
                    image_url = row[0]
                    if 'image url' in image_url or 'image_url' in image_url:
                        continue
                    if image_url == lines[0]:
                        if lines[1] == 'True':
                            verified+=1
                        elif lines[1] == 'False':
                            unverified +=1
        print('observed')
        print(verified/(verified+unverified))

        legend.append(comparisonFile+' '+str(len(comparisonImages)) +' images')
        markers = ['o', 'v', 's', 'p', '*']
        colors = ['','','red', 'green', 'blue', 'orange']
        plt.scatter([percentage],[verified/(verified+unverified)], color = colors[classifierIndex], marker=markers[legend.index(comparisonFile+' '+str(len(comparisonImages)) +' images')])
        xyList.append([percentage, verified/(verified+unverified)])


    f = lambda m, c: plt.plot([], [], marker=m, color=c, ls="none")[0]
    handles = [f("s", colors[i]) for i in range(2,6)]
    handles += [f(markers[i], "k") for i in range(5)]
    labels = []
    for i in range(2,6):
        labels.append(header[i])
    for label in legend:
        label = label.replace('.csv', '')
        label = label.replace('rabbit', '')
        label = label.replace('canetoad', '')
        label = label.replace('cane toad', '')
        label = label.replace('german wasp', '')
        label = label.replace('germanwasp', '')
        labels.append(label.replace('.csv',''))
    print(labels)
    plt.legend(handles, labels, framealpha=1)


# get all csv files
directory = 'manual_verification/verified images/'
files = []
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        files.append(filename.replace('_saved',''))
    else:
        continue

files.sort()
print(files)

comparison = []
for filename in files:

    if 'rabbit' not in filename and 'rand' not in filename:
        continue

    if 'ala' in filename:
        # if looking at rabbit, use the validated ala file
        if 'rabbit' in filename:
            if 'validated' in filename:
                authoritative = filename
        else:
            authoritative = filename
    elif 'random' in filename:
        rand = filename
    else:
        comparison.append(filename)


xyList = []
for classifierIndex in range(2,6):
    tagFrequencyAnalysis(directory, authoritative, rand, comparison, classifierIndex)


# regression
xyList = np.array(xyList)
x = list(xyList[:,0])
y = list(xyList[:,1])
reg = scipy.stats.linregress(x, y)
print('Gradient')
print(reg.slope)
print('Intercept')
print(reg.intercept)
print('R2')
print(reg.rvalue)


plt.plot([0,1],[0,1])
plt.ylabel('Observed fraction of desired images')
plt.xlabel('Predicted fraction of desired images')
plt.title('Rabbit')
plt.annotate('y = %.2fx + %.2f\nR^2 = %.2f'%(reg.slope, reg.intercept, reg.rvalue),[0,0.75])
plt.show()
