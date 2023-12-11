from PyQt6.QtWidgets import *
from PyQt6 import uic
from typing import *
from dataclasses import dataclass
import os
import sys
import json


class DMP:
    def __init__(self, Q, V, Funcs, Start, End, EndStack):
        self.Q = Q
        self.V = V
        self.loadFunc(Funcs)
        self.Start = Start
        self.End = End
        self.EndStack = EndStack
        self.output = ""

    def loadFunc(self, Funcs):
        self.Func = {}
        for func in Funcs:
            self.addFunc(func)

    def addFunc(self, Func):
        self.Func[str( (Func[0][0], Func[0][1], Func[0][2]) )] = str( (Func[1][0], Func[1][1], Func[1][2]) )
    def getFunc(self, Func_ind):

        Func_id_str = str( (Func_ind[0], Func_ind[1], Func_ind[2]) )
        if Func_id_str in self.Func:
            return eval( self.Func[Func_id_str] )
        else:
            return -1

def throwMessageBox(self, windowTitle: str, message: str):
    mes = QMessageBox(self)
    mes.show()
    mes.setWindowTitle(windowTitle)
    mes.setText(message)

def machineInputTxt(filename):
    def passWhileNotFound(f, s):
        while f.readline().strip() != s:
            pass

    def passEmptyStrings(f):
        line = ""
        while (line := f.readline()).strip() == "":
            pass
        return line

    with open(filename, encoding="utf-8") as f:
        try:
            states = passEmptyStrings(f).replace(" ", "").strip().split(":")[1].removesuffix(";").split(",")
            alphabet = passEmptyStrings(f).replace(" ", "").strip().split(":")[1].removesuffix(";").split(",")
            passWhileNotFound(f,"{")
            func_array = []


            while (line := passEmptyStrings(f).strip()) != "}":
                line = line.replace(" ", "").strip().replace(";", "").replace(")", "").replace("(", "")
                vars = line.split('=')
                vars = [i.split(',') for i in vars]

                if len(vars[0][1]) > 1 or len(vars[0][2]) > 1:
                    raise Exception("Must be symbols, not substrings")
                func_array.append(vars)
            start = passEmptyStrings(f).replace(" ", "").strip().split(":")[1].removesuffix(";")
            end = passEmptyStrings(f).replace(" ", "").strip().split(":")[1].removesuffix(";")
            endStack = passEmptyStrings(f).replace(" ", "").strip().split(":")[1].removesuffix(";")
            return DMP(states, alphabet, func_array, start, end, endStack)
        except Exception:
            return -1

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

        self.machine = machineInputTxt(filepath)
        #print(self.machine)
        if self.machine != -1:
            self.drawMachine = DrawMachine(self.machine)
        else:
            throwMessageBox(self,"Ошибка", "Ошибка в синтаксисе файла.")
            return

class DrawMachine(QDialog):
    def __init__(self, machine, parent = None):
        super().__init__(parent)
        uic.loadUi('drawMachine.ui', self)
        self.machine = machine
        self.printMachine(machine)
        self.checkSequenceButton.clicked.connect(self.checkSequence)
        self.show()
        self.outCheckingSequences = []

    def printMachine(self, machine):
        #print(machine.Func)
        funcs = str(machine.Func).replace("{","").replace("}", "").replace('"',"")\
        .replace("'","").replace(":"," =").replace("),", ")\n")
        self.textEdit.setText(funcs)
        pass

    def checkSequence(self):
        sequence: str = self.sequenceLine.text()
        if sequence == "":
            throwMessageBox(self,"Ошибка", "Введите цепочку")
            return
        sequence = sequence.replace(" ","")
        sequences = sequence.split(";")
        #if sequence not in [self.outCheckingSequences[i].sequence for i in range(len(self.outCheckingSequences))]: #and len(self.outCheckingSequences) < 500:
        self.outCheckingSequences.append(OutCheckingSequences(machine=self.machine,sequences=sequences))



class OutCheckingSequences(QDialog):
    def __init__(self, machine, sequences, parent=None):
        super().__init__(parent)
        uic.loadUi('outCheckingSequences.ui', self)
        self.machine = machine
        self.sequences = sequences
        self.check_button()
        self.quitButton.clicked.connect(self.close)
        self.show()

    def check_button(self):
        for seq in self.sequences:
            self.check_word(seq, self.machine, self.machine.Start)

    def check_word(self, word, machine: DMP, state):
        prevText = self.sequenceText.toPlainText()
        machine.output = ""
        seq: str = word
        stat: str = state
        stack: str = machine.EndStack

        output = f"###### Проверка цепочки {seq} ######\n"

        seq_sym = seq[0] if (len(seq) != 0) else "ε"
        stk_sym = stack[0] if (len(stack) != 0) else "ε"

        while (func := machine.getFunc((stat, seq_sym, stk_sym))) != -1:
            fseq = seq if len(seq) != 0 else "λ"
            fstack = stack if len(stack) != 0 else "λ"
            foutput = machine.output if (len(machine.output) != 0) else "λ"
            output += f"({stat},{fseq},{fstack},{foutput})\n"

            seq = seq[1:] if len(seq) != 0 else "ε"
            stack = stack[1:] if len(stack) != 0 else "ε"

            stat = func[0]
            stack = ("" if func[1] == "ε" else func[1]) + stack
            machine.output += ("" if func[2] == "λ" else func[2])

            seq_sym = seq[0] if (len(seq) != 0) else "ε"
            stk_sym = stack[0] if (len(stack) != 0) else "ε"

        fseq = seq if len(seq) != 0 and seq != "ε" else "λ"
        fstack = stack if len(stack) != 0 else "λ"
        foutput = machine.output if (len(machine.output) != 0) else "λ"
        output += f"({stat},{fseq},{fstack},{foutput})\n"

        if len(stack) == 0 and seq == "ε" and stat == machine.End:
            output += (f"Последовательность пуста, стек пуст, достигнуто конечное состояние \n=> Цепочка подходит языку X \n=>"
                       f"Перевод произведен")
        else:
            if stat != machine.End:
                output += (f"Отсутствует переход из состояния '{stat}' по символу '{seq_sym}' последовательности "
                           f"и символу '{stk_sym}' стека\n"
                           f"Конечное состояние не достигнуто\n")
            if len(stack) != 0:
                output += f"Стек не опустошен\n"
            if seq != "ε":
                output += f"Последовательность не пуста\n"
            output += "=> Цепочка не подходит языку X => Перевод невозможен"
        output += "\n"
        self.sequenceText.setText(prevText + output)

    def closeEvent(self, event):
        #self.parent().outCheckingSequences.remove(self)
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
