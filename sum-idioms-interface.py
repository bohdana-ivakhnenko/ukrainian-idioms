import os
import csv
import re
from tabulate import tabulate
import collections
from alphabet_detector import AlphabetDetector
alphabet = AlphabetDetector()


class IdiomThesaurus:
    _en_uk = {
        'abstract relations': 'абстрактні відношення',
        'existence': 'існування',
        'relation': 'відношення',
        'quantity': 'кількість',
        'order': 'порядок',
        'number': 'число',
        'time': 'час',
        'change': 'зміна',
        'causation': 'причинновість',
        'affections': 'емоції',
        'affections in general': 'загалом',
        'personal': 'особисті',
        'sympathetic': 'співчуття',
        'moral': 'моральні',
        'religious': 'релігійні',
        'intellect': 'інтелект',
        'formation of ideas': 'формування ідей',
        'communication of ideas': 'обмін ідеями',
        'matter': 'матерія',
        'generally': 'загалом',
        'inorganic': 'неорганічна',
        'organic': 'органічна',
        'space': 'простір',
        'dimensions': 'виміри',
        'form': 'форма',
        'motion': 'рух',
        'volition': 'вольовий акт',
        'individual': 'індивідуальний',
        'intersocial': 'соціальний'
    }
    _uk_en = {value: key for key, value in _en_uk.items()}

    _classes_sections = {
        'abstract relations': ('existence', 'relation', 'quantity', 'order',
                               'number', 'time', 'change', 'causation'),
        'affections': ('affections in general', 'personal',
                       'sympathetic', 'moral', 'religious'),
        'intellect': ('formation of ideas', 'communication of ideas'),
        'matter': ('generally', 'inorganic', 'organic'),
        'space': ('generally', 'dimensions', 'form', 'motion'),
        'volition': ('individual', 'intersocial')
    }

    def __init__(self, file='sum-idioms-annotated.tsv'):
        self.file = file
        self.database = []
        self.columns = {}
        self.initialize()

        self.class_ = ''
        self.section_ = ''
        self.save = False
        self.search_tag = ''
        self.get_query()

        self.idioms = []
        self.get_idioms()

        self.idiom_groups = collections.defaultdict(list)
        self.group_idioms()

        self.provide_results()

        if self.next_round():
            self.__init__(file=self.file)

    @staticmethod
    def next_round():
        print('Виконати ще один пошук? (так/ні)')
        answer = input().strip().lower()
        answers = {True: ('так', 'yes', '1'),
                   False: ('ні', 'no', '0')}
        if answer in answers[True]:
            return True

    def initialize(self):
        with open(self.file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            self.database = [line for line in reader]
            self.columns = {column: index for index, column in enumerate(self.database.pop(0))}

    @staticmethod
    def answer_not_appropriate(answer, categories):
        all_options = ['шукати в усіх класах', 'в усіх класах', 'усі', 'всі',
                       'шукати в усіх секціях', 'в усіх секціях', 'усюди',
                       'шукати в усіх', 'шукати всюди', 'в усіх', 'всюди']

        words = answer.isalpha() and not (answer.isdigit() or
                                          (answer.lower() in list(IdiomThesaurus._uk_en.keys()) +
                                                             list(IdiomThesaurus._en_uk.keys())
                                           and IdiomThesaurus._uk_en[answer].lower() in categories) or
                                          answer in categories or
                                          answer.lower() in all_options)
        number = (answer.startswith('-') or (answer.isdigit() and
                                             not int(answer) <= len(categories)+1))
        unknown = not (answer.isalpha() or answer.isdigit())
        return words or number or unknown

    def get_query(self):
        if not self.class_:
            classes = self._classes_sections.keys()
            print('Виберіть номер класу або напишіть сам клас:')
            [print(f'{index + 1}. {IdiomThesaurus._en_uk[class_]}') for index, class_ in enumerate(classes)]
            print(f'{len(classes) + 1}. шукати в усіх класах')
            answer_class = input().strip()
            if self.answer_not_appropriate(answer_class, classes):
                print('\nВи ввели неправильне числове значення або вказали неіснуючий клас.')
                print('Спробуйте ще раз!', end='\n\n')
                self.get_query()
            else:
                if answer_class.isdigit():
                    self.class_ = list(classes)[int(answer_class) - 1]
                elif alphabet.only_alphabet_chars(answer_class, "CYRILLIC") \
                        and answer_class in IdiomThesaurus._uk_en.keys():
                    self.class_ = IdiomThesaurus._uk_en[answer_class]
                elif alphabet.only_alphabet_chars(answer_class, "LATIN") \
                        and answer_class in IdiomThesaurus._en_uk.keys():
                    self.class_ = answer_class
                else:
                    self.class_ = "усі"
                    self.section_ = "усі"

        if self.class_ and not self.section_:
            sections = IdiomThesaurus._classes_sections[self.class_]
            print('Можете також обрати секцію:')
            [print(f'{index + 1}. {IdiomThesaurus._en_uk[section_]}') for index, section_ in enumerate(sections)]
            print(f'{len(sections) + 1}. шукати в усіх секціях')
            answer_section = input().strip()
            if self.answer_not_appropriate(answer_section, sections):
                print('\nВи ввели неправильне числове значення або вказали неіснуючу секцію.')
                print('Спробуйте ще раз!', end='\n\n')
                self.get_query()
            else:
                if answer_section.isdigit():
                    self.section_ = list(sections)[int(answer_section) - 1]
                elif alphabet.only_alphabet_chars(answer_section, "CYRILLIC") \
                        and answer_section in IdiomThesaurus._uk_en.keys():
                    self.section_ = IdiomThesaurus._uk_en[answer_section]
                elif alphabet.only_alphabet_chars(answer_section, "LATIN") \
                        and answer_section in IdiomThesaurus._en_uk.keys():
                    self.section_ = answer_section
                else:
                    self.section_ = "усі"

        print("Напишіть тег для пошуку, якщо хочете зберегти результат у файл:")
        answer_tag = input().strip()
        self.search_tag = answer_tag

        if not (self.class_ and self.section_):
            print('Упссс, щось пішло не так, спробуйте ще раз!')
            self.get_query()
        return

    def get_idioms(self):
        full_path_id = self.columns['head group>head']
        idiom_id = self.columns['idiom']
        definition_id = self.columns['definition']
        type_id = self.columns['semantic-type']
        citation_id = self.columns['citation']
        source_id = self.columns['source']

        class_id = self.columns['class']
        section_id = self.columns['section']
        subsection_id = self.columns['subsection']

        if self.class_ == 'усі':
            self.idioms = [(line[full_path_id],
                            line[idiom_id], line[definition_id],
                            line[type_id], line[citation_id], line[source_id],
                            line[class_id], line[section_id], line[subsection_id])
                           for line in self.database]
        elif self.section_ == 'усі':
            self.idioms = [(line[full_path_id],
                            line[idiom_id], line[definition_id],
                            line[type_id], line[citation_id], line[source_id],
                            line[class_id], line[section_id], line[subsection_id])
                           for line in self.database
                           if line[self.columns['class']] == self.class_]
        else:
            self.idioms = [(line[full_path_id],
                            line[idiom_id], line[definition_id],
                            line[type_id], line[citation_id], line[source_id],
                            line[class_id], line[section_id], line[subsection_id])
                           for line in self.database
                           if line[self.columns['class']] == self.class_ and
                           line[self.columns['section']] == self.section_]

    def group_idioms(self):
        self.idiom_groups = collections.defaultdict(list)
        for idiom_line in self.idioms:
            class_ = idiom_line[-3]
            self.idiom_groups[class_].append(idiom_line)

        for class_, idiom_lines in self.idiom_groups.items():
            sections = collections.defaultdict(list)
            for idiom_line in idiom_lines:
                section_ = idiom_line[-2]
                sections[section_].append(idiom_line)
            self.idiom_groups[class_] = sections

        for class_, sections in self.idiom_groups.items():
            for section_, idiom_lines in sections.items():
                subsections = collections.defaultdict(list)
                for idiom_line in idiom_lines:
                    subsection_ = idiom_line[-1]
                    subsections[subsection_].append(idiom_line)
                self.idiom_groups[class_][section_] = subsections

    def get_doubling_files(self):
        paths = os.listdir("queries/")
        file_name_pattern = re.compile(r'(?<=idioms_'+self.search_tag+'_)[0-9]+(?=.tsv)')
        doubling_files = file_name_pattern.findall('\n'.join(paths))
        return [int(file) for file in doubling_files]

    def get_file_name(self):
        doubling_files = self.get_doubling_files()
        if doubling_files:
            return f"idioms_{self.search_tag}_{max(doubling_files)+1}"
        return f"idioms_{self.search_tag}_{1}"

    def provide_results(self):
        if self.search_tag:
            headers = ('id', 'class', 'section', 'subsection', 'head group>head',
                       'idiom', 'definition', 'semantic type',
                       'citation', 'source')
            file = open(f"queries/{self.get_file_name()}.tsv", "w")
            writer = csv.writer(file, delimiter='\t', lineterminator='\n')

            writer.writerow(headers)

        for class_, sections in self.idiom_groups.items():
            for section_, subsections in sections.items():
                for subsection_, idioms in subsections.items():
                    if subsection_:
                        headers = ('id', 'head group>head',
                                   'idiom', 'definition', 'semantic type',
                                   'citation', 'source')
                        print(f"{class_} > {section_} > {subsection_}".upper())
                    else:
                        headers = ('id', 'head',
                                   'idiom', 'definition', 'semantic type',
                                   'citation', 'source')
                        print(f"{class_} > {section_}".upper())

                    lines_to_show = [[index+1] + list(idiom[:6]) for index, idiom in enumerate(idioms)]
                    print(tabulate(lines_to_show, headers=headers, tablefmt="fancy_grid", stralign="left",
                                   maxcolwidths=[None, None, 30, 40, 20, 50, 34]))
                    print()

                    if self.search_tag:
                        lines_to_write = [[index + 1, class_, section_, subsection_] + list(idiom[:6])
                                          for index, idiom in enumerate(idioms)]
                        for line in lines_to_write:
                            writer.writerow(line)
        if self.search_tag:
            file.close()


if __name__ == '__main__':
    IdiomThesaurus()
