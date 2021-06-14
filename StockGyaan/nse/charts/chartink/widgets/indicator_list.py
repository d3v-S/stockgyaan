from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from nse.data.data_chartink_charts import G_lower_indictors, G_overlay_indicators
from nse.charts.chartink.widgets.indicator_input import IndicatorInput
from common.ui import CHARTINK_INDICATOR_LIST_MAX_WIDTH


class IndicatorList(QListWidget):
    def __init__(self):
        super(QListWidget, self).__init__()
        self.setObjectName("indicator_list")
        self.setSpacing(1)
        self.setUI()
        self.setMaximumWidth(CHARTINK_INDICATOR_LIST_MAX_WIDTH)

    def setUI(self):
        lower= []
        lower_default = []
        for i in G_lower_indictors:
            lower.append(i[0].strip())
            lower_default.append(i[3].strip())
        for i in G_overlay_indicators:
            lower.append(i[0].strip())
            lower_default.append(i[3].strip())
        for index, i in enumerate(lower):
            self.addIndicator(i, lower_default[index])



    def addIndicator(self, text, def_val):
        ii = IndicatorInput(text, def_val)
        item = QListWidgetItem()
        item.setSizeHint(ii.sizeHint())  ## mandatory
        self.addItem(item)
        self.setItemWidget(item, ii)


    def getIndicators(self):
        dict_ = {}
        for i in range(self.count()):
            item = self.item(i)
            item_widget = self.itemWidget(item)
            ret = item_widget.getState()
            if ret is not None:
                param_list = []
                params = ret[1].split(",")
                for p in params:
                    param_list.append(p.strip())
                dict_[ret[0]] = param_list
        return dict_








