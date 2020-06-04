from model_for_emb.model_part3 import AlignDlib
from model_for_emb.model_part2 import create_model
import numpy as np
import asyncio
from free_conn_base import main
import cv2
import httplib2
import pandas as pd
import vk
import time


def align_image(img):
    return alignment.align(96, img, alignment.getLargestFaceBoundingBox(img),
                           landmarkIndices=AlignDlib.OUTER_EYES_AND_NOSE)


def distance(emb1, emb2):
    return np.sum(np.square(emb1 - emb2))


def load_image(path):
    img = cv2.imread(path, 1)
    # OpenCV loads images with color channels
    # in BGR order. So we need to reverse them
    return img[..., ::-1]


def img_requests(url):
    h = httplib2.Http('.cache')
    response, content = h.request(url)
    if response['status'] == '200':
        path = 'file.jpg'
        out = open(path, 'wb')
        out.write(content)
        out.close()
        img = load_image(path)
        img_al = align_image(img)
        try:
            img = (img_al / 255.).astype(np.float32)
            embedded = nn4_small2_pretrained.predict(np.expand_dims(img, axis=0))[0]
            return embedded
        except TypeError:
            return 'None'
    else:
        print(response)
        return img_requests(url)


nn4_small2_pretrained = create_model()
nn4_small2_pretrained.load_weights('nn4.small2.v1.h5')
alignment = AlignDlib('models/landmarks.dat')

session = vk.AuthSession(app_id='', user_login='rus91ad@mail.ru', user_password='')
api = vk.API(session, v='5.95', lang='ru', timeout=10)

Countries = api.database.getCountries()
# status_list = [2, 3, 4, 7, 8]
status_list = [6]
count_requests = 0
row_db = 0
sex = 1

try:
    for status in status_list:
        for country in Countries['items']:
            city_list = api.database.getCities(country_id=country['id'], need_all=0, count=1000)
            count_requests += 1
            for city in city_list['items']:
                time.sleep(0.35)
                search_new = api.users.search(q='',
                                              country=country['id'], city=city['id'],
                                              offset=0,
                                              count=1000,
                                              sex=2, status=status,
                                              fields='photo_max_orig, relation, verified')
                print(country['title'], city['title'], len(search_new['items']))
                count_requests += 1
                df = pd.DataFrame.from_dict(search_new['items'])
                if status in [6]:
                    df = df[ \
                        (df['is_closed'] == False) & \
                        (df['verified'] == 0)]
                else:
                    df = df[ \
                        (~df['relation_partner'].isna())& \
                        (df['is_closed'] == False) & \
                        (df['verified'] == 0)]

                for row in df.index:
                    person = df.loc[row]['id']
                    if status in [6]:
                        men = "None"
                        emb_men = 'None'
                    else:
                        men = df.loc[row]['relation_partner']['id']
                        time.sleep(0.35)
                        emb_men = img_requests(
                            api.users.get(user_ids=men, fields='photo_max_orig')[0]['photo_max_orig'])

                    time.sleep(0.35)
                    emb_person = img_requests(df.loc[row]['photo_max_orig'])
                    if emb_person != 'None':
                        asyncio.run(main(id_val=person,
                                         link_photo=str(df.loc[row]['photo_max_orig']),
                                         vector=emb_person,
                                         sex=2
                                         ))
                        row_db += 1
                        if row_db == 50:
                                exit()

                    count_requests += 1


finally:
    print(count_requests)


