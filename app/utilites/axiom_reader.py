# -*- coding: utf-8 -*-
from rdflib import Graph, Namespace, RDF, RDFS, OWL, BNode

def getClassAxioms(ontoclass, G, prefix):
    """
    :param ontoclass: в формате объекта RDF URI Reference <class 'rdflib.term.URIRef'>
    :param G: в виде объекта rdfLib <class 'rdflib.graph.Graph'>
    :param prefix:  в формате строки, например http://portal.domen#
    """

    ONTO = Namespace(prefix)

    def qName(urn):
        pref = ""
        position = str(urn).find("#")
        result = ""
        if position > 0:
            if urn[:position + 1] == str(OWL):
                pref = "owl:"
            elif urn[:position + 1] == str(RDF):
                pref = "rdf:"
            elif urn[:position + 1] == str(RDFS):
                pref = "rdfs:"
            elif urn[:position + 1] == ONTO:
                pref = "onto:"
            else:
                pref = "?:" + urn[:position + 1]
            result = pref + urn[position + 1:]
        else:
            result = urn
        return (result)

    def drillelements(node):
        first = ""
        rest = ""
        other = []
        for p, o in G.predicate_objects(node):
            if p == RDF.first:
                if type(o) == BNode:
                    first = '(' + drillelements(o) + ')'
                else:
                    first = qName(o)
            elif p == RDF.rest:
                if type(o) == BNode:
                    rest = '(' + drillelements(o) + ')'
                else:
                    rest = qName(o)
            else:
                other.append(qName(p) + ' - ' + qName(o) + '\n')

        if first == 'rdf:nil':
            first = ''

        if rest == 'rdf:nil':
            rest = ''

        mstr = '\n' + first + ' ' + rest + ' '.join(other)
        return mstr

    # Работаем с аксиомами эквивалентных классов
    axioms = []
    axiom = ''
    for o in G.objects(ontoclass, OWL.equivalentClass):
        if type(o) == BNode:
            axiom = axiom + 'OWL:equivalentClass:\n'
            for o2 in G.objects (o, OWL.intersectionOf):
                if type(o2) == BNode:
                    axiom = axiom + 'OWL:intersectionOf:' + drillelements(o2)
                else:
                    axiom = axiom + qName(o2)
                axiom = axiom + '\n'
            axioms.append(axiom)
            axiom = ''

    # Работаем с аксиомами подклассов
    for o in G.objects(ontoclass, RDFS.subClassOf):
        if type(o) == BNode:
            axiom = axiom + 'rdfs:subClassOf:\n'
            for p3, o3 in G.predicate_objects(o):
                if type(o3) == BNode:
                    axiom = axiom + 'OWL:subClassOf:' + drillelements(o3)
                else:
                    axiom = axiom + qName(p3) + ' - ' + qName(o3) + '\n'
            axiom = axiom + '\n'
            axioms.append(axiom)
            axiom = ''

    # print('\n '.join(axioms))
    return axioms