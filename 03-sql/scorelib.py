#!/usr/bin/env python3

import re


class Print:
    def __init__(self):
        self.print_id = None
        self.edition = None
        self.partiture = None

    def composition(self):
        return self.edition.composition

    def format(self):
        print('Print Number: ' + str(self.print_id))
        print('Composer: ', end='')
        composers = self.edition.composition.authors
        for i in range(0, len(composers)):
            print(composers[i].name, end='')

            if composers[i].born is not None or composers[i].died is not None:
                print(' (', end='')

            if composers[i].born is not None:
                print(str(composers[i].born), end='')

            if composers[i].born is not None or composers[i].died is not None:
                print('--', end='')
            if composers[i].died is not None:
                print(str(composers[i].died),end='')

            if composers[i].born is not None or composers[i].died is not None:
                print(')', end='')

            if i + 1 != len(composers):
                print(';', end=' ')
        print()
        print('Title: ' + to_string(self.edition.composition.name))
        print('Genre: ' + to_string(self.edition.composition.genre))
        print('Key: ' + to_string(self.edition.composition.key))
        print('Composition Year: ' + str(to_string(self.edition.composition.year)))
        print('Edition: ' + to_string(self.edition.name))
        print('Editor: ', end='')
        editors = self.edition.authors
        for i in range(0, len(editors)):
            print(editors[i].name, end='')
            if i + 1 != len(editors):
                print('; ', end='')
        print()

        voices = self.edition.composition.voices
        for i in range(0, len(voices)):
            print('Voice ' + str(i+1) + ': ', end='')
            if voices[i].range is not None:
                print(voices[i].range, end='')
            if voices[i].name is not None and voices[i].range is None:
                print(voices[i].name)
            if voices[i].name is not None and voices[i].range is not None:
                print(', ' + voices[i].name)

        print('Partiture: ' + boolean_to_string(self.partiture))
        print('Incipit: ' + to_string(self.edition.composition.incipit))


class Edition:
    def __init__(self):
        self.composition = None
        self.authors = []
        self.name = None

    def __eq__(self, other):
        if self.name != other.name or self.composition != other.composition:
            return False

        if len(self.authors) != len(other.authors):
            return False

        for i in range(0, len(self.authors)):
            if self.authors[i].name != other.authors[i].name:
                return False

        return True



class Composition:
    def __init__(self):
        self.name = None
        self.incipit = None
        self.key = None
        self.genre = None
        self.year = None
        self.voices = []
        self.authors = []


    def __eq__(self, other):
        if self.name != other.name or self.incipit != other.incipit or self.key != other.key\
                or self.genre != other.genre or self.year != other.year:
            return False

        if len(self.voices) != len(other.voices):
            return False

        if len(self.authors) != len(other.authors):
            return False

        for i in range(0, len(self.voices)):
            if self.voices[i].number != other.voices[i].number or self.voices[i].name != other.voices[i].name or self.voices[i].range != other.voices[i].range:
                return False

        for i in range(0, len(self.authors)):
            if self.authors[i].name != other.authors[i].name:
                return False

        return True


class Voice:
    def __init__(self):
        self.number = None
        self.name = None
        self.range = None


class Person:
    def __init__(self):
        self.name = None
        self.born = None
        self.died = None


# If value is None empty string is returned, otherwise value is returned
def to_string(value):
    if value is None:
        return ''
    else:
        return value


# If True then 'yes', if False then 'no', otherwise empty string
def boolean_to_string(value):
    if value:
        return 'yes'
    elif not value:
        return 'no'
    else:
        return ''


