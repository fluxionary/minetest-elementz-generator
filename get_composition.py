import csv
import math
import functools
import itertools
import regex

parser_re = regex.compile('(?:([a-zA-Z]+)([0-9]+))+')

weight_by_symbol = {}

with open('elements.csv') as fh:
    dialect = csv.Sniffer().sniff(fh.read(2048))
    fh.seek(0)
    csv_reader = csv.reader(fh)
    next(csv_reader)  # skip header

    for row in csv_reader:
        weight_by_symbol[row[2]] = float(row[3])


def round_parts_to(parts, total: int):
    """
    give a table of floating point values, and a desired integer total,
    produce a scaled table roughly proportional to the original,
    where the sum of the components equals the total, and all components
    are integers, in an approximately-fair fashion.

    see https://en.wikipedia.org/wiki/Largest_remainder_method
    """
    s = sum(parts)
    # normalize, sort, and track indices
    ifparts = sorted(
        zip(map(list, map(math.modf,
                (part * total / s for part in parts))),
            itertools.count()),
        key=lambda ifpart: ifpart[0][0],
        reverse=True
    )
    # convert int parts to actual ints
    for index in range(len(ifparts)):
        ifparts[index][0][1] = int(ifparts[index][0][1])

    # increase values of bins w/ largest fractional parts as necessary
    isum = sum(ifpart[0][1] for ifpart in ifparts)
    for index in range(total - isum):
        ifparts[index][0][1] += 1

    # put back in the original order
    ifparts.sort(key=lambda ifpart: ifpart[1])
    return tuple(ifpart[0][1] for ifpart in ifparts)


class Compound:
    @staticmethod
    def parse(components):
        m = parser_re.fullmatch(components)
        if not m:
            raise Exception(f'{components!r}')
        return dict(zip(m.captures(1), map(int, m.captures(2))))

    def __init__(self, components):
        if isinstance(components, str):
            components = Compound.parse(components)

        self.components = components

    def weight(self):
        return sum(
            weight_by_symbol[element] * quantity
            for element, quantity
            in self.components.items()
        )

    def count(self):
        return sum(self.components.values())

    def __mul__(self, scalar):
        return Compound({
            element: quantity * scalar
            for element, quantity in self.components.items()
        })

    def __truediv__(self, scalar):
        return self * (1/scalar)

    def __add__(self, other):
        components = dict(self.components)
        for element, quantity in other.components.items():
            components[element] = components.get(element, 0) + quantity
        return Compound(components)

    def __repr__(self):
        return repr(self.components)

    def __str__(self):
        rounded = round_parts_to(self.components.values(), round(sum(self.components.values())))
        items = sorted(zip(self.components.keys(), rounded),
                       key=lambda item: (-item[1], item[0]))
        return ' '.join(
            f'{element}{quantity}'
            for element, quantity
            in items
            if quantity != 0
        )

    def __hash__(self):
        return hash(tuple(sorted(self.components.items())))


basalt = {
    Compound({'Si': 1, 'O': 2}): 49.97,
    Compound({'Ti': 1, 'O': 2}): 1.87,
    Compound({'Al': 2, 'O': 3}): 15.99,
    Compound({'Fe': 2, 'O': 3}): 3.85,
    Compound({'Fe': 1, 'O': 1}): 7.24,
    Compound({'Mn': 1, 'O': 1}): 0.20,
    Compound({'Mg': 1, 'O': 1}): 6.84,
    Compound({'Ca': 1, 'O': 1}): 9.62,
    Compound({'Na': 2, 'O': 1}): 2.96,
    Compound({'K': 2, 'O': 1}): 1.12,
    Compound({'P': 2, 'O': 5}): 0.35,
}

