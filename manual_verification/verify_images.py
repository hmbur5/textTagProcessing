from skimage import io
import matplotlib.pyplot as plt
import os
import csv
import sys
import ssl
os.chdir('..')
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def manualConfirmation(image_url):
    '''
    Function to open an image, and wait for key press Y or N to return True if user decides it is a candidate of the
    species, and false if not
    :param image_url: image urls
    '''
    global manualConfirm
    # print each image and wait for key press
    image = io.imread(image_url)
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.set_title('y for candidate, n for not')
    # calls function press when key is pressed
    fig.canvas.mpl_connect('key_press_event', lambda event: pressTest(event, image_url, plt))
    plt.show()
    return manualConfirm

def pressTest(event, image_url, plt):
    global manualConfirm
    sys.stdout.flush()
    if event.key == 'y':
        plt.close()
        manualConfirm = True
    elif event.key == 'n':
        plt.close()
        manualConfirm = False


# get all csv files
directory = 'scraping_images/image_metadata/classified/'
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
                new_row = lines
                new_row.insert(1,manualConfirmation(image_url))
                new_rows.append(new_row)
            else:
                new_row = lines
                new_row.insert(1,'Manual validation')
                new_rows.append(new_row)
            if len(new_rows)>10:
                break


    with open('manual_verification/verified images/' +filename + '.csv', "w") as csv_file:
        wr = csv.writer(csv_file, delimiter=',')
        wr.writerows(new_rows)