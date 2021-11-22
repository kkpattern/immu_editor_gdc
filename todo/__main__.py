import sys

from todo.app import TodoApp


def main():
    todo_app = TodoApp()
    sys.exit(todo_app.exec_())


if __name__ == "__main__":
    main()
