# comparing google cloud vision's tags for ala records of cane toads and australian green tree frog
import numpy as np
import csv
import matplotlib.pyplot as plt

def getTagFreq(file):
    directory = 'scraping_images/image_metadata/classified/'

    images = []
    with open(directory + file, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []
        for lines in csv_reader:
            if 'image url' in lines or 'image_url' in lines:
                continue
            images.append(lines)
    images = images[:250]

    allTags = []
    for item in images:

        #print(item)
        #print(classifierIndex)
        tags = item[3]

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
    counts = list(counts[sorted_indices])
    labels = list(labels[sorted_indices])

    return(labels,counts)




labelsCT, countsCT = getTagFreq('ala cane toad.csv')
labelsGTF, countsGTF = getTagFreq('ala aus green tree frog.csv')

labels = list(set(labelsCT + labelsGTF))
counts = []
for label in labels:
    labelCounts = []
    try:
        labelCounts.append(countsCT[labelsCT.index(label)])
    except ValueError:
        labelCounts.append(0)
    try:
        labelCounts.append(countsGTF[labelsGTF.index(label)])
    except ValueError:
        labelCounts.append(0)
    counts.append(labelCounts)

countsOrig = counts.copy()
counts.sort(key = lambda x: max(x), reverse=True)
counts = counts[0:20]

sorted_labels = []
for count in counts:
    sorted_labels.append(labels[countsOrig.index(count)])

countsCT = []
countsGTF = []
for count in counts:
    countsCT.append(count[0])
    countsGTF.append(count[1])

labels = sorted_labels
print(len(labels))
print(countsCT)
print(countsGTF)
ticks = range(len(countsCT))

n = 20
r = np.arange(n)
width = 0.25

plt.bar(r, countsCT, color='b',
        width=width, edgecolor='black',
        label='Cane toad')
plt.bar(r + width, countsGTF, color='g',
        width=width, edgecolor='black',
        label='Aus green tree frog')


plt.legend(['Cane toad', 'Australian green tree frog'])
plt.xticks(ticks, labels, rotation='vertical')
plt.title('Tag frequencies of ALA species records')
plt.tight_layout()
plt.show()

