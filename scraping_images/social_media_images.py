'''
Each function returns a list of images where each list contains
[image url, date upload, image size, account, title/description, date accessed]
'''

from datetime import datetime
import csv
import time


def flickr_download(search):
    from flickrapi import FlickrAPI

    FLICKR_PUBLIC = '67b52264b7ded98bd1af796bb92b5a14'
    FLICKR_SECRET = '5c7c9c7344542522'

    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    # extras for photo search (can include geo tag, date etc)
    extras = 'url_o, url_c, date_taken, owner_name, o_dim'

    image_data = [['image url', 'date taken', 'image size', 'account', 'description', 'date accessed']]
    for pageNumber in [0,1]:
        # get flickr photos based on search text
        photoSearch = flickr.photos.search(text=search, per_page=250, page=pageNumber, extras=extras)
        photos = photoSearch['photos']
        for element in photos['photo']:
            try:
                image_url = element['url_o']
                size = [element['height_o'], element['width_o']]
            except:
                try:
                    image_url = element['url_c']
                    size = [element['height_c'], element['width_c']]
                except:
                    continue


            photo_id = element['id']
            title = element['title']
            date = element['datetaken']
            owner = element['ownername'] + ' (' +element['owner'] +')'
            info = flickr.photos.getInfo(photo_id = photo_id)
            description = 'Title: ' + title + '\nDescription: '+ info['photo']['description']['_content']

            date_accessed = datetime.now()
            date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

            print([image_url, date, size, owner, description, date_accessed])
            image_data.append([image_url, date, size, owner, description, date_accessed])

            if len(image_data)>250:
                break

    # save image data to file
    file_name = 'flickr '+search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def instagram_download(search):
    from instaloader import Instaloader

    loader = Instaloader()

    posts = loader.get_hashtag_posts(search)
    image_data = [['image url', 'date taken', 'image size', 'account', 'description', 'date accessed']]
    for post in posts:
        time.sleep(10)

        image_url = post.url
        date = post.date
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        owner = post.owner_username
        description = post.caption

        date_accessed = datetime.now()
        date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

        print([image_url, date, '', owner, description, date_accessed])
        image_data.append([image_url, date, '', owner, description, date_accessed])


        if len(image_data)>250:
            break

    # save image data to file
    file_name = 'instagram '+search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)



