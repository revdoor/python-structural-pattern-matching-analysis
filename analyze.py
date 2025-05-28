import argparse
import ast
from pattern_converter import convert_pattern, convert_pattern_matrix


if __name__ == '__main__':
    # run:
    # python analyze.py -t <target_file>
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', required=True)
    args = parser.parse_args()

    target = args.target

    code = "".join(line for line in open(target, 'r').readlines())

    root = ast.parse(code)

    with open(f'ast_dump_{target.split(".")[0]}.txt', 'w') as f:
        f.write(ast.dump(root, indent=4))

    print(ast.dump(root, indent=4))

    for node in ast.walk(root):
        # if isinstance(node, ast.pattern):
        #     try:
        #         pattern = convert_pattern(node)
        #         print(f"Converted pattern: {pattern}")
        #     except Exception as e:
        #         print(f"Error converting pattern {node}: {e}")

        if isinstance(node, ast.Match):
            try:
                pattern_matrix = convert_pattern_matrix(node)

                print(f"Converted pattern matrix")
                for line in pattern_matrix:
                    print(f'[{", ".join(str(p) for p in line)}]')
                print()
            except Exception as e:
                print(f"Error converting match node {node}: {e}")
                print()
