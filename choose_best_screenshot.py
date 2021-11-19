import ast
import itertools
import os
import sys
from pathlib import Path
from typing import List, Dict

from PySide2 import QtCore, QtGui, QtWidgets


class Dialog(QtWidgets.QDialog):
    def __init__(self, paths: List[Path]):
        QtWidgets.QDialog.__init__(self)

        outerLayout = QtWidgets.QVBoxLayout(self)

        self.viewportLayout = QtWidgets.QStackedLayout(self)
        self.viewportLayout.setStackingMode(
            QtWidgets.QStackedLayout.StackingMode.StackAll
        )

        for path in paths:
            viewer = self.makeQLabelFromImage(str(path))
            self.viewportLayout.addWidget(viewer)

        self.numberOverlay = QtWidgets.QLabel(
            self, text=str(self.viewportLayout.currentIndex() + 1)
        )

        self.editor = QtWidgets.QLineEdit(self, maxLength=1)
        self.editor.returnPressed.connect(self.handleReturnPressed)
        self.editor.installEventFilter(self)

        outerLayout.addLayout(self.viewportLayout)
        outerLayout.addWidget(self.numberOverlay)
        outerLayout.addWidget(self.editor)

    def makeQLabelFromImage(self, path: str) -> QtWidgets.QLabel:
        viewer = QtWidgets.QLabel(self)
        viewer.setMinimumSize(QtCore.QSize(400, 400))
        viewer.setScaledContents(True)
        viewer.setPixmap(QtGui.QPixmap(path))
        return viewer

    def eventFilter(self, obj, event):
        if obj == self.editor and event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key_Right:
                self.viewportLayout.setCurrentIndex(
                    self.viewportLayout.currentIndex() + 1
                )
            elif event.key() == QtCore.Qt.Key_Left:
                self.viewportLayout.setCurrentIndex(
                    self.viewportLayout.currentIndex() - 1
                )
            else:
                return False
            self.numberOverlay.setText(str(self.viewportLayout.currentIndex() + 1))
            return True
        return False

    def handleReturnPressed(self):
        if self.editor.text().lower() == "q":
            self.reject()
        else:
            self.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    args = app.arguments()[1:]
    if len(args) != 1:
        raise ValueError("enter one argument")

    if not Path(args[0]).is_file():
        Path(args[0]).write_text("{}")

    bestPicPerScene: Dict[int, Any] = ast.literal_eval(Path(args[0]).read_text())

    for i in itertools.count(1):
        paths = list(Path.cwd().glob(f"**/*-{str(i).zfill(3)}-0*.png"))
        if not paths:
            break
        if i in sorted(bestPicPerScene):
            continue

        dialog = Dialog(paths)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            if dialog.editor.text():
                bestPicPerScene[i] = dialog.editor.text()
            else:
                bestPicPerScene[i] = dialog.viewportLayout.currentIndex() + 1
            print(f"For scene {i}, you chose {bestPicPerScene[i]}")
        else:
            break

    print(bestPicPerScene)
    Path(args[0]).write_text(str(bestPicPerScene))

if __name__ == "__main__":
    main()
