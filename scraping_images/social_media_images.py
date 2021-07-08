'''
Each function returns a list of images where each list contains
[image url, date upload, image size, dimensions, extension, location, account, title/description, date accessed]
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
    extras = 'url_o, url_c, date_taken, owner_name, o_dim, geo'
    image_url_list = []

    image_data = [['image url', 'date taken', 'image size', 'dimensions','extension','location','account', 'description', 'date accessed']]
    for pageNumber in [1,2]:
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
            info = flickr.photos.getInfo(photo_id = photo_id)
            description = 'Title: ' + title + '\nDescription: '+ info['photo']['description']['_content']
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

            print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
            image_data.append([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])

            if len(image_data)>350:
                break

    # save image data to file
    file_name = 'flickr '+search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def instagram_download(search):
    from instaloader import Instaloader
    import re

    loader = Instaloader()
    loader.interactive_login('hanbooboo1')

    posts = loader.get_hashtag_posts(search)
    image_data = [['image url', 'date taken', 'image size', 'dimensions','extension','location','account', 'description', 'date accessed']]
    for post in posts:
        time.sleep(10)
        try:
            image_url = post.url
            date = post.date
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            owner = post.owner_username
            notUnique = False
            for previous in image_data:
                if owner == previous[6]:
                    notUnique = True
            if notUnique:
                continue
            description = post.caption

            date_accessed = datetime.now()
            date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

            size='NA'
            dimensions = 'NA'
            extension = 'NA'
            if post.location != None:
                try:
                    loc = str(post.location)
                    long = re.findall(r'lng=\-*\d+\.*\d+',loc)[0]
                    long = long.replace('lng=','')
                    lat = re.findall(r'lat=\-*\d+\.*\d+',loc)[0]
                    lat = lat.replace('lat=','')
                    location = 'long: ' + long + ', lat: ' + lat
                except Exception as e:
                    print(post.location)
                    print(e)
                    location = 'NA'

            else:
                location = 'NA'
        except KeyError:
            pass

        print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
        image_data.append([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])

        if len(image_data)>300:
            break

    # save image data to file
    file_name = 'instagram '+search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)



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
        search_results = api.search_submissions(q=search_term, limit=5000)
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

            if len(image_data) > 400:
                break

    # save image data to file
    file_name = 'reddit ' + search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def ala_download(search):
    '''
    The raw file comes from ALA using a download url in the following form (change search field for different species):
    https://biocache-ws.ala.org.au/ws/occurrences/offline/download*?q=cane%20toad&email=hmbur5%40student.monash.edu&fields=all_image_url,occurrence_date,user_id,latitude,longitude
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
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def inaturalist_download(search):
    file_dir = 'image_metadata/inaturalist raw/' + search + '.csv'
    image_data = [['image url', 'date taken', 'image size', 'dimensions','extension','location','account', 'description', 'date accessed']]
    with open(file_dir, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for lines in csv_reader:
            image_url = lines[12]
            if 'image_url' not in image_url:
                owner = lines[6]
                date = lines[2]
                description = lines[15]
                lat = lines[21]
                long = lines[22]
                location = 'long: ' + long + ', lat: ' + lat

                date_accessed = datetime.now()
                date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

                size = 'NA'
                dimensions = 'NA'
                extension = 'NA'

                print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
                image_data.append(
                    [image_url, date, size, dimensions, extension, location, owner, description, date_accessed])

                if len(image_data)>300:
                    break

    # save image data to file
    file_name = 'inaturalist ' + search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def random_download_flickr():
    import random
    import datetime as datetime_orig
    from flickrapi import FlickrAPI

    FLICKR_PUBLIC = '67b52264b7ded98bd1af796bb92b5a14'
    FLICKR_SECRET = '5c7c9c7344542522'

    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    # extras for photo search (can include geo tag, date etc)
    extras = 'url_o, url_c, date_taken, owner_name, o_dim, geo'

    image_data = [['image url', 'date taken', 'image size', 'dimensions','extension','location','account', 'description', 'date accessed']]

    while len(image_data)<=300:
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
            info = flickr.photos.getInfo(photo_id = photo_id)
            description = 'Title: ' + title + '\nDescription: '+ info['photo']['description']['_content']

            date_accessed = datetime.now()
            date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

            print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
            image_data.append(
                [image_url, date, size, dimensions, extension, location, owner, description, date_accessed])

            break

    # save image data to file
    file_name = 'random'
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)


