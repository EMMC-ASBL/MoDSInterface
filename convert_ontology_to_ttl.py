import os
import rdflib
from osp.core.ontology.parser import OntologyParser
from osp.core.ontology import Ontology


def export_ontology(ontology_namespace):

    ontology_graph = rdflib.graph.Graph()
    packages_path = os.path.expanduser(
        os.path.join('~', '.osp_ontologies')
    )
    package_path = os.path.join(packages_path, ontology_namespace)

    export_file_path = os.path.join(
        os.getcwd(), f"{ontology_namespace}.ttl"
    )

    if os.path.exists(f'{package_path}.yml'):
        ontology = Ontology(from_parser=OntologyParser
                            .get_parser(package_path))
        ontology_graph += ontology.graph
    else:
        raise FileNotFoundError(f'Package {ontology_namespace} not '
                                f'found in {packages_path}. Are '
                                f'you sure it is installed?')

    result = ontology_graph.serialize(format="ttl", encoding='UTF-8').decode('UTF-8')
    with open(export_file_path, 'w+') as file_handle:
        file_handle.write(result)


if __name__ == "__main__":
    
    export_ontology("mods")
