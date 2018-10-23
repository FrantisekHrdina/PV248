#!/usr/bin/env python3

import sqlite3
import sys
import json


def get_print(cur, print_id):
    tmp_print = {}
    tmp_print['Print Number'] = print_id

    cur.execute('SELECT partiture, edition FROM print WHERE print.id=?', (print_id,))
    print_db = cur.fetchone()

    partiture = False
    if print_db[0] == 'Y':
        partiture = True

    tmp_print['Partiture'] = partiture

    edition_id = print_db[1]

    cur.execute('SELECT name, score, year FROM edition WHERE id=?', (edition_id,))
    edition_db = cur.fetchone()

    tmp_print['Edition'] = edition_db[0]
    tmp_print['Publication Year'] = edition_db[2]

    score_id = edition_db[1]

    cur.execute('SELECT name, genre, key, incipit, year FROM score WHERE id=?', (score_id,))
    score_db = cur.fetchone()

    tmp_print['Title'] = score_db[0]
    tmp_print['Genre'] = score_db[1]
    tmp_print['Key'] = score_db[2]
    tmp_print['Incipit'] = score_db[3]
    tmp_print['Composition Year'] = score_db[4]

    cur.execute('SELECT name, born, died FROM person JOIN score_author on person.id=score_author.composer'
                ' WHERE score_author.score=?', (score_id,))

    composers_db = cur.fetchall()

    composers = []
    for composer in composers_db:
        tmp_composer = {}
        tmp_composer['name'] = composer[0]
        tmp_composer['born'] = composer[1]
        tmp_composer['died'] = composer[2]
        composers.append(tmp_composer)

    tmp_print['Composer'] = composers

    cur.execute('SELECT name, born, died FROM person JOIN edition_author on person.id=edition_author.editor'
                ' WHERE edition_author.edition=?', (edition_id,))

    editors_db = cur.fetchall()

    editors = []
    for editor in editors_db:
        tmp_editor = {}
        tmp_editor['name'] = editor[0]
        tmp_editor['born'] = editor[1]
        tmp_editor['died'] = editor[2]
        editors.append(tmp_editor)

    tmp_print['Editor'] = editors

    cur.execute('SELECT number, name, range FROM voice WHERE score=?', (score_id,))

    voices_db = cur.fetchall()

    for voice in voices_db:
        tmp_voice = {}
        tmp_voice['name'] = voice[1]
        tmp_voice['range'] = voice[2]

        tmp_print['Voice ' + str(voice[0])] = tmp_voice

    return tmp_print


def get_composers(cur, like_param):
    like_param = '%' + like_param + '%'
    cur.execute('SELECT name from person WHERE person.name LIKE ? ', (like_param,))

    composers_names = []

    result = cur.fetchall()
    for i in result:
        composers_names.append(i[0])

    return composers_names


def main():
    conn = sqlite3.connect('scorelib.dat')
    # For debugging SQL
    # conn.set_trace_callback(print)
    if len(sys.argv) != 2:
        print('Wrong number of arguments')
        print('Example: ')
        print('./search.py Bach')
        sys.exit(1)

    cur = conn.cursor()

    composers_names = get_composers(cur, sys.argv[1])
    result_json = {}
    for composer in composers_names:
        cur.execute('SELECT print.id FROM score JOIN score_author on score.id=score_author.score '
                    ' JOIN person on person.id=score_author.composer'
                    ' JOIN edition on edition.score=score.id'
                    ' JOIN print on print.edition=edition.id'
                    ' WHERE person.name=?', (composer,))

        result = cur.fetchall()

        print_ids = list()
        for i in result:
            print_ids.append(i[0])

        print_list = list()
        for print_id in print_ids:
            print_list.append(get_print(cur, print_id))

        result_json[composer] = print_list

    print(json.dumps(result_json, ensure_ascii=False, sort_keys=False, indent=4))


if __name__ == '__main__':
    main()