def random_download_reddit():
    import random
    import datetime as datetime_orig
    import praw
    import re

    reddit = praw.Reddit(client_id='TcM6ROJWy6s8ig', client_secret='vJ89hRTSvhOiKoHePbBUq5TPf3sHAw',
                         user_agent='canetoad')
    all = reddit.subreddit('all')

    image_url_list = []

    from psaw import PushshiftAPI

    api = PushshiftAPI(reddit)

    image_data = [
        ['image url', 'date taken', 'image size', 'dimensions', 'extension', 'location', 'account', 'description',
         'date accessed']]
    while len(image_data)<400:
        randint = random.randrange(1577836800, 1609459200)
        print(randint)

        search_results = api.search_submissions(limit=100, before=randint, after=randint-5)
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

            dimensions = 'NA'
            size = 'NA'
            extension = 'NA'
            location = 'NA'

            try:
                # if image urls are in metadata
                for key in b.media_metadata.keys():
                    # add image url for each image
                    image_url = b.media_metadata[key]['s']['u']
                    size = [b.media_metadata[key]['s']['y'], b.media_metadata[key]['s']['x']]

                    if image_url not in image_url_list:
                        image_url_list.append(image_url)
                    else:
                        continue
                    print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
                    image_data.append(
                        [image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
                    break


            # otherwise check if submission url is an image
            except AttributeError:
                image_url = b.url
                # if the url is an image, it will end in .jpg etc, so use regex to check
                # this will still include some other urls but can be checked later
                if len(re.findall('\\.\w+$', image_url)) >= 1:
                    if image_url not in image_url_list:
                        image_url_list.append(image_url)
                    else:
                        continue
                    print([image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
                    image_data.append(
                        [image_url, date, size, dimensions, extension, location, owner, description, date_accessed])
                    break
            except KeyError:
                pass


    # save image data to file
    file_name = 'random_reddit'
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)

def twitter_download(search):
    import time
    import selenium
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from webdriver_manager.chrome import ChromeDriverManager

    browser = webdriver.Chrome(ChromeDriverManager().install())

    image_data = [['image url', 'date taken', 'image size','dimensions','extension','location', 'account', 'description', 'date accessed']]

    # iterate through searches within certain dates to get enough results
    for year in [2021,2020, 2019, 2018, 2017, 2016,2015,2014,2013,2012]:
        for month in [1,2,3,4,5,6,7,8,9,10,11,12]:
            for day in [1,16]:
                url = 'https://twitter.com/search?q=' + search + '%20until%3A' + str(year) + '-' + str(
                    month) + '-' + str(day + 14) + '%20since%3A' + str(year) + '-' + str(month) + '-' + str(
                    day) + '&src=typed_query&f=image'

                if year ==2021 and month>4:
                    continue

                # download the page as html for parsing
                try:
                    browser.get(url)
                except selenium.common.exceptions.WebDriverException:
                    time.sleep(10)
                    browser.get(url)

                time.sleep(1)
                body = browser.find_element_by_tag_name('body')
                for _ in range(10):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.2)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                try:
                    tags = soup.find('div', attrs={'aria-label': 'Timeline: Search timeline'})
                    tags = tags.contents[0]
                    tweets = tags.contents
                    for tweet in tweets:
                        try:
                            content = tweet.contents
                            while len(content)==1:
                                content = content[0].contents
                            while len(content)==2:
                                data = content[0].contents
                                content = content[1].contents
                            if len(content)>2:
                                image = content[1].findAll('img')
                                image_url = image[0]['src']
                                image_url.replace('amp;','')
                                text = content[0]
                                try:
                                    text= text.content[0]
                                    text= text.content[0]
                                    text= text.content[0]
                                except Exception as e:
                                    pass
                                description = text.get_text()


                                while len(data)<3:
                                    data = data[0].contents
                                username = data[0]
                                try:
                                    username = username.content[-1]
                                    username = username.content[-1]
                                    username = username.content[-1]
                                    username = username.content[-1]
                                    username = username.content[-1]
                                    username = username.content[-1]
                                except:
                                    pass
                                username = username.get_text()
                                date = data[2]
                                date = date.find('time')
                                date = date['datetime']

                                date_accessed = datetime.now()
                                date_accessed = date_accessed.strftime('%Y-%m-%d %H:%M:%S')

                                dimensions = 'NA'
                                size = 'NA'
                                extension = 'NA'
                                location = 'NA'

                                print([image_url, date, size, dimensions, extension, location, username, description,
                                       date_accessed])
                                image_data.append(
                                    [image_url, date, size, dimensions, extension, location, username, description,
                                     date_accessed])

                                if len(image_data)>300:
                                    break
                        except Exception as e:
                            print(e)
                    print(len(image_data))
                except AttributeError:
                    time.sleep(120)
                except Exception as e:
                    print(e)

    # save image data to file
    file_name = 'twitter ' +search
    with open('image_metadata/' + file_name + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, delimiter=',')
        wr.writerows(image_data)




###cane toad###
#ala_download('cane toad')
#reddit_download('cane toad')
#instagram_download('canetoad')
#flickr_download('cane toad')
#inaturalist_download('cane toad')
#twitter_download('canetoad')

###german wasp###
#ala_download('german wasp')
#reddit_download('german wasp')
#instagram_download('germanwasp')
#flickr_download('german wasp')
#inaturalist_download('german wasp')
#twitter_download('german wasp')


###rabbit###
#ala_download('rabbit')
#reddit_download('rabbit')
#instagram_download('wildrabbit')
#flickr_download('rabbit')
#inaturalist_download('rabbit')
#twitter_download('rabbit')


###random###
#random_download_flickr()
random_download_reddit()