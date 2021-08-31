from datetime import datetime
import time
import csv
import pandas as pd
import numpy as np
import os
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

from google.cloud.vision import types
from google.cloud import vision
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "google_keys.json"
#client = vision.ImageAnnotatorClient()


def reddit_download(search):
    import praw
    import re

    reddit = praw.Reddit(client_id='TcM6ROJWy6s8ig', client_secret='vJ89hRTSvhOiKoHePbBUq5TPf3sHAw', user_agent='canetoad')
    all = reddit.subreddit('all')

    image_url_list = []

    from psaw import PushshiftAPI

    api = PushshiftAPI(reddit)

    image_data = [['image url', 'date taken', 'image size', 'dimensions','extension','location','account', 'description', 'date accessed']]
    search_terms = [search, 'german yellowjacket']
    for search_term in search_terms:
        search_results = api.search_submissions(q=search_term, limit=100000)
        for b in search_results:
            # exclude over 18 content
            if b.over_18 == True:
                continue
            owner = b.author
            description = b.title
            date = datetime.utcfromtimestamp(int(b.created_utc))
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            date_accessed = datetime.now()
            date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

            dimensions='NA'
            size = 'NA'
            extension = 'NA'
            location = 'NA'

            try:
                #if image urls are in metadata
                for key in b.media_metadata.keys():
                    # add image url for each image
                    image_url = b.media_metadata[key]['s']['u']
                    size = [b.media_metadata[key]['s']['y'], b.media_metadata[key]['s']['x']]

                    if image_url not in image_url_list:
                        image_url_list.append(image_url)
                    else:
                        continue
                    print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
                    image_data.append([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])


            # otherwise check if submission url is an image
            except AttributeError:
                image_url = b.url
                # if the url is an image, it will end in .jpg etc, so use regex to check
                # this will still include some other urls but can be checked later
                if len(re.findall('\\.\w+$', image_url))>=1:
                    if image_url not in image_url_list:
                        image_url_list.append(image_url)
                    else:
                        continue
                    print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
                    image_data.append([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])

            except KeyError:
                continue

            print(len(image_data))
            if len(image_data) > 10000:
                break

    # save image data to file
    file_name = 'reddit ' + search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)

def flickr_download(search):
    from flickrapi import FlickrAPI

    FLICKR_PUBLIC = '67b52264b7ded98bd1af796bb92b5a14'
    FLICKR_SECRET = '5c7c9c7344542522'

    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    # extras for photo search (can include geo tag, date etc)
    extras = 'url_o, url_c, date_taken, owner_name, o_dim, geo'
    image_url_list = []

    image_data = [['image url', 'date taken', 'image size', 'dimensions','extension','location','account', 'date accessed']]
    for pageNumber in range(1000):
        # get flickr photos based on search text
        photoSearch = flickr.photos.search(text=search, per_page=250, page=pageNumber, extras=extras)
        photos = photoSearch['photos']
        for element in photos['photo']:
            try:
                image_url = element['url_o']
                dimensions = [element['height_o'], element['width_o']]
            except:
                try:
                    image_url = element['url_c']
                    dimensions = [element['height_c'], element['width_c']]
                except:
                    continue


            photo_id = element['id']
            title = element['title']
            date = element['datetaken']
            owner = element['ownername'] + ' (' +element['owner'] +')'
            #info = flickr.photos.getInfo(photo_id = photo_id)
            #description = 'Title: ' + title + '\nDescription: '+ info['photo']['description']['_content']
            if element['longitude']!=0 or element['latitude']!=0:
                location = 'long: '+element['longitude']+', lat: '+element['latitude']
            else:
                location = 'NA'
            size = 'NA'
            extension = 'NA'

            date_accessed = datetime.now()
            date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

            if image_url not in image_url_list:
                image_url_list.append(image_url)
            else:
                continue

            print([image_url, date, size, dimensions, extension, location, owner, date_accessed])
            image_data.append([image_url, date, size, dimensions, extension, location, owner, date_accessed])

            if len(image_data)>20000:
                break
            if len(image_data)%100==0:
                # save image data to file
                file_name = 'flickr ' + search
                with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
                    wr = csv.writer(myfile, delimiter=',')
                    wr.writerows(image_data)
                time.sleep(10)
            print(len(image_data))



def random_download_flickr():
    import random
    import datetime as datetime_orig
    from flickrapi import FlickrAPI

    FLICKR_PUBLIC = '67b52264b7ded98bd1af796bb92b5a14'
    FLICKR_SECRET = '5c7c9c7344542522'

    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    # extras for photo search (can include geo tag, date etc)
    extras = 'url_o, url_c, date_taken, owner_name, o_dim, geo'

    image_data = [['image url', 'date taken', 'image size', 'dimensions','extension','location','account', 'date accessed']]

    while len(image_data)<=10000:
        randint = random.randrange(1577836800, 1609459200)
        random_date_end = datetime.utcfromtimestamp(randint)
        random_date_start = datetime.utcfromtimestamp(randint-5)

        photoSearch = flickr.photos.search(min_taken_date = random_date_start, max_taken_date=random_date_end, extras=extras)
        photos = photoSearch['photos']
        for element in photos['photo']:
            try:
                image_url = element['url_o']
                dimensions = [element['height_o'], element['width_o']]
            except:
                try:
                    image_url = element['url_c']
                    dimensions = [element['height_c'], element['width_c']]
                except:
                    pass

            if element['longitude']!=0 or element['latitude']!=0:
                location = 'long: '+element['longitude']+', lat: '+element['latitude']
            else:
                location = 'NA'
            size = 'NA'
            extension = 'NA'


            photo_id = element['id']
            title = element['title']
            date = element['datetaken']
            owner = element['ownername'] + ' (' +element['owner'] +')'
            #info = flickr.photos.getInfo(photo_id = photo_id)
            #description = 'Title: ' + title + '\nDescription: '+ info['photo']['description']['_content']

            date_accessed = datetime.now()
            date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

            print([image_url, date, size, dimensions, extension, location, owner, date_accessed])
            image_data.append(
                [image_url, date, size, dimensions, extension, location, owner, date_accessed])

            break

    if len(image_data) % 100 == 0:
        # save image data to file
        file_name = 'random'
        with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
            wr = csv.writer(myfile, delimiter=',')
            wr.writerows(image_data)
        time.sleep(10)



def google_label(image_url):
    tagNames = ['hi', 'hannah']
    tagString = str(tagNames)
    return tagString

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


#reddit_download('wild rabbit')
#flickr_download('wild rabbit')
random_download_flickr()

file_names = ['reddit wild rabbit', 'flickr wild rabbit', 'random']

for file_name in file_names:
    df = pd.read_csv('image_metadata/'+file_name+'.csv')
    df['tags'] = ''

    start_time = time.time()
    for i in df.index:
        url = df['image url'][i]
        df.at[i, 'tags'] = google_label(url)
    df.to_csv(file_name+' tagged.csv')
    print(file_name+' time')
    print(time.time()-start_time)