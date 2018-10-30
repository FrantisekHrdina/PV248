#!/usr/bin/env python3

import scorelib
import sqlite3
import sys
import os


def init_database(cur):
    person = 'create table person (id integer primary key not null, born integer, died integer, name varchar not null);'
    score = 'create table score (id integer primary key not null, name varchar, genre varchar, key varchar, incipit varchar, year integer);'
    voice = 'create table voice (id integer primary key not null, number integer not null, score integer references score(id) not null, range varchar, name varchar);'
    edition = 'create table edition (id integer primary key not null, score integer references score(id) not null, name varchar, year integer);'
    score_author = 'create table score_author(id integer primary key not null, score integer references score(id) not null, composer integer references person(id) not null);'
    edition_author = 'create table edition_author(id integer primary key not null, edition integer references edition(id) not null, editor integer references person(id) not null);'
    print = 'create table print (id integer primary key not null, partiture char(1) default \'N\' not null, edition integer references edition(id));'

    cur.execute(person)
    cur.execute(score)
    cur.execute(voice)
    cur.execute(edition)
    cur.execute(score_author)
    cur.execute(edition_author)
    cur.execute(print)


def save_persons(cur, persons):
    persons_ids = list()
    for person in persons:
        cur.execute('SELECT id FROM person WHERE name=(?)', (person.name,))
        row = cur.fetchone()
        if row is None:
            cur.execute('INSERT INTO person (name, born, died) VALUES (?, ?, ?)',
                        (person.name, person.born, person.died))
            persons_ids.append(cur.lastrowid)

        else:
            persons_ids.append(row[0])
            if person.born is not None:
                cur.execute('UPDATE person SET born=(?) WHERE id=(?)', (person.born, row[0]))
            if person.died is not None:
                cur.execute('UPDATE person SET died=(?) WHERE id=(?)', (person.died, row[0]))

    return persons_ids


def save_print(cur, print_id, partiture, edition_id):
    if partiture is None:
        partiture = 'N'
    else:
        if partiture:
            partiture = 'Y'
        else:
            partiture = 'N'

    cur.execute('INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)', (print_id, partiture, edition_id))

    return cur.lastrowid


def save_score(cur, composition):
    params = []
    #params.append(composition.name)

    if composition.name is None:
        name_query = 'name is NULL'
    else:
        name_query = 'name=?'
        params.append(composition.name)

    if composition.genre is None:
        genre_query = 'genre is NULL'
    else:
        genre_query = 'genre=?'
        params.append(composition.genre)

    if composition.key is None:
        key_query = 'key is NULL'
    else:
        key_query = 'key=?'
        params.append(composition.key)
    if composition.incipit is None:
        incipit_query = 'incipit is NULL'
    else:
        incipit_query = 'incipit=?'
        params.append(composition.incipit)
    if composition.year is None:
        year_query = 'year is NULL'
    else:
        year_query = 'year=?'
        params.append(composition.year)

    cur.execute('SELECT id FROM score WHERE ' + name_query + ' and ' + genre_query + ' and ' + key_query +
                ' and ' + incipit_query + ' and ' + year_query,
                (params))

    row = cur.fetchone()

    if row is None:
        cur.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)',
              (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
        return cur.lastrowid
    else:
        tmp_composition = scorelib.Composition()
        tmp_composition.name = composition.name
        tmp_composition.genre = composition.genre
        tmp_composition.key = composition.key
        tmp_composition.incipit = composition.incipit
        tmp_composition.year = composition.year

        cur.execute('SELECT name from person JOIN score_author ON person.id=score_author.composer WHERE score=?', (row[0],))

        result = cur.fetchall()
        if result is not None:
            for composer in result:
                tmp_composer = scorelib.Person()
                tmp_composer.name = composer[0]
                tmp_composition.authors.append(tmp_composer)

        cur.execute('SELECT number, name, range from voice WHERE score=?', (row[0],))

        result = cur.fetchall()

        if result is not None:
            for i in range(0, len(result)):
                tmp_voice = scorelib.Voice()
                tmp_voice.number = int(result[i][0])
                tmp_voice.name = result[i][1]
                tmp_voice.range = result[i][2]
                tmp_composition.voices.append(tmp_voice)

        if composition.__eq__(tmp_composition):
            return row[0]
        else:
            cur.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)',
                        (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
            return cur.lastrowid


def save_edition(cur, edition, score_id):
    params = []

    if edition.name is None:
        edition_query = 'name is NULL'
    else:
        edition_query = 'name=?'
        params.append(edition.name)

    params.append(score_id)

    cur.execute('SELECT id FROM edition WHERE ' + edition_query + ' and score=?', (params))

    row = cur.fetchone()

    if row is None:
        cur.execute('INSERT INTO edition (name, score) VALUES (?, ?)',
             (edition.name, score_id))
        return cur.lastrowid
    else:
        tmp_edition = scorelib.Edition()
        tmp_edition.name = edition.name
        tmp_edition.composition = edition.composition

        cur.execute('SELECT name from person JOIN edition_author ON person.id=edition_author.editor WHERE edition=?',
                    (row[0],))

        result = cur.fetchall()
        if result is not None:
            for editor in result:
                tmp_editor = scorelib.Person()
                tmp_editor.name = editor[0]
                tmp_edition.authors.append(tmp_editor)

        if edition.__eq__(tmp_edition):
            return row[0]
        else:
            cur.execute('INSERT INTO edition (name, score) VALUES (?, ?)',
                        (edition.name, score_id))
            return cur.lastrowid


def save_voices(cur, voices, score_id):
    voices_ids = list()

    for voice in voices:
        cur.execute('INSERT INTO voice (number, range, name, score) VALUES (?, ?, ?, ?)',
                        (voice.number, voice.range, voice.name, score_id))
        voices_ids.append(cur.lastrowid)

    return voices_ids


def save_to_database(cur, prints_list):
    for print_item in prints_list:
        # Save Composers
        composers_ids = save_persons(cur, print_item.composition().authors)
        # Save Editors
        editors_ids = save_persons(cur, print_item.edition.authors)

        score_id = save_score(cur, print_item.composition())

        edition_id = save_edition(cur, print_item.edition, score_id)
        print_id = save_print(cur, print_item.print_id, print_item.partiture, edition_id)

        voices_ids = save_voices(cur, print_item.composition().voices, score_id)

        # Relationship tables
        # score-author
        for composer_id in composers_ids:
            cur.execute('INSERT INTO score_author (score, composer) VALUES (?, ?)', (score_id, composer_id))

        # edition-author
        for editor_id in editors_ids:
            cur.execute('INSERT INTO edition_author (edition, editor) VALUES (?, ?)', (edition_id, editor_id))


def main():
    print()
    if len(sys.argv) != 3:
        print('Wrong number of arguments')
        print('Example: ')
        print('./import.py scorelib.txt scorelib.dat')

    # Just for comfortable testing
    # os.remove(sys.argv[2])

    conn = sqlite3.connect(sys.argv[2])
    # For debugging SQL queries
    # conn.set_trace_callback(print)

    cur = conn.cursor()
    # with open('scorelib.sql') as fp:
    #     cur.executescript(fp.read())

    init_database(cur)

    prints_list = scorelib.load(sys.argv[1])

    save_to_database(cur, prints_list)
    conn.commit()


if __name__ == '__main__':
    main()