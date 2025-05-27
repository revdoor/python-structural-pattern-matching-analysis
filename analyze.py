import argparse
import ast


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
