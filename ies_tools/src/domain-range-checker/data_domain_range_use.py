import rdflib
from dataclasses import dataclass
import argparse
from typing import List

import rdflib.term

@dataclass 
class trace_result:
    target_type: str
    expected_type: str
    target_result: bool = False
    target_result_reason: str = None

@dataclass
class detail_result:
    subj: str
    pred: str
    obj: str
    domain: str = None
    range: str = None
    domain_result: trace_result = None
    range_result: trace_result = None
    range_result:str = None
    result: bool = None
    result_reason: str = None

def good_powertype_exists(combo, item_type, domain):
    subj_type_class = combo.value(item_type, rdflib.RDF.type)
    if subj_type_class != rdflib.RDFS.Class:
        print("subj_type_class", subj_type_class)
        for stc in combo.transitive_objects(subj_type_class, rdflib.RDFS.subClassOf):
            print("stc", stc)
            powertype_subj = combo.value(predicate=IES.powertype, object=stc)
            print("powertype of subject", powertype_subj)
            if powertype_subj:
                print(stc, combo.value(predicate=IES.powertype, object=stc))
                for h in combo.transitive_objects(powertype_subj, rdflib.RDFS.subClassOf):
                    print("---->", h)
                    if h == domain:
                        print("ok via powertype")
                        return True
                else:
                    print("no useful powertype")
                    return False
        else:
            print("Still no matching super class found for", subj_type_class, "with domain", domain)
            return False
    print("no expectation - not an ontology instance for", item_type)
    return False         

