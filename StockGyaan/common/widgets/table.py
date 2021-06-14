
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pandas as pd
from natsort import natsorted, index_natsorted, order_by_index



# show dataframe as QTableView
# https://stackoverflow.com/questions/55310051/displaying-pandas-dataframe-in-qml/55310236#55310236
# https://github.com/eyllanesc/stackoverflow/tree/master/questions/44603119
#
# usage => Qtableview.setModel(DFModel(df)), QTableView.setSorting(enabled)
# #
from common.utils_ import setUpParent, defaultSlot, dbgOK


class DataFrameModel(QAbstractTableModel):
    DtypeRole = Qt.UserRole + 1000
    ValueRole = Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    pyqtSlot(int, Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QVariant()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QVariant()

    def roleNames(self):
        roles = {
            Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles
    
    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        if order == 0:
            self._dataframe = self._dataframe.reindex(index=order_by_index(self._dataframe.index, index_natsorted(eval('self._dataframe.%s' % (list(self._dataframe.columns)[column])))))
        else:
            self._dataframe = self._dataframe.reindex(index=order_by_index(self._dataframe.index, reversed(index_natsorted(eval('self._dataframe.%s' % (list(self._dataframe.columns)[column]))))))

        self._dataframe.reset_index(inplace=True, drop=True)
        self.setDataFrame(self._dataframe)
        self.layoutChanged.emit()


class DfTable(QTableView):
    def __init__(self, parent=None, name="dfTable", cellDoubleClickSlot=None):
        super(DfTable, self).__init__()
        (self.parent, self.log, self.status) = setUpParent(parent)
        self.name = name
        self.setObjectName(self.name + "_qtv")

        # user-defined handler / slot
        self.cellDoubleClickSlot = cellDoubleClickSlot

        # config.
        self.setSortingEnabled(True)
        self.doubleClicked.connect(lambda qmodelindex: self.cellDoubleClick(qmodelindex))

    def cellDoubleClick(self, qmodelindex):
        #https://stackoverflow.com/questions/19442050/qtableview-how-can-i-get-the-data-when-user-click-on-a-particular-cell-using-mo
        dbgOK(self, "double clicked -- " + str(qmodelindex.data()))
        if self.cellDoubleClickSlot is not None:
            self.cellDoubleClickSlot(qmodelindex)
        else:
            defaultSlot(self, "cellDoubleClickSlot", str(self.name))

    def setDf(self, df):
        self.setModel(DataFrameModel(df))

    def getContainer(self):
        return self
