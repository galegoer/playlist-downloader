import csv, os
import random
import requests
from datetime import date
import sys


def numSongs():
    with open('remaining_songs.csv', mode='r', encoding='utf-8') as song_file:
        return sum(1 for line in song_file)
    
def findImage(song_title, artist, limit=5):
    base_url = 'http://ws.audioscrobbler.com/2.0/'

    params = {
        'method': 'album.search',
        'api_key': os.getenv("FM_API_KEY"),
        'artist': artist,
        'track': song_title,
        'format': 'json'
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    # print(data)

    # Extract cover art URL from the response
    cover_art_url = None
    if 'track' in data and 'album' in data['track']:
        album = data['track']['album']
        if 'image' in album and len(album['image']) > 0:
            cover_art_url = album['image'][-1]['#text']
    print(cover_art_url)

    return cover_art_url

def deleteRow(row_to_delete):
    temp_file, org_file = 'temp_remaining.csv', 'remaining_songs.csv'
    # Open the original CSV file for reading
    with open(org_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Remove the line from the rows list
    rows.pop(row_to_delete)

    # Write the modified rows to the temporary file
    with open(temp_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    # Replace the original file with the temporary file
    os.replace(temp_file, org_file)

    # print('Line removed successfully')
    return


def pullDailyRand(testing):
    # exclude header
    total_songs = numSongs() - 1
    print(total_songs)
    rand_num = random.randint(1, total_songs)
    print(rand_num)
    with open('remaining_songs.csv', encoding='utf-8') as song_file:
        reader = csv.reader(song_file)
        csv_headings = next(reader)
        for row in range(0,rand_num):
            rand_song = next(reader)
    
    day = date.today().strftime("%b-%d-%Y")
    rand_song.append(day)
    print(rand_song)

    # if we are testing random song do not delete
    if(not testing):
        # write to completed songs
        with open('completed_songs.csv', mode='a', encoding='utf-8') as completed_songs:
            writer = csv.writer(completed_songs, delimiter=",", quotechar='"', lineterminator="\n")
            writer.writerow(rand_song)

        # delete song from remaining_songs
        deleteRow(rand_num)
    
    return rand_song

def sendMessage(message):
    webhook_url = os.getenv("DISC_WEBHOOK")
    payload = {
        'content': message
    }

    # Send the HTTP POST request to the webhook URL
    response = requests.post(webhook_url, json=payload)

    # Check the response status code
    if response.status_code == 204:
        print('Message sent successfully')
    else:
        print(f'Failed to send message. Status code: {response.status_code}')
        print(response.text)
    return


if __name__ == "__main__":

    if len(sys.argv) > 1:
        daily_rand = pullDailyRand(True)
    else:
        daily_rand = pullDailyRand(False)
        image = findImage(daily_rand[1], daily_rand[2])
        message1 = f'Title: {daily_rand[1]} \n Artist: {daily_rand[2]} \n Album: {daily_rand[3]}'
        sendMessage(message1)
        sendMessage(image)