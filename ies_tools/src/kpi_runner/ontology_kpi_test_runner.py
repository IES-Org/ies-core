import rdflib
import pyshacl
from dataclasses import dataclass
import datetime
import glob
import os
import argparse

@dataclass
class kpi_result:
    name: str
    tested: int
    failed:int
    passed:int

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Run all shacl validations in a give directory")
    
    # Add arguments for the two file names
    parser.add_argument("--kpi_directory", type=str, help="Path to kpi directory")
    parser.add_argument("--new_ontology", type=str, help="Path to the new ontology")
    parser.add_argument("--results", type=str, help="Path to the results directory")
    
    # Parse the arguments
    args = parser.parse_args()

    ontology = rdflib.Graph()
    ontology.parse(args.new_ontology)

    print("SHACL start")
    aggregator = []
    for filenm in glob.glob(f"{args.kpi_directory}/*.ttl"):
        print(filenm)
        shacl = rdflib.Graph()
        shacl.parse(filenm, format="turtle")
        result, result_graph, result_report = pyshacl.validate(data_graph=ontology, shacl_graph=shacl)
        result_filenm = os.path.basename(filenm).replace(".ttl", ".txt")
        with open(f"{args.results}/{datetime.date.today().strftime('%Y-%m-%d')}_{result_filenm}", "w") as f:
            f.write(result_report)
        result_graph.serialize(f"{args.results}/{datetime.date.today().strftime('%Y-%m-%d')}_{result_filenm.replace('.txt', '')}_result.ttl")
        print(result)
        print("====")
        # Extract all focus nodes tested
        focus_nodes = set(ontology.subjects())  # Modify based on your dataset and focus node definition

        # Extract failing focus nodes from the result graph
        failing_nodes = set(result_graph.objects(predicate=rdflib.URIRef("http://www.w3.org/ns/shacl#focusNode")))
        # Derive passing focus nodes
        passing_nodes = focus_nodes - failing_nodes

        print(f"Total Focus Nodes Tested: {len(focus_nodes)}")
        print(f"Failing Focus Nodes: {len(failing_nodes)}")
        print(f"Passing Focus Nodes: {len(passing_nodes)}")
        aggregator.append(kpi_result(filenm, len(focus_nodes), len(failing_nodes), len(passing_nodes)))
    print("SHACL end")
    print("SUMMARY")
    for a in aggregator:
        print(a)

if __name__ == "__main__":
    main()