dirt = {
    Compound({'Si': 1, 'O': 2}): 64.893,
    Compound({'Ti': 1, 'O': 2}): 0.876,
    Compound({'Al': 2, 'O': 3}): 16.311,
    Compound({'Fe': 2, 'O': 3}): 3.246,
    Compound({'Fe': 1, 'O': 1}): 1.123,
    Compound({'Mn': 1, 'O': 1}): 0.071,
    Compound({'Mg': 1, 'O': 1}): 1.028,
    Compound({'Ca': 1, 'O': 1}): 0.934,
    Compound({'Na': 2, 'O': 1}): 2.1378,
    Compound({'K': 2, 'O': 1}): 2.99,
    Compound({'P': 2, 'O': 5}): .1031,
    Compound({'H': 1, 'C': 1, 'O': 1}): 6.3,
}

schist_mica = {
    Compound({'Si': 1, 'O': 2}): 63.14,
    Compound({'Ti': 1, 'O': 2}): 0.79,
    Compound({'Al': 2, 'O': 3}): 14.86,
    Compound({'Fe': 2, 'O': 3}): 1.83,
    Compound({'Fe': 1, 'O': 1}): 5.3,
    Compound({'Mn': 1, 'O': 1}): 0.06,
    Compound({'Mg': 1, 'O': 1}): 3.04,
    Compound({'Ca': 1, 'O': 1}): 1.75,
    Compound({'Na': 2, 'O': 1}): 3.09,
    Compound({'K': 2, 'O': 1}): 3.04,
    Compound({'P': 2, 'O': 5}): 0.15,
    Compound({'H': 2, 'O': 1}): 1.95,
}

andesite = {
    Compound({'Si': 1, 'O': 2}): 58.2,
    Compound({'Al': 2, 'O': 3}): 17.0,
    Compound({'Fe': 2, 'O': 3}): 3.2,
    Compound({'Fe': 1, 'O': 1}): 3.7,
    Compound({'Mg': 1, 'O': 1}): 3.5,
    Compound({'Ca': 1, 'O': 1}): 6.3,
    Compound({'Na': 2, 'O': 1}): 3.5,
    Compound({'K': 2, 'O': 1}): 2.1,
}

amphibolite = {
    Compound({'Si': 1, 'O': 2}): 41.08,
    Compound({'Ti': 1, 'O': 2}): 2.34,
    Compound({'Al': 2, 'O': 3}): 13.12,
    Compound({'Fe': 2, 'O': 3}): 2.96,
    Compound({'Fe': 1, 'O': 1}): 12.86,
    Compound({'Mn': 1, 'O': 1}): 0.09,
    Compound({'Mg': 1, 'O': 1}): 10.76,
    Compound({'Ca': 1, 'O': 1}): 11.05,
    Compound({'Na': 2, 'O': 1}): 1.14,
    Compound({'K': 2, 'O': 1}): 2.34,
    Compound({'P': 2, 'O': 5}): 0.00,
    Compound({'H': 2, 'O': 1}): 1.95,
}

gneiss = {
    Compound({'Si': 1, 'O': 2}): 74.1,
    Compound({'Ti': 1, 'O': 2}): 0.42,
    Compound({'Al': 2, 'O': 3}): 12.4,
    Compound({'Fe': 2, 'O': 3}): 1.0,
    Compound({'Fe': 1, 'O': 1}): 1.8,
    Compound({'Mn': 1, 'O': 1}): 0.07,
    Compound({'Mg': 1, 'O': 1}): 0.51,
    Compound({'Ca': 1, 'O': 1}): 1.5,
    Compound({'Na': 2, 'O': 1}): 2.9,
    Compound({'K': 2, 'O': 1}): 4.5,
    Compound({'P': 2, 'O': 5}): 0.10,
    Compound({'H': 2, 'O': 1}): 0.60,
    Compound({'C': 1, 'O': 2}): 0.05,
}

ochre = {
    Compound({'Si': 1, 'O': 2}): 61.5,
    Compound({'Al': 2, 'O': 3}): 6.3,
    Compound({'Fe': 2, 'O': 3}): 13.2,
    Compound({'Mg': 1, 'O': 1}): 0.3,
    Compound({'Ca': 1, 'S': 1, 'O': 4}): 1.4,
    Compound({'H': 2, 'O': 1}): 16.1,
    Compound({'Ti': 1, 'O': 2}): 1.2,
}

