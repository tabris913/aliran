# coding: utf-8

import json
import os
from typing import Any, Dict

import pandas
import sympy

COLUMNS = [
    'r2005',
    'r2006#1',
    'r2006#2',
    'r2007',
    'r2008',
    'r2009',
    'r2010',
    'r2011',
    'r2012',
    'r2013',
    'r2014',
    'r2015',
    'r2016',
    'r2017',
    'r2018',
    'r2019']


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
        'r2019u': [None] * n,
        'initial': [None] * n,
        'kind': [[]] * n,
        'remarks': [None] * n}
    works2 = [[]] * n
    for col0 in COLUMNS:
        d[col0] = [None] * n

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
            map(lambda i: works[i[:3]]['title'], song['works']))
        works2[index] = list(
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
                         'r2005',
                         'r2006#1',
                         'r2006#2',
                         'r2007',
                         'r2008',
                         'r2009',
                         'r2010',
                         'r2011',
                         'r2012',
                         'r2013',
                         'r2014',
                         'r2015',
                         'r2016',
                         'r2017',
                         'r2018',
                         'r2019u',
                         'r2019',
                         'remarks']].to_csv('summary.csv',
                                          index=False,
                                          encoding='utf8')

    # works.json
    kinds = info['kinds']
    d = {
        'title': [],
        'kind': [],
        'date': []
    }
    for uid, work in works.items():
        d['title'] += [work['title']]
        d['kind'] += [work['kind']]
        d['date'] += [work['release']]
    with open('works.json', 'w', encoding='utf8') as jf:
        json.dump(d, jf, ensure_ascii=False)


def calc_mean():
    info = load()
    songs = info['songs']
    for uid, song in songs.items():
        count = 0
        k = int(uid)
        s = 0
        for col0 in COLUMNS:
            if col0 not in song:
                continue
            val = song[col0]
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


def load() -> Dict[str, Dict[str, Any]]:
    with open(os.path.join('json', 'info.json'), encoding='utf8') as jf:
        j = json.load(jf)
    return j


def dump(obj: Any):
    with open(os.path.join('json', 'info.json'), 'w', encoding='utf8') as jf:
        json.dump(obj, jf, ensure_ascii=False)


if __name__ == '__main__':
    # calc_mean()
    output_summary()
