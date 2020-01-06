#coding: utf-8

import json
import os
from typing import Any, Dict

import pandas
import sympy

FILENAME = './alirank.xlsx'
SHEETNAME = 'song_ranking'
df = pandas.read_excel(
    FILENAME, index_col=0, sheet_name=SHEETNAME).reset_index()
COLUMNS = [
    (2005, 2005),
    ('2006#1', 2006),
    ('2006#2', 2006),
    (2007, 2007),
    (2008, 2008),
    (2009, 2009),
    (2010, 2010),
    (2011, 2011),
    (2012, 2012),
    (2013, 2013),
    (2014, 2014),
    (2015, 2015),
    (2016, 2016),
    (2017, 2017),
    (2018, 2018),
    (2019, 2019)]
SETTINGS = ['info.json', 'max.json', 'kinds.json']


def make_json():
    c = 0
    for i in df.index:
        row = df.loc[i].dropna()
        if not df.at[i, 'title']:
            c += 1
            continue

        d = {
            'title': df.at[i, 'title'],
            'kind': str(df.at[i, 'kind']).split('/'),
            'release': int(df.at[i, 'release']),
            'inst': False,
            'works': [],
            'debut': ''
        }
        for col0, col1 in COLUMNS:
            if col0 in row:
                if df.at[i, col0] == '-':
                    d['inst'] = True
                else:
                    d[str(col0)] = int(df.at[i, col0])
            elif df.at[i, 'debut'] <= col1:
                d[str(col0)] = None
        # print(d)
        # for k, v in d.items():
        #     print(k, type(k), v, type(v))
        with open(os.path.join('json', f'{i:03d}.json'), 'w', encoding='utf8') as jf:
            json.dump(d, jf, ensure_ascii=False)
    print(f'continued: {c}')


def check_max():
    max_d = {}
    for filename in os.listdir('json'):
        if filename in SETTINGS:
            continue
        with open(os.path.join('json', filename), encoding='utf8') as jf:
            j = json.load(jf)
        for col0, col1 in COLUMNS:
            if str(col0) in j and j[str(col0)]:
                if max_d.get(col0, 0) < j[str(col0)]:
                    max_d[col0] = j[str(col0)]
    print(max_d)
    with open(os.path.join('json', 'max.json'), 'w', encoding='utf8') as jf:
        json.dump(max_d, jf, ensure_ascii=False)


def concatename_jsons():
    d = {}
    songs = {}
    for filename in os.listdir('json'):
        if filename in SETTINGS:
            continue

        with open(os.path.join('json', filename), encoding='utf8') as jf:
            j = json.load(jf)

        song_uid = filename.split('.')[0]

        songs[f'{int(song_uid) + 1:03d}'] = j
    d['songs'] = songs

    with open(os.path.join('json', 'max.json'), encoding='utf8') as jf:
        j = json.load(jf)
    d['max'] = j
    with open(os.path.join('json', 'kinds.json'), encoding='utf8') as jf:
        j = json.load(jf)
    d['kinds'] = j
    d['works'] = {}

    dump(d)


def check_inst():
    info = load()
    songs: Dict[str, dict] = info.get('songs')
    COLUMNS_FILTERED = list(
        filter(lambda col0_col1: col0_col1[1] >= 2013, COLUMNS))
    updated = False

    for uid, song in songs.items():
        if song['inst']:
            for col0, col1 in COLUMNS_FILTERED:
                if str(col0) in song:
                    updated = True
                    song.pop(str(col0))
    if updated:
        dump(info)


def calc_mean():
    info = load()
    songs = info['songs']
    for uid, song in songs.items():
        count = 0
        k = int(uid)
        s = 0
        for col0, col1 in COLUMNS:
            key = str(col0)
            if key not in song:
                continue
            val = song[key]
            if val is not None:
                if not isinstance(val, (int, float)):
                    print(k, val)
                count += 1
                s += val
        if count:
            r = sympy.Rational(s, count)
            song['mean'] = [r.numerator(), r.denominator()]
        else:
            song['mean'] = None
    dump(info)