def load(file_path):
    print_id_regex = re.compile(r"Print Number: (.*)")
    partiture_regex = re.compile(r"Partiture: (no|yes).*")
    composer_regex = re.compile(r"Composer: (.*)")
    title_regex = re.compile(r"Title: (.*)")
    genre_regex = re.compile(r"Genre: (.*)")
    key_regex = re.compile(r"Key: (.*)")
    composition_year_regex = re.compile(r"Composition Year: (\d{4})")
    edition_regex = re.compile(r"Edition: (.*)")
    editor_regex = re.compile(r"Editor: (.*)")
    voice_regex = re.compile(r"Voice (\d*): (.*)")
    incipit_regex = re.compile(r"Incipit: (.*)")

    file = open(file_path, 'r', encoding='utf8')
    file = file.read()

    prints_list = list()

    for line in file.split("\n\n"):
        if line == '':
            break
        print_id_match = print_id_regex.search(line)
        partiture_match = partiture_regex.search(line)
        composers_match = composer_regex.search(line)
        title_match = title_regex.search(line)
        genre_match = genre_regex.search(line)
        key_match = key_regex.search(line)
        composition_year_match = composition_year_regex.search(line)
        edition_match = edition_regex.search(line)
        editors_match = editor_regex.search(line)
        voices_match = voice_regex.findall(line)
        incipit_match = incipit_regex.search(line)

        ''' Parsing composers '''
        if composers_match is not None:
            composers = []
            for composer in composers_match.group(1).split(';'):
                composer_name = re.sub(r"\(.*\)", '', composer)
                composer_name = re.sub(r"\s*$", '', composer_name)
                composer_name = re.sub(r"^\s*", '', composer_name)
                born_die_regex = re.compile(r"\((\d{4})-*(\d{4})\)")
                born_die = born_die_regex.search(composer)
                born = None
                died = None
                if born_die is not None:
                    born = int(born_die.group(1))
                    if len(born_die.groups()) == 2:
                        if born_die.group(2) != '':
                            died = int(born_die.group(2))

                if born_die is None:
                    # If there is incorrect format of birth but valid format of died
                    incorrect_birth = re.compile(r"\(.*-*(\d{4})\)").search(composer)
                    if incorrect_birth is not None:
                        died = int(incorrect_birth.group(1))

                    # If there is incorrect format of died but valid format of born
                    incorrect_dead = re.compile(r"\((\d{4})[-*].*\)").search(composer)
                    if incorrect_dead is not None:
                        born = int(incorrect_dead.group(1))

                    born_advanced = re.compile(r"\*(\d{4})").search(composer)
                    died_advanced = re.compile(r"\+(\d{4})").search(composer)

                    if born_advanced is not None:
                        born = int(born_advanced.group(1))
                    if died_advanced is not None:
                        died = int(died_advanced.group(1))

                if composer_name != '':
                    tmp_composer = Person()
                    tmp_composer.name = composer_name
                    tmp_composer.born = born
                    tmp_composer.died = died

                    composers.append(tmp_composer)

        ''' Parsing voices '''
        if voices_match is not None:
            voices = []

            for i in voices_match:
                tmp_voice = Voice()
                tmp_voice.number = int(i[0])
                range_in_voice_regex = re.compile(r"(\(.*\).+--.+|.+--.+\(.*\)|\w+--\w+)[,|;]\s*(.*)")
                range_voice = range_in_voice_regex.match(i[1])

                if range_voice is not None:
                    tmp_voice.name = range_voice.group(2).strip()
                    tmp_voice.range = range_voice.group(1).strip()

                else:
                    tmp_voice.name = i[1].strip()

                # Fix: empty strings should not be in database
                if tmp_voice.name == '':
                    tmp_voice.name = None

                if tmp_voice.range == '':
                    tmp_voice.range = None

                voices.append(tmp_voice)

        ''' Parsing composition'''
        tmp_composition = Composition()
        if title_match is not None:
            tmp_composition.name = title_match.group(1).strip()

        if key_match is not None:
            tmp_composition.key = key_match.group(1).strip()

        if genre_match is not None:
            tmp_composition.genre = genre_match.group(1).strip()

        if composition_year_match is not None:
            tmp_composition.year = int(composition_year_match.group(1))

        if incipit_match is not None:
            tmp_composition.incipit = incipit_match.group(1).strip()

        # Fix: empty strings should not be in database
        if tmp_composition.name == '':
            tmp_composition.name = None

        if tmp_composition.key == '':
            tmp_composition.key = None

        if tmp_composition.genre == '':
            tmp_composition.genre = None

        if tmp_composition.incipit == '':
            tmp_composition.incipit = None


        tmp_composition.authors = composers
        tmp_composition.voices = voices

        ''' Parsing edition '''
        tmp_edition = Edition()
        if edition_match is not None:
            tmp_edition.name = edition_match.group(1).strip()

        if tmp_edition.name == '':
            tmp_edition.name = None

        tmp_edition.composition = tmp_composition

        ''' Parsing editors '''
        editors = []
        if editors_match is not None:
            editors_splitted_semicolon = str(editors_match.group(1)).split(";")
            editors_splitted_comma = str(editors_match.group(1)).split(",")

            # Editors contains only one editor instance consists of one word
            if ';' not in editors_match.group(1) and ',' not in editors_match.group(1):
                if editors_match.group(1).strip() != '':
                    tmp_editor = Person()
                    tmp_editor.name = editors_match.group(1).strip()
                    tmp_editor.name = re.sub(r"\(.*\)", '', tmp_editor.name)
                    tmp_editor.name = tmp_editor.name.strip()
                    editors.append(tmp_editor)

            else:
                # Editors contains editors separated by semicolon
                if ';' in editors_match.group(1):
                    for i in range(0, len(editors_splitted_semicolon)):
                        if editors_match.group(1).strip() != '':
                            tmp_editor = Person()
                            tmp_editor.name = editors_splitted_semicolon[i]
                            tmp_editor.name = tmp_editor.name.strip()
                            editors.append(tmp_editor)
                # Editors contains editors separated by comma, and there is firstname and surname separated by coma too
                else:
                    for i in range(0, len(editors_splitted_comma), 2):
                        if editors_splitted_comma[i] + "," + editors_splitted_comma[i+1] != '':
                            tmp_editor = Person()
                            tmp_editor.name = editors_splitted_comma[i] + "," + editors_splitted_comma[i+1]
                            tmp_editor.name = tmp_editor.name.strip()
                            editors.append(tmp_editor)

        tmp_edition.authors = editors

        ''' Parsing print '''
        tmp_print = Print()
        if print_id_match is not None:
            tmp_print.print_id = int(print_id_match.group(1))

        if partiture_match is not None:
            if partiture_match.group(1) == "no":
                tmp_print.partiture = False
            if partiture_match.group(1) == "yes":
                tmp_print.partiture = True

        tmp_print.edition = tmp_edition

        if tmp_print is not None:
            prints_list.append(tmp_print)

        prints_list.sort(key=lambda x: int(x.print_id), reverse=False)
    return prints_list
