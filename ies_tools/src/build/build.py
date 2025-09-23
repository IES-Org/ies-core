"""Build tools for generating documentation and ontology release files."""

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Set
import rdflib
from rdflib import Graph, Namespace
from rdflib.namespace import OWL
import click
import shutil

# ToDo - move this to ies-tools/src/utils.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BuildType(str, Enum):
    """Supported build types."""
    DIAGRAMS = "diagrams"
    SHACL = "shacl"
    RDF = "RDF"

class RDFType(str, Enum):
    """Supported RDF types."""
    TTL = "ttl"
    XML = "xml"
    N3 = "n3"
    JSON_LD = "json-ld"

class DiagramType(str, Enum):
    """Supported diagram types."""
    MERMAID = "mermaid"
    GRAPHVIZ = "graphviz"
    UNKNOWN = "unknown"


@dataclass
class DiagramFile:
    """Represents a diagram file with source and output information."""
    source: Path
    type: DiagramType
    name: str


@dataclass
class BuildConfig:
    """Configuration for build process."""
    source_dir: Path
    build_dir: Path
    type: BuildType


class DiagramBuilder:
    """Handles the generation of diagrams from source files."""

    EXTENSIONS = {
        '.mmd': DiagramType.MERMAID,
        '.mermaid': DiagramType.MERMAID,
        '.dot': DiagramType.GRAPHVIZ
    }
    OUTPUT_FORMATS = ['.svg', '.png']

    def __init__(self, root_dir: Path):
        """Initialize with project root directory."""
        self.root_dir = Path(root_dir).resolve()
        self.docs_diagrams = self.root_dir / 'docs' / 'diagrams'
        self.build_diagrams = self.root_dir / 'build' / 'docs' / 'diagrams'

    def verify_tools(self) -> None:
        """Verify required tools are available."""
        try:
            subprocess.run(['mmdc', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("mermaid-cli not found. Install with: npm install -g @mermaid-js/mermaid-cli")

        try:
            subprocess.run(['dot', '-V'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Graphviz not found. Install with package manager (apt/brew install graphviz)")

    def setup_build_directory(self) -> None:
        """Create build directory if it doesn't exist."""
        try:
            self.build_diagrams.mkdir(parents=True, exist_ok=True)
            logger.info(f"Build directory ensured at {self.build_diagrams}")
        except Exception as e:
            raise click.ClickException(f"Failed to create build directory: {e}")

    def find_diagram_files(self) -> List[DiagramFile]:
        """Find all diagram source files in docs/diagrams directory."""
        if not self.docs_diagrams.exists():
            logger.warning(f"Diagrams directory not found: {self.docs_diagrams}")
            return []

        diagram_files = []
        for source in self.docs_diagrams.iterdir():
            if source.suffix in self.EXTENSIONS:
                diagram_files.append(
                    DiagramFile(
                        source=source,
                        type=self.EXTENSIONS[source.suffix],
                        name=source.stem
                    )
                )

        logger.info(f"Found {len(diagram_files)} diagram source files")
        return diagram_files

    def generate_mermaid_diagram(self, source: Path, output: Path) -> bool:
        """Generate diagram from Mermaid source file."""
        try:
            subprocess.run(
                [
                    'mmdc',
                    '-i', str(source),
                    '-o', str(output),
                    '-b', 'transparent'
                ],
                capture_output=True,
                check=True
            )
            logger.info(f"Generated {output} from {source}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate Mermaid diagram: {e.stderr}")
            return False

    def generate_graphviz_diagram(self, source: Path, output: Path) -> bool:
        """Generate diagram from Graphviz source file."""
        try:
            fmt = output.suffix[1:]  # Remove the dot
            subprocess.run(
                [
                    'dot',
                    '-T', fmt,
                    '-o', str(output),
                    str(source)
                ],
                capture_output=True,
                check=True
            )
            logger.info(f"Generated {output} from {source}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate Graphviz diagram: {e.stderr}")
            return False

    def generate_all_diagrams(self) -> None:
        """Generate all diagrams in specified output formats."""
        try:
            self.verify_tools()
            self.setup_build_directory()

            source_files = self.find_diagram_files()
            if not source_files:
                logger.warning("No diagram files found to process")
                return

            success_count = 0
            total_files = len(source_files) * len(self.OUTPUT_FORMATS)

            for diagram in source_files:
                for output_ext in self.OUTPUT_FORMATS:
                    output = self.build_diagrams / f"{diagram.name}{output_ext}"

                    if diagram.type == DiagramType.MERMAID:
                        if self.generate_mermaid_diagram(diagram.source, output):
                            success_count += 1
                    elif diagram.type == DiagramType.GRAPHVIZ:
                        if self.generate_graphviz_diagram(diagram.source, output):
                            success_count += 1

            if success_count < total_files:
                logger.warning(
                    f"Generated {success_count} out of {total_files} diagram files"
                )
            else:
                logger.info(f"Successfully generated all {total_files} diagram files")

        except Exception as e:
            raise click.ClickException(f"Diagram generation failed: {e}")


def find_project_root(start_path: Path) -> Path:
    """Find project root by looking for pyproject.toml."""
    current = start_path.resolve()
    while not (current / 'pyproject.toml').exists():
        if current == current.root:
            raise click.ClickException("Could not find project root (pyproject.toml)")
        current = current.parent
    return current


class Builder:
    """Handles generation of build artifacts."""

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir).resolve()
        self.docs_dir = self.root_dir / 'docs'
        self.build_dir = self.root_dir / 'build'
        self.diagrams = DiagramBuilder(self.root_dir)

    def setup_build_directory(self, build_type: BuildType) -> Path:
        """Create and return build directory under project root."""
        build_dir = self.root_dir / 'build' / str(build_type)
        build_dir.mkdir(parents=True, exist_ok=True)
        return build_dir

    from rdflib.namespace import OWL

    def build_shacl(self, ttl_file: Path) -> None:
        """Generate SHACL shapes from TTL ontology file."""
        try:
            g = Graph()
            g.parse(source=ttl_file, format="turtle")

            shacl_g = Graph()
            sh = Namespace("http://www.w3.org/ns/shacl#")

            # Add SHACL prefix
            shacl_g.bind("sh", sh)
            for prefix, ns in g.namespaces():
                shacl_g.bind(prefix, ns)

            # Generate SHACL shapes for classes
            for cls in g.subjects(rdflib.RDF.type, rdflib.RDFS.Class):
                shape_uri = rdflib.URIRef(f"{cls}Shape")  # Name shape based on class URI
                shacl_g.add((shape_uri, rdflib.RDF.type, sh.NodeShape))  # Declare type
                shacl_g.add((shape_uri, sh.targetClass, cls))
                shacl_g.add((shape_uri, sh.severity, sh.Warning))

            # Detect properties (ObjectProperty, DatatypeProperty, or inferred)
            properties = set(g.subjects(rdflib.RDF.type, OWL.ObjectProperty))
            properties.update(g.subjects(rdflib.RDF.type, OWL.DatatypeProperty))
            properties.update(g.subjects(rdflib.RDFS.domain, None))
            properties.update(g.subjects(rdflib.RDFS.range, None))

            logger.info(f"Detected properties: {len(properties)}")

            # Generate SHACL shapes for properties
            for prop in properties:
                # Check for rdfs:domain
                domains = list(g.objects(prop, rdflib.RDFS.domain))
                if domains:
                    for domain in domains:
                        domain_shape_uri = rdflib.URIRef(f"{prop}DomainShape")
                        shacl_g.add((domain_shape_uri, rdflib.RDF.type, sh.NodeShape))
                        shacl_g.add((domain_shape_uri, sh.targetSubjectsOf, prop))
                        shacl_g.add((domain_shape_uri, sh["class"], domain))
                        shacl_g.add((domain_shape_uri, sh.severity, sh.Warning))

                # Check for rdfs:range
                ranges = list(g.objects(prop, rdflib.RDFS.range))
                if ranges:
                    for range_ in ranges:
                        range_shape_uri = rdflib.URIRef(f"{prop}RangeShape")
                        shacl_g.add((range_shape_uri, rdflib.RDF.type, sh.NodeShape))
                        shacl_g.add((range_shape_uri, sh.targetObjectsOf, prop))
                        shacl_g.add((range_shape_uri, sh["class"], range_))
                        shacl_g.add((range_shape_uri, sh.severity, sh.Warning))

            # Determine the output directory and file name
            build_dir = self.root_dir / 'build' / 'ontology'
            build_dir.mkdir(parents=True, exist_ok=True)

            output_file = build_dir / f"{ttl_file.stem}.shacl"
            shacl_g.serialize(destination=str(output_file), format="turtle")
            logger.info(f"Generated SHACL shapes at {output_file}")

        except Exception as e:
            logger.error(f"Error processing TTL file: {str(e)}")
            raise

    def build_rdf(self, ttl_file: Path | None = None, formats: Set[RDFType] | None = None) -> None:
        """Generate alternate RDF formats from TTL source."""
        FORMAT_MAP = {
            RDFType.XML: ('xml', 'rdf'),
            RDFType.N3: ('n3', 'n3'),
            RDFType.JSON_LD: ('json-ld', 'json')
        }
        formats = formats or set(FORMAT_MAP.keys())

        if ttl_file is None:
            ttl_file = self.root_dir / 'src' / 'ontology' / 'ontology.ttl'

        if not ttl_file.exists():
            raise FileNotFoundError(f"Source ontology file not found: {ttl_file}")

        build_dir = self.root_dir / 'build' / 'ontology'
        build_dir.mkdir(parents=True, exist_ok=True)

        # Copy the TTL file to build directory
        output_ttl = build_dir / ttl_file.name
        shutil.copy2(ttl_file, output_ttl)

        g = Graph()
        g.parse(ttl_file, format='turtle')

        for fmt in formats:
            rdf_format, extension = FORMAT_MAP[fmt]
            output_file = build_dir / f"{ttl_file.stem}.{extension}"
            g.serialize(destination=str(output_file), format=rdf_format)
            logger.info(f"Generated {rdf_format} format at {output_file}")

    def build(self, build_type: BuildType, **kwargs) -> None:
        """Main build method that dispatches to specific builders."""
        if build_type == BuildType.DIAGRAMS:
            self.diagrams.generate_all_diagrams()
        elif build_type == BuildType.SHACL:
            ttl_file = kwargs.get('ttl_file')
            if not ttl_file:
                raise ValueError("TTL file path required for SHACL generation")
            self.build_shacl(Path(ttl_file))
        elif build_type == BuildType.RDF:
            ttl_file = kwargs.get('ttl_file')
            formats = kwargs.get('formats')
            if not ttl_file:
                raise ValueError("TTL file path required for RDF generation")
            # Build RDF files
            self.build_rdf(ttl_file, formats)


def resolve_ttl_path(ttl_file: Path | None = None) -> tuple[Path, Path]:
    """
    Resolve TTL file path and project root directory.
    Returns tuple of (root_dir, input_path)
    """
    root_dir = find_project_root(Path.cwd())

    if ttl_file is None:
        input_path = root_dir / 'src' / 'ontology' / 'ontology.ttl'
    else:
        if ttl_file.is_absolute() or str(ttl_file).startswith('.'):
            input_path = ttl_file.resolve()
        else:
            input_path = root_dir / 'src' / 'ontology' / ttl_file

    if not input_path.exists():
        raise click.ClickException(
            f"TTL file not found at {input_path}. "
            "Please provide correct path or place file in src/ontology/"
        )

    return root_dir, input_path

@click.group()
def cli():
    """Build tools for documentation and ontology generation."""
    pass


@cli.command()
@click.option(
    '--docs-dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path('docs'),
    help="Path to the docs directory containing diagrams/ subdirectory"
)
def build_diagrams(docs_dir: Path):
    """Generate diagrams from source files in docs/diagrams/."""
    try:
        # Check for diagrams subdirectory
        diagrams_dir = docs_dir / 'diagrams'
        if not diagrams_dir.exists():
            raise click.ClickException(
                f"Diagrams directory not found at {diagrams_dir}. "
                "Ensure you have a docs/diagrams/ directory with source files."
            )

        click.echo("🎨 Starting diagram generation...")
        builder = Builder(docs_dir.parent)
        builder.build(BuildType.DIAGRAMS)
        click.echo("✨ Diagram generation completed")

    except click.ClickException as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('ttl-file', type=click.Path(dir_okay=False, path_type=Path), required=False)
def build_shacl(ttl_file: Path | None):
    """Generate SHACL shapes from TTL ontology file."""
    try:
        click.echo("🔨 Generating SHACL shapes...")
        root_dir, input_path = resolve_ttl_path(ttl_file)
        builder = Builder(root_dir)
        builder.build(BuildType.SHACL, ttl_file=input_path)
        click.echo("✨ SHACL generation completed")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('ttl-file', type=click.Path(dir_okay=False, path_type=Path), required=False)
@click.option('--formats', '-f', multiple=True,
              type=click.Choice([t.value for t in RDFType]),
              help='Output RDF formats to generate')
def build_ontology(ttl_file: Path | None, formats: List[str]):
    """Generate alternate RDF formats from TTL source."""
    try:
        click.echo("🔨 Generating RDF formats...")
        root_dir, input_path = resolve_ttl_path(ttl_file)
        builder = Builder(root_dir)
        rdf_types = {RDFType(f) for f in formats} if formats else None
        builder.build(BuildType.RDF, ttl_file=input_path, formats=rdf_types)
        click.echo("✨ RDF generation completed")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    cli()
