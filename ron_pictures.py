from bs4 import BeautifulSoup
import requests
import random
import urllib.request
import shutil
import subprocess   
from PIL import Image
import os
import logging




def get_album(table):
    # get list of lowest level directories from home page
    list_of_links = []

    for grouping in table:
        for links in grouping.find_all('a'):
            list_of_links.append(links['href'].replace('http://planetnothing.com',''))


    deepest_links = []
    for i in list_of_links:
        for j in list_of_links:
            to_write = True
            if i in j and i != j:
                to_write = False
                break
        if to_write:
            deepest_links.append(i)

    return deepest_links

def get_picture_info(album):
    # give an album, return the 
    album_soup = BeautifulSoup(requests.get(album).text, 'lxml')

    page_blob = album_soup.find('div',{'id':'gsPages'}).get_text().split('\n\n')
    page_blob.remove('Page:')
    page_blob.remove('')
    page_blob.remove('\n')
    nbr_pages = max([int(i) for i in page_blob])

    page_choice = random.randint(1,nbr_pages)



    picture_page = '{}?g2_page={}'.format(album, page_choice)
    
    return picture_page


def get_picture(url, picture_page):
    picture_soup = BeautifulSoup(requests.get(picture_page).text, 'lxml')
    picture_table = picture_soup.find('table',{'id':'gsThumbMatrix'})



    picture_links = [h['href'] for h in picture_table.find_all('a')]

    picture_choice = url + random.choice(picture_links) + '?g2_imageViewsIndex=50'

    picture_soup = BeautifulSoup(requests.get(picture_choice).text,'lxml')
    image_info_soup = picture_soup.find('div',{'id':'gsContent'})

    # picture_name = image_info_soup.find('img')['alt']
    new_file_name = picture_soup.find('div',{'class':'block-core-BreadCrumb'}).get_text().replace('\n\n','->').replace('\n','').replace('->Albums->','')
    print(new_file_name)


    picture_direct_link = url + image_info_soup.find('img')['src']

    return picture_direct_link, new_file_name


def change_desktop(path):
    print(path)
    SCRIPT = """osascript<<END
    tell application "Finder"
    set desktop picture to POSIX file "{}"
    end tell
    END""".format(path)


    subprocess.Popen(SCRIPT, shell=True)    

def check_picture(image_path):
    im = Image.open(image_path)


def main():
    
    # Get list of all album links
    url = 'http://www.planetnothing.com'
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    picture_table = soup.find_all('table')[0].find_all('tr')

    # choose a random album from the directory list
    chosen_album = url + random.choice(get_album(picture_table))

    # return random page number within album 
    picture_info = get_picture_info(chosen_album)

    # get picture url and name/directory
    actual_picture, picture_to_be_named = get_picture(url, picture_info)


    # where to save the image
    # download_path = "/Users/kcrawford/Desktop/DesktopImages/{}.jpg".format(picture_name)
    download_path = "/Users/kcrawford/Desktop/DesktopImages/{}.jpg".format(picture_to_be_named)

    # save image
    with urllib.request.urlopen(actual_picture) as response, open(download_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    # change desktop
    change_desktop(download_path)

    os.system('''sqlite3 ~/Library/Application\ Support/Dock/desktoppicture.db "update data set value ='{}'"'''.format(download_path))
    os.system('killall Dock')






if __name__ == '__main__':
    unhappy_with_picture = True
    while unhappy_with_picture:
        main()
        new_answer = input('Do you want a new picture?: ') + ' '
        if new_answer[0] == 'y':
            pass
        else:
            unhappy_with_picture = False



    # check_picture()