granite = {
    Compound({'Si': 1, 'O': 2}): 71.84,
    Compound({'Ti': 1, 'O': 2}): 0.31,
    Compound({'Al': 2, 'O': 3}): 14.43,
    Compound({'Fe': 2, 'O': 3}): 1.22,
    Compound({'Fe': 1, 'O': 1}): 1.65,
    Compound({'Mn': 1, 'O': 1}): 0.05,
    Compound({'Mg': 1, 'O': 1}): 0.72,
    Compound({'Ca': 1, 'O': 1}): 1.85,
    Compound({'Na': 2, 'O': 1}): 3.71,
    Compound({'K': 2, 'O': 1}): 4.1,
    Compound({'P': 2, 'O': 5}): 0.12,
}

faizievite_formula = {
    Compound('K2Na2Ca6Ti4Li6Si24O66F2'): 1,
}

eclogite = {
    Compound({'Si': 1, 'O': 2}): 50.51,
    Compound({'Ti': 1, 'O': 2}): 1.39,
    Compound({'Al': 2, 'O': 3}): 15.70,
    Compound({'Fe': 2, 'O': 3}): 9.46,
    Compound({'Mn': 1, 'O': 1}): 0.18,
    Compound({'Mg': 1, 'O': 1}): 7.94,
    Compound({'Ca': 1, 'O': 1}): 11.58,
    Compound({'Na': 2, 'O': 1}): 2.70,
    Compound({'K': 2, 'O': 1}): 0.16,
    Compound({'P': 2, 'O': 5}): 0.16,
}

crust = {
    Compound({'O': 1}): .461,
    Compound({'Si': 1}): .282,
    Compound({'Al': 1}): .0823,
    Compound({'Fe': 1}): .0563,
    Compound({'Ca': 1}): .0415,
    Compound({'Na': 1}): .0235,
    Compound({'Mg': 1}): .0233,
    Compound({'K': 1}): .0209,
    Compound({'Ti': 1}): .00565,
    Compound({'H': 1}): .00140,
}

phyllite = {
    Compound({'Si': 1, 'O': 2}): 73.66,
    Compound({'Al': 2, 'O': 3}): 16.05,
    Compound({'Ti': 1, 'O': 2}): 0.29,
    Compound({'Fe': 2, 'O': 3}): 1.22,
    Compound({'Fe': 1, 'O': 1}): 0.07,
    Compound({'Mn': 1, 'O': 1}): 0.007,
    Compound({'Ca': 1, 'O': 1}): 0.60,
    Compound({'Mg': 1, 'O': 1}): 1.98,
    Compound({'Na': 2, 'O': 1}): 0.19,
    Compound({'K': 2, 'O': 1}): 5.34,
    Compound({'H': 2, 'O': 1}): 0.32,
    Compound({'P': 2, 'O': 5}): 0.146,
}

dunite = {
    Compound({'Si': 1, 'O': 2}): 39.53,
    Compound({'Al': 2, 'O': 3}): 0.93,
    Compound({'Fe': 2, 'O': 3}): 0.65,
    Compound({'Fe': 1, 'O': 1}): 7.62,
    Compound({'Mg': 1, 'O': 1}): 48.83,
    Compound({'H': 2, 'O': 1}): 0.89 + 0.16,
    Compound({'Ti': 1, 'O': 2}): 0.013,
    Compound({'Mn': 1, 'O': 1}): 0.12,
    Compound({'C': 1, 'O': 2}): 0.06,
    Compound({'Ni': 1, 'O': 1}): 0.32,
    Compound({'Cr': 2, 'O': 3}): 1.01,
    Compound({'Co': 1, 'O': 1}): 0.018,
}

