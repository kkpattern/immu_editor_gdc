import argparse
import sys

from level.app import LevelDesigner


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test-case")
    return parser.parse_args()


def main():
    args = parse_args()
    level_designer = LevelDesigner(args.test_case)
    sys.exit(level_designer.exec_())


if __name__ == "__main__":
    main()