def reddit_download(search, search2 = ''):
    import praw
    import re

    reddit = praw.Reddit(client_id='TcM6ROJWy6s8ig', client_secret='vJ89hRTSvhOiKoHePbBUq5TPf3sHAw', user_agent='canetoad')
    all = reddit.subreddit('all')

    image_data = [['image url', 'date taken', 'image size', 'account', 'description', 'date accessed']]
    search_terms = [search, search.replace(' ', '')]
    if search2!='':
        # since reddit limits search results, you may need an alternative search term to boost results
        search_terms+=[search2, search2.replace(' ', '')]
    sort_method = ['relevance', 'new', 'hot', 'top', 'comments']
    image_urls = []
    for search_term in search_terms:
        for method in sort_method:
            if len(image_data)>350:
                break
            search_results = all.search(search_term, sort=method, limit=5000)
            count = 0
            for b in search_results:
                count+=1
                print(count)
                owner = b.author
                description = b.title
                date = datetime.utcfromtimestamp(int(b.created_utc))
                date = date.strftime('%Y-%m-%d %H:%M:%S')
                date_accessed = datetime.now()
                date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

                try:
                    #if image urls are in metadata
                    for key in b.media_metadata.keys():
                        # add image url for each image
                        image_url = b.media_metadata[key]['s']['u']
                        size = [b.media_metadata[key]['s']['y'], b.media_metadata[key]['s']['x']]


                        if image_url not in image_urls:
                            print([image_url, date, size, owner, description, date_accessed])
                            image_urls.append(image_url)
                            image_data.append([image_url, date, size, owner, description, date_accessed])

                # otherwise check if submission url is an image
                except AttributeError:
                    image_url = b.url
                    # if the url is an image, it will end in .jpg etc, so use regex to check
                    # this will still include some other urls but can be checked later
                    if len(re.findall('\\.\w+$', image_url))>=1:
                        if image_url not in image_urls:
                            print([image_url, date, '', owner, description, date_accessed])
                            image_urls.append(image_url)
                            image_data.append([image_url, date, '', owner, description, date_accessed])

                if len(image_data) > 350:
                    break

    # save image data to file
    file_name = 'reddit ' + search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def ala_download(search):
    '''
    The raw file comes from ALA using a download url in the following form (change search field for different species):
    https://biocache-ws.ala.org.au/ws/occurrences/offline/download*?q=cane%20toad&email=hmbur5%40student.monash.edu&fields=all_image_url
    which sends a link to your email.
    This image url is then put into the form https://images.ala.org.au/store/b/8/a/0/d6ea9ad8-0293-4144-b40e-9087eb400a8b/original
    where the first 4 digits are the reverse of the last 4 digits from the giant 'url'
    The other columns in this file relate to quality test warnings: which are true if it is a warning (this could be used
    to give a value of quality of data)
    '''
    file_dir = 'image_metadata/ala raw/'+search+'.csv'
    url_id_list = []
    with open(file_dir, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        image_data = [['image url', 'date taken', 'image size', 'account', 'description', 'date accessed']]
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

                date = lines[1]
                owner = lines[2]
                date_accessed = datetime.now()
                date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

                image_data.append([image_url, date, '', owner, '', date_accessed])

                if len(image_data)>250:
                    break

    # save image data to file
    file_name = 'ala ' + search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def inaturalist_download(search):
    file_dir = 'image_metadata/inaturalist raw/' + search + '.csv'
    image_data = [['image url', 'date taken', 'image size', 'account', 'description', 'date accessed']]
    with open(file_dir, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for lines in csv_reader:
            image_url = lines[12]
            if 'image_url' not in image_url:
                owner = lines[6]
                date = lines[2]
                description = lines[15]

                date_accessed = datetime.now()
                date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

                image_data.append([image_url, date, '', owner, description, date_accessed])

                if len(image_data)>250:
                    break

    # save image data to file
    file_name = 'inaturalist ' + search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def random_download():
    import random
    import datetime as datetime_orig
    from flickrapi import FlickrAPI

    FLICKR_PUBLIC = '67b52264b7ded98bd1af796bb92b5a14'
    FLICKR_SECRET = '5c7c9c7344542522'

    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    # extras for photo search (can include geo tag, date etc)
    extras = 'url_o, url_c, date_taken, owner_name, o_dim'

    image_data = [['image url', 'date taken', 'image size', 'account', 'description', 'date accessed']]

    while len(image_data)<=250:
        randint = random.randrange(1577836800, 1609459200)
        random_date_end = datetime.utcfromtimestamp(randint)
        random_date_start = datetime.utcfromtimestamp(randint-5)

        photoSearch = flickr.photos.search(min_taken_date = random_date_start, max_taken_date=random_date_end, extras=extras)
        photos = photoSearch['photos']
        for element in photos['photo']:
            try:
                image_url = element['url_o']
                size = [element['height_o'], element['width_o']]
            except:
                image_url = element['url_c']
                size = [element['height_c'], element['width_c']]


            photo_id = element['id']
            title = element['title']
            date = element['datetaken']
            owner = element['ownername'] + ' (' +element['owner'] +')'
            info = flickr.photos.getInfo(photo_id = photo_id)
            description = 'Title: ' + title + '\nDescription: '+ info['photo']['description']['_content']

            date_accessed = datetime.now()
            date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

            print([image_url, date, size, owner, description, date_accessed])
            image_data.append([image_url, date, size, owner, description, date_accessed])

            break

    # save image data to file
    file_name = 'random'
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


###cane toad###
#ala_download('cane toad')
#reddit_download('cane toad',search2='Rhinella marina')
#instagram_download('canetoad')
#flickr_download('cane toad')
#inaturalist_download('cane toad')

###german wasp###
#ala_download('german wasp')
#reddit_download('german wasp',search2='Vespula germanica')
#instagram_download('germanwasp')
#flickr_download('german wasp')
#inaturalist_download('german wasp')

###camel###
#ala_download('camel')
#reddit_download('camel',search2='Camelus dromedarius')
#instagram_download('camel')
#flickr_download('camel')
inaturalist_download('camel')

###random###
#random_download()