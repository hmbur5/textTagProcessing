from skimage import io
import matplotlib.pyplot as plt
import os
import csv
import sys
import ssl
os.chdir('..')
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

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


# get all csv files
directory = 'scraping_images/image_metadata/classified/'
files = []
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        filename = filename.replace('_saved','')
        files.append(filename.replace('.csv',''))
    else:
        continue


for filename in files:
    # skip over authoritative and random source as we don't need to manually verify these
    if 'ala' in filename or 'random' in filename:
        new_rows = []
        with open(directory +filename + '.csv', "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for lines in csv_reader:
                new_row = lines
                new_row.insert(1, '')
                new_rows.append(new_row)
                if ('random' in filename and len(new_rows)>251) or ('ala' in filename and len(new_rows)>501):
                    break
        with open('manual_verification/verified images/' + filename + '.csv', "w") as csv_file:
            wr = csv.writer(csv_file, delimiter=',')
            wr.writerows(new_rows)
        continue

    if 'flickr rabbit' not in filename:
        continue

    existing_rows = []
    try:
        with open('manual_verification/verified images/' +filename + '.csv', "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for lines in csv_reader:
                if lines[1]== 'True' or lines[1]=='False':
                    existing_rows.append(lines)
                if lines[1] == 'TRUE':
                    lines[1] = 'True'
                    existing_rows.append(lines)
                if lines[1] == 'FALSE':
                    lines[1] = 'False'
                    existing_rows.append(lines)
    except FileNotFoundError:
        pass

    with open(directory+filename+'.csv', "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        new_rows = []
        count = 0
        verified_urls = []
        for lines in csv_reader:
            new_row=[]
            image_url = lines[0]
            verification = None

            if image_url not in verified_urls:
                verified_urls.append(image_url)
            else:
                continue

            count+=1

            for row in existing_rows:

                if image_url == row[0]:
                    verification = row[1]
                    done = True

            print(image_url)
            try:
                if 'image url' not in image_url and 'image_url' not in image_url:
                    new_row = lines
                    if verification is None:
                        new_row.insert(1,manualConfirmation(image_url, filename+' '+str(count)))
                    else:
                        new_row.insert(1, verification)
                    new_rows.append(new_row)
                else:
                    new_row = lines
                    new_row.insert(1,'Manual validation')
                    new_rows.append(new_row)
            except Exception as e:
                pass



            with open('manual_verification/verified images/' +filename + '.csv', "w") as csv_file:
                wr = csv.writer(csv_file, delimiter=',')
                wr.writerows(new_rows)

            if len(new_rows) > 251:
                break
