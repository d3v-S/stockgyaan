from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QLineEdit, QCompleter


def QLECompleter(list_string):
    qle = QLineEdit()
    model = QStringListModel()
    model.setStringList(list_string)
    completer = QCompleter()
    completer.setModel(model)
    qle.setCompleter(completer)
    return (qle, model)


