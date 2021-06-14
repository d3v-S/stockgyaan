from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget, QCheckBox, QLabel, QLineEdit, QHBoxLayout

from common.utils_ import str2bool
from common.ui import CHARTINK_INDICATOR_LABEL_MAX_WIDTH, \
    CHARTINK_INDICATOR_ITEM_MAX_HEIGHT, CHARTINK_INDICATOR_INPUT_MAX_WIDTH


class IndicatorInput(QWidget):
    def __init__(self, text, def_val=" "):
        super(QWidget, self).__init__()

        self.setMaximumHeight(CHARTINK_INDICATOR_ITEM_MAX_HEIGHT)

        self.checkbox = QCheckBox()
        self.text = text
        self.checkbox.setMaximumWidth(15)

        self.label = QLabel()
        self.label.setText(text)
        self.label.setMaximumWidth(CHARTINK_INDICATOR_LABEL_MAX_WIDTH)

        self.input = QLineEdit()
        self.input.setText(def_val)
        self.input.setMaximumWidth(CHARTINK_INDICATOR_INPUT_MAX_WIDTH)

        self.setUI()
        self.loadState()

    def setUI(self):
        hbox = QHBoxLayout()
        hbox.addWidget(self.checkbox)
        hbox.addWidget(self.label)
        hbox.addWidget(self.input)
        self.setLayout(hbox)


    def getState(self):
        check = self.checkbox.checkState()
        self.saveState()
        if check == 0: # not checked
            return None
        else:
            # (indicator, params)
            return (self.text.strip(), self.input.text().strip())


    def saveState(self):
        settings = QSettings()
        settings.setValue(self.text+"_checkbox", self.checkbox.isChecked())
        settings.setValue(self.text+"_input", self.input.text().strip())
        settings.sync()

    def loadState(self):
        settings=QSettings()
        checkbox_state = settings.value(self.text+"_checkbox")
        if checkbox_state is None:
            return
        self.checkbox.setChecked(str2bool(checkbox_state))
        input_state = settings.value(self.text+"_input")
        self.input.setText(input_state)