lamproite = {
    Compound({'Si': 1, 'O': 2}): 41.2,
    Compound({'Ti': 1, 'O': 2}): 3.0,
    Compound({'Al': 2, 'O': 3}): 3.6,
    Compound({'Fe': 1, 'O': 1}): 9.2,
    Compound({'Mn': 1, 'O': 1}): 0.1,
    Compound({'Mg': 1, 'O': 1}): 23.7,
    Compound({'C': 1, 'O': 2}): 4.5,
    Compound({'Na': 2, 'O': 1}): 0.4,
    Compound({'K': 2, 'O': 1}): 3.0,
    Compound({'P': 2, 'O': 5}): 0.9,
    Compound({'B': 1}): 1.2,
}

slate = {
    Compound({'Na': 2, 'O': 1}): 1.285,
    Compound({'Mg': 1, 'O': 1}): 1.748,
    Compound({'Al': 2, 'O': 3}): 11.578,
    Compound({'Si': 1, 'O': 2}): 43.451,
    Compound({'P': 2, 'O': 5}): 0.198,
    Compound({'K': 2, 'O': 1}): 2.522,
    Compound({'Ca': 1, 'O': 1}): 33.68,
    Compound({'Fe': 2, 'O': 3}): 5.399,
    Compound({'Sr': 1, 'O': 1}): 0.138,
}

phonolite = {
    Compound({'Si': 1, 'O': 2}): 56.0,
    Compound({'Al': 2, 'O': 3}): 19.2,
    Compound({'Fe': 2, 'O': 3}): 2.9,
    Compound({'Fe': 1, 'O': 1}): 1.6,
    Compound({'Mg': 1, 'O': 1}): 0.6,
    Compound({'Ca': 1, 'O': 1}): 2.0,
    Compound({'Na': 2, 'O': 1}): 8.5,
    Compound({'K': 2, 'O': 1}): 5.3,
    Compound({'Ni': 1, 'O': 1}): 4.9,
}

mantle_1 = {
    Compound({'Mg': 1, 'Si': 1, 'O': 3}): 0.75,
    Compound({'Mg': 0.5, 'Fe': 0.5, 'O': 1}): 0.17,
    Compound({'Ca': 1, 'Si': 1, 'O': 3}): 0.08
}

kimberlite = {
    Compound({'Mg': 1, 'Fe': 1, 'Si': 1, 'O': 4}): 50,
    Compound({'C': 1, 'O': 2}): 10,
    Compound({'H': 2, 'O': 1}): 5,
    Compound({'Na': 2, 'O': 1}): 0.5,
    Compound({'K': 2, 'O': 1}): 3,
    Compound({'Al': 2, 'O': 3}): 1,
    Compound({'Mg': 0.5, 'Fe': 0.5, 'Al': 1, 'Cr': 1, 'O': 4}): 15,
    Compound({'Fe': 2, 'Ti': 1, 'O': 4}): 15,
}

peat = {
    Compound({'C': 1}): .480,
    Compound({'Ca': 1}): .02,
    Compound({'H': 1}): .05,
    Compound({'Al': 1}): .005,
    Compound({'Cl': 1}): .001,
    Compound({'Mg': 1}): .003,
    Compound({'N': 1}): .025,
    Compound({'O': 1}): .32,
    Compound({'K': 1}): .001,
    Compound({'Si': 1}): .05,
    Compound({'S': 1}): .005,
    Compound({'Mg': 1}): .003,
    Compound({'Pb': 1}): .0004,
    Compound({'Fe': 1}): .03,
}

crude_oil = {
    Compound({'C': 1}): 84,
    Compound({'H': 1}): 12,
    Compound({'N': 1}): 1,
    Compound({'O': 1}): 1,
    Compound({'S': 1}): 2,
}

phosphate_slime = {
    Compound('Ca5P2O11C1F1'): 22.5,
    Compound('Si1O2'): 32.5,
    Compound('Na1Al4Mg2Si12O36H6'): 22.5,
    Compound('Mg1Al1Si4O15H9'): 7.5,
    Compound('Al3P2O13F3H10'): 5,
}

