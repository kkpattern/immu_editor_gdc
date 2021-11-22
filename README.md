This todo app is a demo for demonstrating how a immutable data based editor
framework works.

The app requires python3 and PySide6 to run. It's tested on Windows and MacOS.

## Run

To start the app, run `start.bat` on Windows or run `./start.sh` on MacOS.

Press `enter` in the input box to create a new todo item.

Toggle the checkbox to mark a todo item finished or not.

You can click the color label to change the label color for the todo item.

## Repo structure

This repository is mainly composed by two parts. The `framework` directory
contains all the framework code. Which is independent of the todo app. The
`todo` directory contains all the todo app related code.
