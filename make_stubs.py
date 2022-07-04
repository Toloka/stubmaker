import importlib.util
import os
import json
import sys
from argparse import ArgumentParser

from stubmaker.builder.representations_tree_builder import RepresentationsTreeBuilder
from stubmaker.builder import override_module_import_path, traverse_modules
from stubmaker.viewers.stub_viewer import StubViewer


def main():
    parser = ArgumentParser()
    parser.add_argument('--module-root', type=str, required=True, help='Module name to import these sources as')
    parser.add_argument('--src-root', type=os.path.abspath, required=True, help='Path to source files to process')
    parser.add_argument('--output-dir', type=os.path.abspath, required=True)
    parser.add_argument(
        '--described-objects', type=os.path.abspath, required=False,
        help='A path to a python file containing a dictionary from python objects to tuples consisting of module and '
             'qualname for each object (e.g. ModuleType: ("types", "ModuleType")). Such objects\' names and modules '
             'will not be deduced based on runtime data and provided names and modules will be used instead. Provided '
             'python file must have DESCRIBED_OBJECTS dictionary on the module level.'
    )
    parser.add_argument(
        '--modules-aliases', type=os.path.abspath, required=False,
        help='Path to module names to aliases mapping in json format.'
    )
    args = parser.parse_args()

    # Making sure our module is imported from provided src-root even
    # another version of the module is installed in the system
    override_module_import_path(args.module_root, args.src_root)

    if args.described_objects:
        spec = importlib.util.spec_from_file_location(
            'described_objects', os.path.join(os.getcwd(), args.described_objects)
        )
        described_objects = importlib.util.module_from_spec(spec)
        sys.modules['described_objects'] = described_objects
        spec.loader.exec_module(described_objects)
        described_objects = getattr(described_objects, 'DESCRIBED_OBJECTS', None)
        if described_objects is None:
            raise RuntimeError('DESCRIBED_OBJECTS dict should be defined in python file specified in described-objects')

    if args.modules_aliases:
        with open(args.modules_aliases) as f:
            modules_aliases_mapping = json.load(f)

    for module_name, module in traverse_modules(args.module_root, args.src_root):
        dst_path = module.__file__.replace(args.src_root, args.output_dir) + 'i'

        # Normalizing paths before comparison
        dst_path = os.path.abspath(dst_path)
        src_path = os.path.abspath(module.__file__)
        assert src_path != dst_path, f'Attempting to override source file {module.__file__}'

        # Ensuring dst directory exists
        dst_dir = os.path.dirname(dst_path)
        os.makedirs(dst_dir, exist_ok=True)

        # Actually creating a file
        print(f'{module_name} -> {dst_path}')
        with open(dst_path, 'w') as stub_flo:
            builder = RepresentationsTreeBuilder(
                module_name=module_name,
                module=module,
                module_root=args.module_root,
                described_objects=args.described_objects and described_objects,
                modules_aliases_mapping=args.modules_aliases and modules_aliases_mapping
            )

            viewer = StubViewer()
            module_view = viewer.view(builder.module_rep)
            stub_flo.write(module_view)


if __name__ == '__main__':
    main()
