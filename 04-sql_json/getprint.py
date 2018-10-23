#!/usr/bin/env python3

import sqlite3
import sys
import json


def main():
    conn = sqlite3.connect('scorelib.dat')
    # conn.set_trace_callback(print)
    if len(sys.argv) != 2:
        print('Wrong number of arguments')
        print('Example: ')
        print('./getprint.py 125')
        sys.exit(1)

    cur = conn.cursor()

    cur.execute('SELECT score FROM print JOIN edition on print.edition=edition.id WHERE print.id=?', (sys.argv[1],))

    score = cur.fetchone()
    if score is None:
        print('No entry with this print.id found')
        sys.exit(1)

    cur.execute('SELECT person.name, person.born, person.died FROM person,score_author WHERE score=? AND person.id=score_author.composer', (score[0],))

    composers = cur.fetchall()

    composers_list = list()
    for composer in composers:
        tmp_composer = {}
        tmp_composer["name"] = composer[0]
        tmp_composer["born"] = composer[1]
        tmp_composer["died"] = composer[2]
        composers_list.append(tmp_composer)

    print(json.dumps(composers_list, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    main()