import collections
import csv
import pathlib

import pyexcel_ods
import regex

DATABASE_PATH = pathlib.Path('/home/flux/Developer/projects/elementz/elements.ods')
ELEMENTS_PATTERN = regex.compile(r'(?:([a-zA-Z?\*]+)([0-9]+)(?:\s+|$))+')

CALL_FORMAT = r'technic.register_material_reducer_recipe({{input={{"{input}"}}, output={output}, time={time}}})'


def load_elements():
    elements = set()
    element_names = {}

    with open('elements.csv') as fh:
        dialect = csv.Sniffer().sniff(fh.read(2048))
        fh.seek(0)
        csv_reader = csv.reader(fh)
        next(csv_reader)  # skip header

        for row in csv_reader:
            elements.add(row[2])
            element_names[row[2]] = row[1]

    elements |= {'Ab', '?', 'Ub'}
    elements -= {
        'At',
        'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og',
        'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
        'Bk', 'Fm', 'Md', 'No', 'Lr',

        # no recipes for these
        'Ir', 'Ac', 'Fr', 'Tc', 'Pa',
    }

    element_names['Ab'] = 'Abyssalium'
    element_names['?'] = 'Unknown'
    element_names['Ub'] = 'Unobtanium'

    return elements, element_names


ELEMENTS, ELEMENT_NAMES = load_elements()


def parse_recipe(s):
    m = ELEMENTS_PATTERN.fullmatch(s)
    if not m:
        raise Exception(f'unparsable: {s!r}')
    return collections.OrderedDict(zip(m.captures(1), map(int, m.captures(2))))


def generate_output(recipe_dict):
    return '{{{0}}}'.format(', '.join(
        f'"elements:{ELEMENT_NAMES[symbol].lower()} {quantity}"'
        for symbol, quantity
        in sorted(recipe_dict.items(), key=lambda x: (-x[1], x[0]))
    ))


def main():
    print('loading data from spreadsheet...')
    all_sheets = pyexcel_ods.get_data(str(DATABASE_PATH))
    print('done')
    seen = set()
    quantities = collections.defaultdict(lambda: collections.defaultdict(list))

    with open('output.lua', 'w') as output_fh:
        for row in all_sheets['sources (redo)']:
            mod, name, recipe = row[0], row[1], row[3]
            if not isinstance(recipe, str) or recipe == '*':
                print(f'SKIPPING {mod}:{name}')
                continue
            elif recipe == '-':
                recipe = row[2]

            try:
                recipe_dict = parse_recipe(recipe)

            except Exception:
                print(f'COULD NOT PARSE {mod}:{name} {recipe!r}')
                continue

            if any(element not in ELEMENTS for element in recipe_dict):
                print(f'UNKNOWN ELEMENT IN {mod}:{name} {recipe!r}')

            elif len(recipe_dict) > 6:
                print(f'TOO MANY ELEMENTS IN RECIPE: {mod}:{name} {recipe!r}')

            else:
                print(CALL_FORMAT.format(
                    input=f'{mod}:{name}',
                    output=generate_output(recipe_dict),
                    time=sum(recipe_dict.values()) / 3,
                ), file=output_fh)
                # print(f'{mod}:{name} {sum(recipe_dict.values())}')
                seen.update(recipe_dict)
                for element, quantity in recipe_dict.items():
                    quantities[element][quantity].append(f'{mod}:{name}')

        print('\n\n-- uncrafting recipes\n', file=output_fh)
        for row in all_sheets['sources (uncraft)']:
            mod, name, recipe = row[0], row[1], row[2]
            if not isinstance(recipe, str) or recipe == '*':
                print(f'SKIPPING {mod}:{name}')
                continue
            elif recipe == '-':
                recipe = row[2]

            try:
                recipe_dict = parse_recipe(recipe)

            except Exception:
                print(f'COULD NOT PARSE {mod}:{name} {recipe!r}')
                continue

            if any(element not in ELEMENTS for element in recipe_dict):
                print(f'UNKNOWN ELEMENT IN {mod}:{name} {recipe!r}')

            elif len(recipe_dict) > 6:
                print(f'TOO MANY ELEMENTS IN RECIPE: {mod}:{name} {recipe!r}')

            else:
                print(CALL_FORMAT.format(
                    input=f'{mod}:{name}',
                    output=generate_output(recipe_dict),
                    time=sum(recipe_dict.values()) / 3,
                ).replace("'", '"'), file=output_fh)

    for element, items_by_quantity in sorted(quantities.items()):
        items_by_quantity = sorted(
            (
                (quantity, item)
                for quantity, items in items_by_quantity.items()
                for item in items
                if ELEMENT_NAMES[element].lower() not in item
            ),
            key=lambda x: (-x[0], x[1])
        )
        items_by_quantity = tuple(
            f'({item}:{quantity})'
            for quantity, item in items_by_quantity
        )
        if len(items_by_quantity) > 5:
            print(element, *items_by_quantity[:5], '...')

        else:
            print(element, *items_by_quantity)

    missing = ELEMENTS - seen
    if missing:
        print(f'MISSING ELEMENTS: {missing}')


main()
