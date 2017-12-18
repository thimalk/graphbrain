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


import progressbar
import gb.constants as cons
import gb.hypergraph.symbol as sym
import gb.nlp.parser as par
from gb.synonyms.meronomy import Meronomy


def generate(hg):
    print('starting parser...')
    parser = par.Parser()

    mer = Meronomy(parser)

    print('reading edges...')
    total_edges = 0
    total_beliefs = 0

    total_verts = hg.symbol_count() + hg.edge_count()
    i = 0
    with progressbar.ProgressBar(max_value=total_verts) as bar:
        for vertex in hg.all():
            if sym.is_edge(vertex):
                edge = vertex
                total_edges += 1
                if hg.is_belief(edge):
                    mer.add_edge(edge)
                    total_beliefs += 1
            i += 1
            if (i % 1000) == 0:
                bar.update(i)

    print('edges: %s; beliefs: %s' % (total_edges, total_beliefs))

    print('recovering words...')
    i = 0
    with progressbar.ProgressBar(max_value=total_verts) as bar:
        for vertex in hg.all():
            if sym.is_edge(vertex):
                edge = vertex
                if hg.is_belief(edge):
                    mer.recover_words(edge)
            i += 1
            if (i % 1000) == 0:
                bar.update(i)

    print('generating meronomy graph...')
    mer.generate()

    print('normalizing meronomy graph...')
    mer.normalize_graph()

    print('generating synonyms...')
    mer.generate_synonyms()

    print('writing synonyms...')
    i = 0
    with progressbar.ProgressBar(max_value=len(mer.synonym_sets)) as bar:
        for syn_id in mer.synonym_sets:
            edges = set()
            for atom in mer.synonym_sets[syn_id]:
                if atom in mer.edge_map:
                    edges |= mer.edge_map[atom]
            best_count = -1
            best_label_edge = None
            for edge in edges:
                if mer.edge_counts[edge] > best_count:
                    best_count = mer.edge_counts[edge]
                    best_label_edge = edge
            label = hg.get_label(best_label_edge)
            syn_symbol = sym.build(label, 'syn%s' % syn_id)
            for edge in edges:
                syn_edge = (cons.are_synonyms, edge, syn_symbol)
                hg.add(syn_edge)
            label_symbol = sym.build(label, cons.label_namespace)
            label_edge = (cons.has_label, syn_symbol, label_symbol)
            hg.add(label_edge)
            i += 1
            if i % 1000 == 0:
                bar.update(i)
        bar.update(i)

    print('%s synonym sets created' % len(mer.synonym_sets))
    print('done.')


def main_synonym(hg, edge):
    edges = hg.pattern2edges([cons.are_synonyms, edge, None])
    if len(edges) > 0:
        return edges.pop()[2]
    return edge
