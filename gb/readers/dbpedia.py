#   Copyright (c) 2016 CNRS - Centre national de la recherche scientifique.
#   All rights reserved.
#
#   Written by Telmo Menezes <telmo@telmomenezes.com>
#
#   This file is part of GraphBrain.
#
#   GraphBrain is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   GraphBrain is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with GraphBrain.  If not, see <http://www.gnu.org/licenses/>.


import bz2
import re
import gb.constants as const
import gb.hypergraph.symbol as sym
import gb.hypergraph.edge as ed


def convert_camel_case(name):
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)


def process_ontology(name):
    return convert_camel_case(name), 'dbp.o'


class DBPediaReader(object):
    def __init__(self, hg):
        self.hg = hg
        self.edges_found = 0
        self.p_parents = re.compile('(.+)_\((.+)\)')
        self.p_end_number = re.compile('(.+)__([0-9]+)')

    def process_resource(self, name):
        m = self.p_end_number.match(name)
        if m:
            return None, None
        ns_extra = ''
        m = self.p_parents.match(name)
        if m:
            name = str(m.group(1))
            ns_extra = str(m.group(2))
        if ',_' in name:
            tokens = name.split(',_')
            name = tokens[0]
            if ns_extra == '':
                ns_extra = ',_'.join(tokens[1:])
            else:
                ns_extra = '%s_%s' % (ns_extra, ',_'.join(tokens[1:]))
        if ns_extra == '':
            namespace = 'dbp.r'
        else:
            namespace = 'dbp.r.%s' % ns_extra.lower()
        return name, namespace

    def process_entity(self, entity):
        if entity == '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>':
            return const.is_type_of
        elif entity == '<http://www.w3.org/2000/01/rdf-schema#seeAlso>':
            return const.are_related
        elif entity == '<http://www.w3.org/2002/07/owl#Thing>':
            return None
        if '#' in entity:
            parts = entity.split('#')
        else:
            parts = entity.split('/')
        namespace = parts[-2]
        name = parts[-1]
        if len(namespace) == 0:
            return None
        if namespace[0] == '<':
            namespace = namespace[1:]
        if name[-1] == '>':
            name = name[:-1]
        if namespace == 'ontology':
            name, namespace = process_ontology(name)
        elif namespace == 'resource':
            name, namespace = self.process_resource(name)
        if name is None:
            return None
        name = name.lower()
        return sym.build((name, namespace))

    def process_line(self, line):
        line_str = line.decode()
        if line_str[0] == '#':
            return
        parts = line_str.split(' ')
        edge = (self.process_entity(parts[1]), self.process_entity(parts[0]), self.process_entity(parts[2]))
        if None in edge:
            return

        self.hg.add_belief(const.dbpedia, edge)
        print(ed.edge2str(edge))

    def create_edges(self, filename):
        source_file = bz2.BZ2File(filename, 'r')
        count = 0
        for line in source_file:
            self.process_line(line)
            count += 1
            if (count % 10000) == 0:
                print('%s [%s]' % (count, self.edges_found))
        source_file.close()
        print('%s edges found' % self.edges_found)


def read(hg, filename):
    DBPediaReader(hg).create_edges(filename)
