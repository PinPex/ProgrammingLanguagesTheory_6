from PyQt6.QtWidgets import *
from PyQt6 import uic
from typing import *
from dataclasses import dataclass
import os
import sys
import json

@dataclass
class Machine:
    Q: List[str]
    V: List[str]
    Func: Dict[str, Dict[str, str]]
    Start: str
    End: str

def throwMessageBox(self, windowTitle: str, message: str):
    mes = QMessageBox(self)
    mes.show()
    mes.setWindowTitle(windowTitle)
    mes.setText(message)
def machine_input(filename):
    with open(filename, "r") as json_file:
        data = json.load(json_file)
    states = data["states"]
    alphabet = data["alphabet"]
    func = data["Func"]
    start = data["start"]
    ends = data["ends"]
    machine = Machine(states, alphabet, func, start, ends)
    return machine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() # Call the inherited classes __init__ method
        uic.loadUi('mainWindow.ui', self) # Load the .ui file
        self.show() # Show the GUI
        self.loadButton.clicked.connect(self.loadMachine)
        self.pathButton.clicked.connect(self.getPath)

    def getPath(self):
        path = QFileDialog.getOpenFileName()
        self.pathLine.setText(path[0])

    def loadMachine(self):
        filepath = self.pathLine.text()
        if not os.path.exists(filepath):
            throwMessageBox(self,"Ошибка","Файла не существует. Проверьте правильность "
                                                       "введенного пути")
            return

        self.machine = machine_input(filepath)

        self.drawMachine = DrawMachine(self.machine)

class DrawMachine(QDialog):
    def __init__(self, machine, parent = None):
        super().__init__(parent)
        uic.loadUi('drawMachine.ui', self) # Load the .ui file
        self.show() # Show the GUI
        self.machine = machine
        self.printMachine(machine)
        self.checkSequenceButton.clicked.connect(self.checkSequence)

    def printMachine(self, machine):
        self.machineTable.setRowCount(len(machine.Q) + 1)
        self.machineTable.setColumnCount(len(machine.V) + 1)

        self.machineTable.setItem(0, 0, QTableWidgetItem("δ"))
        for i, v in enumerate(machine.V):
            self.machineTable.setItem(0, i + 1, QTableWidgetItem(f"'{v}'"))

        for i, q in enumerate(machine.Q):
            self.machineTable.setItem(i + 1, 0, QTableWidgetItem(f"{q}:"))
            for j, v in enumerate(machine.V):
                text = "λ"
                state = machine.Func.get(q)
                if state is not None:
                    passage = state.get(v)
                    if passage is not None:
                        text = passage
                self.machineTable.setItem(i + 1, j + 1, QTableWidgetItem(text))

        self.machineTable.resizeColumnsToContents()
        self.machineTable.resizeRowsToContents()
        self.machineTable.removeColumn(self.machineTable.columnCount() - 1)
    def checkSequence(self):
        sequence = self.sequenceLine.text()
        if sequence == "":
            throwMessageBox(self,"Ошибка", "Введите цепочку")
            return
        if not all([c in self.machine.V for c in sequence]):
            throwMessageBox(self, "Ошибка", "Слово состоит из символов, которых нет в алфавите.\n")
            return
        self.outCheckingSequences = OutCheckingSequences(machine=self.machine,sequence=sequence)


class OutCheckingSequences(QDialog):
    def __init__(self, machine, sequence, parent=None):
        super().__init__(parent)
        uic.loadUi('outCheckingSequences.ui', self)
        self.machine = machine
        self.sequence = sequence
        self.check_button()
        self.quitButton.clicked.connect(self.close)
        self.show()

    def check_button(self):
        self.check_word(self.sequence, self.machine, self.machine.Start)

    def check_word(self, word, machine, state):
        if word == "λ":
            self.sequenceText.insertPlainText(f"({state}, {word})\n")
            self.sequenceText.insertPlainText(f"Конечное состояние: {state}\n")
            if state in machine.End:
                self.sequenceText.insertPlainText("Цепочка принадлежит заданному ДКА.\n")
            else:
                self.sequenceText.insertPlainText("Ошибка. Конечное состояние не принадлежит множеству конечных "
                                                  "состояний ДКА.\n")
            return

        self.sequenceText.insertPlainText(f"({state}, {word})\n")
        if len(word) > 1:
            self.sequenceText.insertPlainText(f"(δ({state},{word[0]}), {word[1:]})\n")
            try:
                state = machine.Func[state][word[0]]
            except KeyError:
                self.sequenceText.insertPlainText("Ошибка. Отсутствует переход для данного состояния.\n")
                return
            word = word[1:]
        else:
            self.sequenceText.insertPlainText(f"(δ({state},{word[0]}), λ)\n")
            try:
                state = machine.Func[state][word[0]]
            except KeyError:
                self.sequenceText.insertPlainText("Ошибка. Отсутсвует переход для данного состояния.\n")
                return
            word = "λ"
        self.check_word(word, machine, state)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    app.exec()
