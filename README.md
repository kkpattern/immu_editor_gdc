This project is a demo for demonstrating how an immutable data based editor
framework works.

The app requires python3 and PySide6 to run. It's tested on Windows and MacOS.

## Run

To start the todo app, run `start_todo.bat` on Windows or run `./start_todo.sh` on MacOS.

Press `enter` in the input box to create a new todo item.

Toggle the checkbox to mark a todo item finished or not.

You can click the color label to change the label color for the todo item.

To start the level designer, run `start_level.bat` on Windows or run `./start_level.sh` on MacOS.


## Debug

You can open the debug window by clicking the `Debug->View tree` menu. The
debug window will show the current view tree of the todo app. The data of each
view and the submit data callback of each view. The debug window will update in
real time.

## Repo structure

This repository is mainly composed by two parts.

### framework

The `framework` directory contains all the framework code. Which is independent
of the todo app.

The `framework/data.py` contains the `DataManager` class. Which is responsible
for managing the data history.

The `framework/view.py` contains some common base view classes. The most
important one is `ViewBase`.

The `ViewBase.try_refresh` is the interface an
editor will use to update the UI. It will compare the new data with the old data
the current view holds. If there're any difference it will call `ViewBase.refresh`
to update the UI.

The `ViewBase.bind_child_view` is used to bind a child view to a parent view.
Every time the `try_refresh` method of a parent view is called, it will call
all the children's `try_refresh` method. When bind a child view to a parent view,
you need to provide a data convert function. Which is used to return the data that
the child view cares from the parent view's data.


### todo

The `todo` directory contains all the todo app related code.

The `todo/data.py` contains the data model of the todo app.

The `todo/view.py` contains all the view classes of the todo app.


### level

The `level` directory contains all the level designer related code.

The `level/data.py` contains the data model of the level designer.

The `level/view.py` contains all the view classes of the level designer.


## Assets

Assets downloaded from [https://kenney.nl/assets/hexagon-pack](https://kenney.nl/assets/hexagon-pack).
License: (CC0 1.0 Universal)