meat = {
    Compound('O1'): 65,
    Compound('C1'): 18.5,
    Compound('H1'): 9.5,
    Compound('N1'): 3.2,
    Compound('Ca1'): 1.5,
    Compound('P1'): 1.0
}

blood_plasma = {  # 55%
    Compound('H2O1'): 92,

}

claystone = {
    Compound('Si1O2'): 67.79,
    Compound('Ti1O2'): 2.42,
    Compound('Al2O3'): 17.81,
    Compound('Fe2O3'): 1.67,
    Compound('Mn1O1'): 0.02,
    Compound('Mg1O1'): 0.13,
    Compound('Ca1O1'): 0.08,
    Compound('Na2O1'): 0.07,
    Compound('K2O1'): 1.63,
    Compound('P2O5'): 0.16,
    Compound('H2O1'): 3.9,
    Compound('C1H1O1'): 3.9,
}

turquoise_formula = {
    Compound('Cu1Al6'): 1,
    Compound('P1O4'): 4,
    Compound('O1H1'): 8,
    Compound('H2O1'): 4,
}

bad_claystone_formula = {
    Compound({'K': 1}): .5,
    Compound({'H': 3, 'O': 1}): .5,
    Compound({'Al': 6}): .5,
    Compound({'Mg': 2}): .25,
    Compound({'Fe': 2}): .25,
    Compound({'Si': 4}): .5,
    Compound({'O': 10}): 1,
    Compound({'O': 1, 'H': 1}): .5,
    Compound({'O': 1, 'H': 2}): .5,
}

limonite_formula = {
    Compound({'Fe': 1}): 1,
    Compound({'O': 1}): 5/6,
    Compound({'O': 1, 'H': 1}): 1 + (1/6),
    Compound({'Cl': 1}): 1/6,
}

jade_formula = {
    Compound({'Ca': 2}): 1,
    Compound({'Mg': 3}): 1,
    Compound({'Fe': 2}): 1,
    Compound({'Si': 8}): 1,
    Compound({'O': 22}): 1,
    Compound({'O': 1, 'H': 1}): 2,
}

malachite_formula = {
    Compound({'Cu': 2}): 1,
    Compound({'C': 1}): 1,
    Compound({'O': 3}): 1,
    Compound({'O': 1, 'H': 1}): 2,
}

bone_formula = {
    Compound({'Ca': 5}): 1,
    Compound({'P': 1, 'O': 4}): 3,
    Compound({'O': 1, 'H': 1}): 1,
}

hectorite_formula = {
    Compound({'Na': 1}): 0.3,
    Compound({'Mg': 0.5, 'Li': 0.5}): 3,
    Compound({'Si': 1}): 4,
    Compound({'O': 1}): 10,
    Compound({'O': 1, 'H': 1}): 2,
}

torbernite_formula = {
    Compound({'Cu': 1}): 1,
    Compound({'U': 1, 'O': 2}): 2,
    Compound({'P': 1, 'O': 4}): 2,
    Compound({'H': 2, 'O': 1}): 12
}

flubber_formula = {
    Compound('C1H1'): 4,
    Compound('C1H2'): 4,
    Compound('O1'): 4,
    Compound('B1'): 1,
    Compound('H2O1'): 4,
}

dumortierite_formula = {
    Compound('Al7B1O6'): 1,
    Compound('Si1O4'): 3,
}

sugilite_formula = {
    Compound('K1Na2Li3Si12O30'): 1,
    Compound({'Fe': 1, 'Mn': 0, 'Al': 0}): 2,
}

kaolinite_formula = {
    Compound('Al2Si2O5'): 1,
    Compound('O1H1'): 4,
}


def reduce(by_weight):
    return functools.reduce(Compound.__add__, (
        (compound * (percent / compound.weight()))
        for compound, percent
        in by_weight.items()
    ))


def reduce_formula(formula):
    return functools.reduce(Compound.__add__, (
        (compound * percent)
        for compound, percent
        in formula.items()
    ))


x = reduce(phosphate_slime)
# x = reduce_formula(kaolinite_formula)
print(x * (60 / x.count()))

