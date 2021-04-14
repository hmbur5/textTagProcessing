import csv
from datetime import datetime
from skimage import io
import matplotlib.pyplot as plt
import sys
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# looking at rabbit ala files, and only adding them to image metadata if they are high quality


search = 'rabbit'


def manualConfirmation(image_url, title):
    '''
    Function to open an image, and wait for key press Y or N to return True if user decides it is a candidate of the
    species, and false if not
    :param image_url: image urls
    '''
    global manualConfirm
    manualConfirm = ''
    # print each image and wait for key press
    image = io.imread(image_url)
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.set_title(title+'\nc for candidate, n for not')
    # calls function press when key is pressed
    fig.canvas.mpl_connect('key_press_event', lambda event: pressTest(event, image_url, plt))
    plt.show()
    return manualConfirm

def pressTest(event, image_url, plt):
    global manualConfirm
    sys.stdout.flush()
    if event.key == 'c':
        plt.close()
        manualConfirm = True
    elif event.key == 'n':
        plt.close()
        manualConfirm = False


# get more ala images
file_dir = 'scraping_images/image_metadata/ala raw/'+search+'.csv'
url_id_list = []
with open(file_dir, "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    image_data = [['image url', 'date taken', 'image size', 'dimensions','extension','location','account', 'description', 'date accessed']]
    for lines in csv_reader:
        url_field = lines[0]
        if url_field != '' and 'image' not in url_field:
            url_string = 'https://images.ala.org.au/store/'
            # add last 4 digits in reverse order
            for i in range(1, 5):
                url_string += str(url_field[-i])
                url_string += '/'
            url_string += url_field
            url_string += '/original'
            image_url = url_string

            if manualConfirmation(image_url, ''):
                pass
            # skip over non rabbit images
            else:
                continue

            date = lines[1]
            if date == '':
                date='NA'
            owner = lines[2]
            if owner == '':
                owner = 'NA'
            lat = lines[3]
            long = lines[4]
            if lat!= '' or long!='':
                location = 'long: ' + long + ', lat: ' + lat
            else:
                location = 'NA'
            date_accessed = datetime.now()
            date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

            size = 'NA'
            dimensions = 'NA'
            extension = 'NA'
            description = 'NA'

            print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
            image_data.append(
                [image_url, date, size, dimensions, extension, location, owner, description, date_accessed])

            if len(image_data)>550:
                break

# save image data to file
file_name = 'ala ' + search
with open('improving_rabbits/' + file_name + '.csv', 'w') as myfile:
    wr = csv.writer(myfile, delimiter=',')
    wr.writerows(image_data)