def add_ura():
    info = load()
    songs = info['songs']

    for i in df.index:
        row = df.loc[i].dropna()
        if '2019u' in row:
            for uid, song in songs.items():
                if row['title'] == song['title']:
                    song['2019u'] = row['2019u']
                    break
                elif row['title'] == '金色のひつじ' and song['title'] == '金いろのひつじ':
                    song['2019u'] = row['2019u']
                    break
                elif row['title'] == '星降る夜の天文学' and song['title'] == '星降る夜の天文学 ～BEDSIDE ASTRONOMY～':
                    song['2019u'] = row['2019u']
                    break
            songs[uid] = song

    dump(info)


def output_summary():
    info = load()
    songs = info['songs']
    works = info['works']
    n = len(songs)

    d = {
        'no': [None] * n,
        'title': [None] * n,
        'ruby': [None] * n,
        'average': [0] * n,
        'inst': [False] * n,
        'hall_of_fame': [False] * n,
        'works': [[]] * n,
        'debut': [None] * n,
        'date': [None] * n,
        '2019u': [None] * n,
        'initial': [None] * n,
        'kind': [[]] * n}
    for col0, col1 in COLUMNS:
        d[str(col0)] = [None] * n

    for uid, song in songs.items():
        index = int(uid) - 1
        d['no'][index] = int(uid)
        if song['mean']:
            d['average'][index] = (lambda x, y: f'{x/y:.3f}')(*song['mean'])
        else:
            d['average'][index] = None
        for key in d:
            if key in song:
                d[key][index] = song[key]
        d['works'][index] = list(
            map(lambda i: works[i[:3]]['title'] + i[3:], song['works']))
        d['debut'][index] = works[song['debut']]['title']
        d['date'][index] = works[song['debut']]['release']

    with open('summary.json', 'w', encoding='utf8') as jf:
        json.dump(d, jf, ensure_ascii=False)

    pandas.DataFrame(d)[['no',
                         'title',
                         'average',
                         'inst',
                         'hall_of_fame',
                         'debut',
                         'date',
                         'initial',
                         '2005',
                         '2006#1',
                         '2006#2',
                         '2007',
                         '2008',
                         '2009',
                         '2010',
                         '2011',
                         '2012',
                         '2013',
                         '2014',
                         '2015',
                         '2016',
                         '2017',
                         '2018',
                         '2019u',
                         '2019']].to_csv('summary.csv',
                                         index=False,
                                         encoding='utf8')


def load() -> Dict[str, Dict[str, Any]]:
    with open(os.path.join('json', 'info.json'), encoding='utf8') as jf:
        j = json.load(jf)
    return j


def dump(obj: Any):
    with open(os.path.join('json', 'info.json'), 'w', encoding='utf8') as jf:
        json.dump(obj, jf, ensure_ascii=False)


def add_2019():
    info = load()
    songs = info['songs']

    for i in df.index:
        row = df.loc[i].dropna()
        if 2019 in row:
            if row[2019] == '-':
                continue
            for uid, song in songs.items():
                if row['title'] == song['title']:
                    song['2019'] = row[2019]
                    break
                elif row['title'] == '金色のひつじ' and song['title'] == '金いろのひつじ':
                    song['2019'] = row[2019]
                    break
                elif row['title'] == '星降る夜の天文学' and song['title'] == '星降る夜の天文学 ～BEDSIDE ASTRONOMY～':
                    song['2019'] = row[2019]
                    break
            songs[uid] = song
    dump(info)


def drop_100():
    info = load()
    songs = info['songs']
    c = 0
    for uid, song in songs.items():
        f = True
        if song['inst']:
            continue
        if '2019' not in song:
            continue
        if song['2019'] is not None and song['2019'] <= 100:
            continue
        for col0, col1 in COLUMNS:
            k = str(col0)
            if col1 == 2019:
                break
            if k in song:
                if song[k] is None:
                    continue
                if song[k] > 100:
                    f = False
                    break
        if f:
            c += 1
            print(song['title'])
    print(c)


if __name__ == '__main__':
    # make_json()
    # check_max()
    # concatename_jsons()

    # add_2019()

    # check_inst()
    # calc_mean()
    # add_ura()
    output_summary()
    # drop_100()
