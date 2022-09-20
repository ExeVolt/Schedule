#!"C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe"
import requests
import re
import os
from time import sleep, strftime, localtime

import pytesseract
from PIL import Image
import json

custom_config = r'--oem 3 --psm 6 --tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'
path = 'C:/xampp/htdocs/data/schedule/'
schedule_path = path + 'schedule.jpg'
cropped_schedule_path = path + 'cropped.jpg'
cropped_schedule_row_path = path + 'rows/%i_row.jpg'

rows_count = 0
last_schedule_name = ''

group_to_search = 'РМ-419'
time_to_check = 3600


def get_group_name_pos(text):
    global custom_config
    img = Image.open(schedule_path)
    edited_image = img.load()
    for x in range(0, img.size[0], 1):
        for y in range(0, img.size[1], 1):
            if edited_image[x, y][0] < 120 and edited_image[x, y][1] < 120 and edited_image[x, y][2] < 120:
                edited_image[x, y] = (255, 255, 255)
    img_data = pytesseract.image_to_data(img, lang='rus', config=custom_config, output_type='dict')
    for i in range(len(img_data['level'])):
        if img_data['text'][i] == text:
            return img_data['left'][i], img_data['top'][i]


def get_rows_text():
    text = list()
    for i in range(0, rows_count):
        row_text = ''
        img = Image.open(cropped_schedule_row_path % i)
        img_data = pytesseract.image_to_data(img, lang='rus', config=custom_config, output_type='dict')
        for j in range(len(img_data['level'])):
            row_text += img_data['text'][j] + ' '
        text.append(row_text)
    for row in range(len(text)):
        text[row] = text[row].replace('|', '').replace('‘', '').strip()
        while '  ' in text[row]:
            text[row] = text[row].replace('  ', ' ')
    return text


def check_rows_by_size():
    global rows_count
    for i in range(0, rows_count):
        file_path = cropped_schedule_row_path % i
        if os.stat(file_path).st_size < 15_000:
            os.remove(file_path)
            rows_count -= 1


def get_schedule_url():
    regex = r"<img width=\"1000\" src=\"(.?\S+)\""
    host = "https://amurkst.ru"
    url = requests.get(host + "/branch3/service/zamena-raspisaniya.php")
    html_text = url.text
    matches = re.findall(regex, html_text, re.MULTILINE)
    return host + matches[1]


def get_schedule_name():
    name = get_schedule_url()
    return name.split('/')[-1]


def download_schedule():
    url = get_schedule_url()
    img_data = requests.get(url).content
    with open(schedule_path, 'wb') as image:
        image.write(img_data)


def get_group_schedule_rectangle(group_name):
    founded_bottom = False
    borders = [0, 0, 0, 0]
    x, y = get_group_name_pos(group_name)
    original_img = Image.open(schedule_path)
    size_x, size_y = original_img.size
    img = original_img.load()
    # search for the left border
    for i in range(x, 0, -1):
        if img[i, y] == (0, 0, 0):
            borders[0] = i + 2
            break
    # search for the right border
    for i in range(x, size_x, 1):
        if img[i, y] == (0, 0, 0):
            borders[2] = i - 2
            break
    # search for the top border
    for i in range(y, 0, -1):
        if img[x, i] == (0, 0, 0):
            borders[1] = i - 2
            break
    # search for the bottom border
    for i in range(y + 100, size_y, 1):
        if founded_bottom:
            break
        for j in range(borders[0], borders[2], 1):
            if img[j, i][0] > 100 and img[j, i][1] < 20:
                borders[3] = i + 2
                founded_bottom = True
                break
    if not founded_bottom:
        borders[3] = size_y
    original_img.crop(borders).save(cropped_schedule_path)


def splitting_the_table():
    global rows_count
    img = Image.open(cropped_schedule_path)
    img_map = img.load()
    split_coord = list()
    black_found = False
    for y in range(10, img.height, 1):
        if img_map[img.width - 1, y] == (255, 255, 255) and black_found:
            split_coord.append(y)
            black_found = False
        if img_map[img.width - 1, y] == (0, 0, 0) and not black_found:
            black_found = True
    rows_count = len(split_coord) - 1
    for i in range(1, len(split_coord), 1):
        box = (0, split_coord[i - 1], img.width, split_coord[i])
        row_img = img.crop(box)
        row_img.save(cropped_schedule_row_path % (i - 1))


def write_schedule_to_json():
    rows_text = get_rows_text()
    data_to_write = dict()
    data_to_write.update({"Information": {"Schedule_date": last_schedule_name[0:-4],
                                          "Group_name": group_to_search}})
    counter = 0
    for row in rows_text:
        number = int(row.split(' ')[0]) if row.split(' ')[0].isdigit() else ''
        lesson = row[row.rindex(row.split(' ')[1]):row.index(
                     row.split(' ')[-1]) if row.split(' ')[-1].isdigit() else None].strip()
        cabinet = int(row.split(' ')[-1]) if row.split(' ')[-1].isdigit() else ''
        data_to_write.update({'Number_%s' % counter: {'Lesson_number': number, 'Lesson': lesson, 'Cabinet': cabinet}})
        counter += 1
    with open(path + 'schedule.json', 'w') as data:
        json.dump(data_to_write, data, indent=4)


def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    global last_schedule_name
    print("Checks every %i minutes" % (time_to_check / 60))

    while True:
        print('-' * 50)
        website_schedule_name = get_schedule_name()
        print('The check started at: ' + strftime("%H:%M:%S", localtime()))
        print('Website schedule name: ' + website_schedule_name)
        if last_schedule_name != website_schedule_name:
            last_schedule_name = website_schedule_name
            print('Start downloading schedule...')
            download_schedule()
            print('Schedule downloaded: ' + schedule_path)
            print('Searching for %s group' % group_to_search)
            get_group_schedule_rectangle(group_to_search)
            print('Schedule cropped into table: ' + cropped_schedule_path)
            splitting_the_table()
            check_rows_by_size()
            for i in range(rows_count):
                print('Schedule table is divided into rows: ' + cropped_schedule_row_path % i)
            print('Schedule rows: \r\n' + '\r\n'.join(get_rows_text()))
            write_schedule_to_json()
        else:
            print('There is no new schedule')
        print("Checks is over at: " + strftime("%H:%M:%S", localtime()))
        sleep(time_to_check)


if __name__ == '__main__':
    main()
