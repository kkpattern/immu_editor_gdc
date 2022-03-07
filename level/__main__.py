import sys

from level.app import LevelDesigner


def main():
    level_designer = LevelDesigner()
    sys.exit(level_designer.exec_())


if __name__ == "__main__":
    main()
