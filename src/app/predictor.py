from model_for_emb.model_part3 import AlignDlib
from PIL import Image
from keras.preprocessing.image import img_to_array
import numpy as np
import cv2
import cvlib as cv
from asyncpg import pool
import pandas as pd


def align_image(img, alignment):
    return alignment.align(96, img, alignment.getLargestFaceBoundingBox(img),
                           landmarkIndices=AlignDlib.OUTER_EYES_AND_NOSE)


def distance(emb1, emb2):
    return np.sum(np.square(emb1 - emb2))


def gender_predict(gender_detection, image):
    # image = cv2.imread(img)
    face, confidence = cv.detect_face(image)
    i = 1
    classes = ['man', 'woman']
    for idx, f in enumerate(face):
        (startX, startY) = f[0], f[1]
        (endX, endY) = f[2], f[3]
        face_crop = np.copy(image[startY:endY, startX:endX])
        face_crop = cv2.resize(face_crop, (96, 96))
        face_crop = face_crop.astype("float") / 255.0
        face_crop = img_to_array(face_crop)
        face_crop = np.expand_dims(face_crop, axis=0)
        conf = gender_detection.predict(face_crop)[0]
        if conf[0] > conf[1]:
            i = 0
        return [classes[i], conf]


def str2list(vec):
    vec = vec[1:-1].replace('  ', ' ')
    vec = vec.replace('\n', '')
    vec = vec.split(' ')
    vec = list(filter(None, vec))
    vec = [float(x) for x in vec[:]]
    return vec


async def query_dataframe(pool: pool.Pool):
    async with pool.acquire() as conn:
        result = await conn.fetch(
                f'''
                    SELECT * FROM public.vectors;
                ''')
        return result


async def query_free_df(pool: pool.Pool):
    async with pool.acquire() as conn:
        result = await conn.fetch(
                f'''
                    SELECT * FROM public.freeFemale;
                ''')
        return result


async def predict_class(img, nn4_small2_pretrained, alignment, gender_detection, pool):
    img = Image.open(img)
    img = np.array(img)
    class_gender = gender_predict(gender_detection, img.copy())
    # Image.fromarray(img).save("thumbnail", "JPEG")
    img_al = align_image(img, alignment)
    img = (img_al / 255.).astype(np.float32)
    embedded = nn4_small2_pretrained.predict(np.expand_dims(img, axis=0))[0]

    if class_gender[0] == 'woman':
        field = 'vector_voman'
        rev_field = 'vector_man'
        sex = 2
    else:
        field = 'vector_man'
        rev_field = 'vector_voman'
        sex = 1

    select_result = await query_dataframe(pool)
    df = pd.DataFrame(columns=['id', 'vector_man', 'vector_voman', 'id_man', 'id_voman'])
    df.inplace = True
    for idx, i in enumerate(select_result):
        df.loc[idx] = [i[0], str2list(i[1]), str2list(i[2]), i[3], i[4]]
    df['distance'] = df[field].apply(lambda x: distance(embedded, x))
    df = df.sort_values('distance', ascending=True)
    top_5 = df.iloc[:5][rev_field]
    select_free_result = await query_free_df(pool)
    df_free = pd.DataFrame(columns=['id', 'link_photo', 'vector', 'sex'])
    df_free.inplace = True
    for idx, i in enumerate(select_free_result):
        df_free.loc[idx] = [i[0], i[1], str2list(i[2]), i[3]]

    result = []
    df_free = df_free[df_free['sex'] == str(sex)]
    for emb in top_5:
        df_free['distance'] = df_free['vector'].apply(lambda x: distance(np.array(emb), np.array(x)))
        idx_person = df_free['distance'].idxmin()
        result.append([df_free.loc[idx_person]['id'],
                       df_free.loc[idx_person]['link_photo']])

    return result


