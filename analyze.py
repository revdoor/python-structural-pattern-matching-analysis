import argparse
import ast
from pattern_converter import convert_pattern, convert_pattern_matrix, get_subjects, get_line_no
from pattern_matching_checker import *


if __name__ == '__main__':
    # run:
    # python analyze.py -t <target_file>
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', required=True)
    args = parser.parse_args()

    target = args.target

    code = "".join(line for line in open(target, 'r').readlines())

    root = ast.parse(code)

    for node in ast.walk(root):
        if isinstance(node, ast.Match):
            print(f"Checking pattern matching in line {node.lineno}:")
            try:
                pattern_matrix = convert_pattern_matrix(node)
                subjects = get_subjects(node)
                line_no_list = get_line_no(node)

                check_useless_patterns(pattern_matrix, subjects, line_no_list)
                check_non_exhaustive_matches(pattern_matrix, subjects)
                print()
            except Exception as e:
                print(f"Error converting match node {node}: {e}")
                print()