def subject_traces_to_domain(combo, data, item, p, domain_or_range):
    print("In subject_traces", p, item, domain_or_range)
    for item_type in combo.objects(subject=item, predicate=rdflib.RDF.type):  # what about multiple types
        item_trace_result = trace_result(str(item_type), str(domain_or_range))
        print("item type=", item_type) 
    # obj_type = data.value(subject=o, predicate=rdflib.RDF.type)
        if domain_or_range == item_type:
            print("==", p, domain_or_range, item_type)
            item_trace_result.target_result = True
            item_trace_result.target_result_reason = "direct match"
            return item_trace_result
        else: 
            print("NM", p, domain_or_range, item_type)
            print(len(list(combo.objects(item_type, rdflib.RDFS.subClassOf))))
            for sup_class in combo.transitive_objects(item_type, rdflib.RDFS.subClassOf):
                print("super class", sup_class)
                if sup_class == domain_or_range:
                    print("ok")
                    item_trace_result.target_result = True
                    item_trace_result.target_result_reason = "via subClassOf"
                    return item_trace_result
                else:
                    print("No matching super class found for", item_type, "with domain_or_range", domain_or_range)
                    # how do i search for powertypes that could be useful?
                    # go up the same transitive object path and find the first powertype and see if that takes you across
                    pwrt = good_powertype_exists(combo, item_type, domain_or_range)
                    if pwrt:
                        print("passing", pwrt)
                        item_trace_result.target_result = True
                        item_trace_result.target_result_reason = "ok via powertype"
                        return item_trace_result
                    else:
                        print("passing", pwrt)
        item_trace_result.target_result_reason = "no subClass or powertype"
        return item_trace_result

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Validate a data ttl graph against a new ontology together with an upper (or common) ontology.")
    
    # Add arguments for the two file names
    parser.add_argument("--new_ontology", type=str, help="Path to the new ontology")
    parser.add_argument("--upper_ontology", type=str, help="Path to the upper ontology")
    parser.add_argument("--data", type=str, help="Path to the data .ttl")
    parser.add_argument("--results", type=str, help="Path to the results directory")
    
    # Parse the arguments
    args = parser.parse_args()

    new_ontology = rdflib.Graph()
    new_ontology.parse(args.new_ontology)
    top_level_ontology = rdflib.Graph()
    top_level_ontology.parse(args.upper_ontology)
    data = rdflib.Graph()
    data.parse(args.data)

    combo = (top_level_ontology+new_ontology+data)
    complete_ontology = (top_level_ontology+new_ontology)
    result_aggregate:List[detail_result] = []
    for s, p, o in data:
        result = detail_result(subj=str(s),
                               pred=str(p),
                               obj=str(o),
                               )  # initialise result object
        # get domain and range of p
        print(s, p, o)
        print()
        # test for no range in ontology warnings
        known_predicates = list(complete_ontology.predicate_objects(p))  # means the predicate is in the ontology otherwise out of bounds error
        print("testing for known predicate", p, len(known_predicates))
        if len(known_predicates) == 0:
            result.result_reason = "predicate warning"
        else:
            domain = combo.value(subject=p, predicate=rdflib.RDFS.domain)   
            if not domain:
                print("ND", p, domain, s)
            else:
                result.domain = str(domain)
                print("Domain trace", domain)
                print(subject_traces_to_domain(combo, data, s, p, domain))
                res = subject_traces_to_domain(combo, data, s, p, domain)
                result.domain_result  = res
            print("_+_+_+_+_+_+_+_++_+_+_+_++_+_+_+_+_")
            range = combo.value(subject=p, predicate=rdflib.RDFS.range)
            if not range:
                print("NR", p, range, o)
            else:
                result.range = str(range)
                print("Range trace", range)
                print(subject_traces_to_domain(combo, data, o, p, range))
                res = subject_traces_to_domain(combo, data, o, p, range)
                result.range_result = res
        
            # print(combo.value(subject=p, predicate=rdflib.RDFS.range))
            if (domain==None and range==None):
                result.result_reason = "inconclusive"
            print(f"{s}, {p}, {o}\n++++++++\n")
        result_aggregate.append(result)
    
    validation_graph = rdflib.Graph()
    validation_graph.bind("", RES)
    report = rdflib.BNode()
    validation_graph.add((report, rdflib.RDF.type, RES.DataValidationReport))
    with open("verbose_data_validation.txt", "w") as f:
        f.write("Data Validation Summary - Verbose\n")
        count_of_fails = 0
        warnings = {}
        for a in result_aggregate:
            f.write(f"{a}\n")
            if a.result_reason not in ["inconclusive", "predicate warning"]:
                if a.domain_result and not a.domain_result.target_result:
                    print(a.domain_result)
                    count_of_fails += 1
                    error_node = rdflib.BNode()
                    validation_graph.add((error_node, rdflib.RDF.type, RES.DomainError))
                    validation_graph.add((error_node, RES.subject, rdflib.URIRef(a.subj)))
                    validation_graph.add((error_node, RES.predicate, rdflib.URIRef(a.pred)))
                    validation_graph.add((error_node, RES.object, rdflib.URIRef(a.obj)))
                    validation_graph.add((error_node, RES.reason, rdflib.Literal(a.domain_result.target_result_reason)))
                    validation_graph.add((error_node, RES.actualDomain, rdflib.Literal(a.domain_result.target_type)))
                    validation_graph.add((error_node, RES.expectedDomain, rdflib.Literal(a.domain_result.expected_type)))
                if a.range_result and not a.range_result.target_result:
                    print(a.range_result)
                    count_of_fails += 1
                    error_node = rdflib.BNode()
                    validation_graph.add((error_node, rdflib.RDF.type, RES.RangeError))
                    validation_graph.add((error_node, RES.subject, rdflib.URIRef(a.subj)))
                    validation_graph.add((error_node, RES.predicate, rdflib.URIRef(a.pred)))
                    validation_graph.add((error_node, RES.object, rdflib.URIRef(a.obj)))
                    validation_graph.add((error_node, RES.reason, rdflib.Literal(a.range_result.target_result_reason)))
                    validation_graph.add((error_node, RES.actualRange, rdflib.Literal(a.range_result.target_type)))
                    validation_graph.add((error_node, RES.expectedRange, rdflib.Literal(a.range_result.expected_type)))
            # make a warning section rather
            elif a.result_reason == "predicate warning":
                    warning_at = warnings.get(a.pred, [])
                    warning_at.append(a.subj)
                    warnings[a.pred] = warning_at
                # print("-----")
                # print(a)
                # print("======")
    if count_of_fails == 0:
        validation_graph.add((report, RES.conforms, rdflib.Literal("true", datatype=rdflib.XSD.boolean)))
    else:
        validation_graph.add((report, RES.conforms, rdflib.Literal("false", datatype=rdflib.XSD.boolean)))
        validation_graph.add((report, RES.numberOfErrors, rdflib.Literal(f"{count_of_fails}", datatype=rdflib.XSD.integer)))
    if len(warnings.keys()) > 0:
        validation_graph.add((report, RES.numberOfWarnings, rdflib.Literal(f"{len(warnings.keys())}", datatype=rdflib.XSD.integer)))
    for w, at in warnings.items():
        error_node = rdflib.BNode()
        validation_graph.add((error_node, rdflib.RDF.type, RES.OutOfOntologyWarning))
        # validation_graph.add((error_node, RES.subject, rdflib.URIRef(a.subj)))
        validation_graph.add((error_node, RES.predicate, rdflib.URIRef(w)))
        # validation_graph.add((error_node, RES.object, rdflib.URIRef(a.obj)))
        validation_graph.add((error_node, RES.reason, rdflib.Literal("predicate warning")))  # are there other categories
        for a in at:
            validation_graph.add((error_node, RES.warningAf, rdflib.URIRef(a)))
    validation_graph.serialize("data_validation.ttl", format="turtle")

if __name__ == "__main__":
    IES = rdflib.Namespace("http://ies.data.gov.uk/ontology/ies4#")
    RES = rdflib.Namespace("http://ies.data.gov.uk/data_validation/")
    main()