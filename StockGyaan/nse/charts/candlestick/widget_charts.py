



# custom class passed to Finplot
from PyQt5 import sip
from PyQt5.QtCore import QRectF, Qt, QSettings
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGraphicsView, QWidget, QSplitter
from PyQt5.sip import delete

import finplot as fplt

import pyqtgraph as pg

from common.charts_ import setCandleStickColors, plotCandles, updateCharts
from common.utils_ import setUpParent, dbgCharts, dbgOK


class ChartsGV:
    """ class to help extract a Graphics View from finplot item. """
    def __init__(self,
                 parent=None,
                 num_rows=1,
                 init_zoom_periods=100,
                 alignment="vertical",
                 onClickHandler= None,
                 ctrlOnClickHandler=None,
                 min_height=300):
        (self.parent, self.log, self.status) = setUpParent(parent)

        setCandleStickColors()
        self.gv = QGraphicsView()

        # for now : just 1 row.
        self.num_rows = 1
        self.init_zoom_periods = init_zoom_periods
        self.alignment = alignment
        self.plot_widgets = fplt.create_plot_widget(self.gv.window(),
                                                    rows=self.num_rows,
                                                    init_zoom_periods=self.init_zoom_periods,
                                                    onClickHandler = onClickHandler,
                                                    ctrlOnClickHandler = ctrlOnClickHandler,
                                                    restore=False)
        # onclickhandler
        self.onClickHandler = onClickHandler
        self.ctrlOnClickHandler = ctrlOnClickHandler

        # plot items returned by plotting
        self.candlestickitem = None
        self.baritem = None

        # minimal config
        self.gv.setMinimumHeight(min_height)

        # set up UI for this graphic View
        self.setGvUI()

        # if graph has been plotted, use update.
        self.plotted = False

        # current rect: everytime at update, save where it was zoomed.
        self.curr_rect = None

        # lines
        self.infinite_lines = []

        # rois
        self.rois = []
        self.pos_list = []
        self.trend_lines_restored = False

    def setGvUI(self):
        if self.alignment == "horizontal":
            hbox = QHBoxLayout()
        else:
            hbox = QVBoxLayout()
        hbox.addWidget(self.plot_widgets.ax_widget)
        self.plot_widgets.set_visible(crosshair=True, xaxis=True, yaxis=True, xgrid=True, ygrid=True)
        self.gv.window().axs = [self.plot_widgets]
        self.gv.setLayout(hbox)
        dbgCharts(self, "Charts GraphicsView UI setup done")

    def removePlotFromGv(self):
        QWidget().setLayout(self.gv.layout())
        dbgCharts(self, "removing all children of GraphicsView")

    def getGV(self):
        return self.gv

    def plotCandles(self, df):
        if self.plotted:
            return
        self.candlestickitem = plotCandles(df, self.plot_widgets)
        self.plotted = True
        fplt.show_widget(self.gv, qt_exec=False)
        dbgCharts(self, "Candlesticks plotted ")
        return



    # update === destroying and recreating the chart
    def updateCandleSticks(self, df):
        if self.plotted:
            self.__getROI()
            self._getCurrentRect()
            self.resetGraphView()
            self.plotted = False
        self.plotCandles(df)
        fplt.show(qt_exec=False)
        if self.plotted:
            self.__restoreROI()
            self._restorePreviousRect()
            self.restoreLines()
        dbgCharts(self, "Candlesticks updated.")




    def plotBar(self, df):
        if self.plotted:
            return
        self.baritem = df.plot(ax=self.plot_widgets, kind="bar")
        self.plotted = True
        fplt.show_widget(self.gv, qt_exec=False)
        dbgCharts(self, "BarCharts plotted")
        return

    def updateBar(self, df):
        self.plotBar(df)
        updateCharts(df, self.baritem)
        dbgCharts(self, "BarCharts updated.")

    def removeWindowFromGlobalWindowList(self):
        if self.gv in fplt.windows:
            fplt.windows.remove(self.gv)
            dbgCharts(self, "removing GraphicsView from fplt windows")



    def resetGraphView(self):
        self.plot_widgets = fplt.create_plot_widget(self.gv.window(),
                                                    rows=self.num_rows,
                                                    init_zoom_periods=self.init_zoom_periods,
                                                    onClickHandler=self.onClickHandler,
                                                    ctrlOnClickHandler=self.ctrlOnClickHandler,
                                                    restore=False)
        self.removeWindowFromGlobalWindowList()
        self.removePlotFromGv()
        self.setGvUI()
        dbgCharts(self, "Charts reset")




    def resetVB(self):
        self.plot_widgets.vb.reset()


    def _getCurrentRect(self):
        self.curr_rect = self.plot_widgets.vb.targetRect()

    def _restorePreviousRect(self):
        if isinstance(self.curr_rect, QRectF):
            self.plot_widgets.vb.setRange(rect=self.curr_rect)
            dbgCharts(self, "restoring the Zoom")


    def getCurrentLinesRoi(self):
        return self.plot_widgets.vb.rois
    #
    # def setLines(self, list_rois):
    #     for i in list_rois:
    #         i.setZValue(40)
    #         self.plot_widgets.vb.addItem(i)

    def drawLine(self, y):
        d = self.drawInfiniteLine(y)
        self.infinite_lines.append(d)

    def removeLine(self, y):
        for d in self.infinite_lines:
            if y-5 <= d["y"] <=  y+5:
                self.infinite_lines.remove(d)
                self.plot_widgets.removeItem(d["item"])
                sip.delete(d["item"])


    def restoreLines(self):
        for d in self.infinite_lines:       ## assume it to be deleted.
            d["item"] = self.drawInfiniteLine(d["y"])["item"]
        dbgCharts(self, "restored the INFINITE Lines")


    def removeAllLines(self):
        for d in self.infinite_lines:
            self.infinite_lines.remove(d)
            self.plot_widgets.removeItem(d["item"])
            sip.delete(d["item"])
        dbgCharts(self, "removed all the infinite lines")


    def restoreListOfLines(self, list_y):
        for i in list_y:
            self.drawLine(i)
        dbgCharts(self, "List Of InfiniteLines restored.")


    def drawInfiniteLine(self, y):
        pen = pg.mkPen(style=Qt.SolidLine, solid=[6, 6], color="#ff0")
        hline = pg.InfiniteLine(angle=0, movable=True, pen=pen)
        hline.setPos(y)
        hline.setZValue(45)
        self.plot_widgets.addItem(hline, ignoreBounds=True)
        d = {}
        d["y"] = y
        d["item"] = hline
        return d


    ###
    # restoring ROI:
    ###
    def __getROI(self):
        self.rois = self.plot_widgets.vb.rois[:]
        for i in self.rois:
            pos = []
            for handle in i.handles:
                pos.append(handle['pos'])
            is_duplicate = False  # list of list
            for p in self.pos_list:
                if pos[0].x() == p[0].x() and p[0].y() == pos[0].y() and pos[1].x() == p[1].x() and p[1].y() == pos[1].y():
                    is_duplicate = True
                    break;
            if not is_duplicate:
                self.pos_list.append(pos) # list of points.
        dbgOK(self, "__getROI " + str(self.pos_list))


    def __restoreROI(self):
        self.plot_widgets.vb.rois = []
        for i in self.pos_list:
            p0 = i[0]
            p1 = i[1]
            draw_line = fplt.FinPolyLine(self.plot_widgets.vb, [p0, p1], closed=False, pen=pg.mkPen("#f00"), movable=False)
            draw_line.setZValue(50)
            self.plot_widgets.vb.rois.append(draw_line)
            self.plot_widgets.vb.addItem(draw_line, ignoreBounds=True)
        dbgOK(self, "restored " + str(self.pos_list))


    def removeAllTrendLines(self):
        for i in self.plot_widgets.vb.rois:
            self.plot_widgets.vb.removeItem(i)
        self.plot_widgets.vb.roi = []
        self.pos_list = []

        # for i in self.pos_list:
        #     delete(i)
        # self.pos_list = []



    def getTrendLines(self):
        return self.pos_list

    def setTrendLines(self, list_pos):
        if list_pos is None:
            return
        self.pos_list = list_pos[:]
        self.trend_lines_restored = True
        self.__restoreROI()
        print (" \n\n ******* SET TRENDLINES:  *******" + str(self.pos_list))

