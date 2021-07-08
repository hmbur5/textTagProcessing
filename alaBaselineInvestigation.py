from tagFrequencyAnalysis import getTagFreq
from tagFrequencyAnalysis import tagFrequencyDifference
import csv
import matplotlib.pyplot as plt
import random
import scipy
import numpy as np
import os



def tagFrequencyAnalysis(directory, authoritativeFile, randomFile, randomFile1, comparisonFiles, classifierIndex):
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

    randomImages1 = []
    with open(directory + randomFile1, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []
        for lines in csv_reader:
            if 'image url' in lines or 'image_url' in lines:
                continue
            randomImages1.append(lines)
    randomImages1 = randomImages1[1:]

    # split authoritative into two randomly
    #authoritativeImagesReference = random.sample(authoritativeImages, int(len(authoritativeImages)/2))
    #authoritativeImagesComparison = [item for item in authoritativeImages if item not in authoritativeImagesReference]
    tagsAuth, freqAuth = getTagFreq(authoritativeImages, classifierIndex)

    # split authoritative images into 10 samples of 50, then find TFD between that and the original 500
    # find average and standard deviation of this
    random.shuffle(authoritativeImages)
    sample_no = 5
    baselines = []
    for sampleIndex in range(sample_no):
        authoritative_sample = authoritativeImages[sampleIndex::sample_no]
        tagsRef, freqRef = getTagFreq(authoritative_sample, classifierIndex)
        baselines.append(tagFrequencyDifference(tagsRef, freqRef, tagsAuth, freqAuth))
    baseline = np.mean(baselines)
    std_baseline = np.std(baselines)
    print('ala')
    print(baseline)


    tagsRand, freqRand = getTagFreq(randomImages, classifierIndex)
    noise = tagFrequencyDifference(tagsRand, freqRand, tagsAuth, freqAuth)
    tagsRand1, freqRand1 = getTagFreq(randomImages1, classifierIndex)
    noise1 = tagFrequencyDifference(tagsRand1, freqRand1, tagsAuth, freqAuth)
    print(str(str(noise) +'\t\t'+str(noise1)))
    print((noise-noise1)/noise)
    print('random')
    print(classifierIndex)
    print(noise)

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
        print(comparisonFile)
        print(classifierIndex)
        print(TFD)


        percentage = 1 - (TFD - baseline)/(noise - baseline)

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

        legend.append(comparisonFile+' '+str(len(comparisonImages)) +' images')
        markers = ['o', 'v', 'P', 'p', '*']
        colors = ['','','red', 'green', 'blue', 'orange']
        axs.scatter([TFD],[verified/(verified+unverified)], color = colors[classifierIndex], marker=markers[legend.index(comparisonFile+' '+str(len(comparisonImages)) +' images')])
        axs.plot([baseline, noise], [1, 0], color = colors[classifierIndex])
        axs.errorbar(baseline, 1, yerr=None, xerr=std_baseline, color=colors[classifierIndex])
        xyList.append([percentage, verified/(verified+unverified)])

        f = lambda m, c: plt.plot([], [], marker=m, color=c, ls="none")[0]
        handles = [f("s", colors[i]) for i in range(2, 6)]
        handles += [f(markers[i], "k") for i in range(5)]
        labels = []
        for i in range(2, 6):
            labels.append(header[i])
        for label in legend:
            label = label.replace('.csv', '')
            label = label.replace('rabbit', '')
            label = label.replace('canetoad', '')
            label = label.replace('cane toad', '')
            label = label.replace('german wasp', '')
            label = label.replace('germanwasp', '')
            labels.append(label.replace('.csv', ''))
        axs.legend(handles, labels, framealpha=1)

        if 'lickr' in comparisonFile:
            tags2 = tagsAuth
            freq2 = freqAuth
            allTags = {}
            count = 0
            for tags1, freq1 in [[tagsComp, freqComp], [tagsRand, freqRand]]:
                for index1, tag1 in enumerate(tags1):
                    if tag1 in tags2:
                        index2 = list(tags2).index(tag1)
                        difference = freq1[index1] - freq2[index2]
                        if tag1 not in allTags.keys():
                            allTags[tag1] = [0,0]
                        allTags[tag1][count] = difference
                    else:
                        difference = freq1[index1]
                        if tag1 not in allTags.keys():
                            allTags[tag1] = [0,0]
                        allTags[tag1][count] = difference
                for index2, tag2 in enumerate(tags2):
                    if tag2 not in tags1:
                        difference = -freq2[index2]
                        if tag2 not in allTags.keys():
                            allTags[tag2] = [0,0]
                        allTags[tag2][count] = difference
                count+=1

            tagsOrder = []
            while len(tagsOrder)<len(allTags.keys()):
                max = 0
                for key in allTags.keys():
                    if key not in tagsOrder:
                        tfd1 = allTags[key][0]
                        tfd2 = allTags[key][1]
                        if np.abs(tfd1)>max or np.abs(tfd2)>max:
                            maxKey = key
                            max = np.max([np.abs(tfd1), np.abs(tfd2)])
                tagsOrder.append(maxKey)

            '''
            plt.clf()
            rand = []
            comp = []
            for tag in tagsOrder:
                rand.append(allTags[tag][1])
                comp.append(allTags[tag][0])
            plt.scatter(tagsOrder[0:25], rand[0:25])
            plt.scatter(tagsOrder[0:25], comp[0:25])
            plt.legend(['Random', 'Flickr'])
            plt.xticks(rotation=90)
            plt.title('Tag frequency differences from ALA')
            plt.ylabel('(Tag freq comparison) - (Tag freq authoritative)')
            plt.show()'''




# get all csv files
directory = 'manual_verification/verified images/'
files = []
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        files.append(filename.replace('_saved',''))
    else:
        continue

files.sort()

comparison = []
for filename in files:

    if 'toad' not in filename and 'rand' not in filename:
        continue
    #if 'instagram' in filename and 'wild' not in filename:
    #    continue

    if 'ala' in filename:
        # if looking at rabbit, use the validated ala file
        if 'rabbit' in filename:
            if 'validated' in filename:
                authoritative = filename
        else:
            authoritative = filename
    elif 'random_reddit' in filename:
        rand1 = filename
    elif 'random.csv'==filename:
        rand = filename
    else:
        comparison.append(filename)

print('german wasp')
print('random flickr    \t\trandom reddit')

xyList = []
fig, axs = plt.subplots(1)
for classifierIndex in range(2,6):
    tagFrequencyAnalysis(directory, authoritative, rand, rand1, comparison, classifierIndex)


axs.set_ylabel('Observed fraction of desired images')
axs.set_xlabel('TFD from all ALA images')
axs.set_title('Rabbit data - sampling ALA for baseline')
axs.set_xlim([0,25])
plt.show()