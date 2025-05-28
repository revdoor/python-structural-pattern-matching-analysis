import argparse
import ast
from pattern_converter import convert_pattern


if __name__ == '__main__':
    # run:
    # python analyze.py -t <target_file>
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', required=True)
    args = parser.parse_args()

    target = args.target

    code = "".join(line for line in open(target, 'r').readlines())

    root = ast.parse(code)

    print(ast.dump(root, indent=4))

    for node in ast.walk(root):
        if isinstance(node, ast.pattern):
            try:
                pattern = convert_pattern(node)
                print(f"Converted pattern: {pattern}")
            except Exception as e:
                print(f"Error converting pattern {node}: {e}")
