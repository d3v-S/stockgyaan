

# watchlist items
WL_ITEM_MAX_WIDTH = 70
WL_ITEM_MAX_HEIGHT = 15
WL_ITEM_BUTTON_MAX_WIDTH = 15
WL_ITEM_LABEL_SYM_FONT_SIZE = str(11)
WL_ITEM_LABEL_PRICE_FONT_SIZE = str(10)
WL_UPDATE_INTERVAL = 5
WL_INPUT_MAX_HEIGHT = 45
WL_STATUS_MAX_HEIGHT =30



# watchlist
WL_MAX_WIDTH = 300
WL_FONT_SIZE = 10



# chartink periods
CHARTINK_PERIOD_1MIN = 1
CHARTINK_PERIOD_3MIN = 2
CHARTINK_PERIOD_5MIN = 3
CHARTINK_PERIOD_15MIN = 10
CHARTINK_PERIOD_60MIN = 60
CHARTINK_PERIOD_DICT = {
    1: 1,
    3: 1,
    5: 2,
    15: 10,
    30: 20,
    60: 30,
    120: 120,
    240: 365
}


# chartink image download period
CHARTINK_DOWNLOAD_PERIOD = 10


# chartink Indicator items
CHARTINK_INDICATOR_LABEL_MAX_WIDTH=100
CHARTINK_INDICATOR_INPUT_MAX_WIDTH = 70
CHARTINK_INDICATOR_ITEM_MAX_HEIGHT=35
CHARTINK_INDICATOR_LIST_MAX_WIDTH = 300


# PAPERTRADE
PAPERTRADE_INPUT_HEIGHT = 50
PAPERTRADE_ACTIVE_TRADE_UPDATE_INTERVAL = 10000 # ms
PAPERTRADE_INPUT_UPDATE_INTERVAL = 20      # seconds
PAPERTRADE_EXIT_BUTTON_WIDTH = 30
# STATUS
STATUS_MAX_HEIGHT = 30

# TIMERS
CANDLESTICK_UPDATE_TIMER = 50



# STYLESHEET

STYLESHEET = """
        
        QListWidgetItem {
            margin: 3px;
        }

        QTabWidget::pane { /* The tab widget frame */
                border-top: 1px solid #C2C7CB;
        }
        
        QTabWidget::tab-bar {
            left: 2px; /* move to the right by 5px */
            font-size: 9px;
        }
        
        QSplitter::handle:horizontal {
             width: 5px;
        }

        QSplitter::handle:vertical {
            height: 5px;
        }
        
        QTableView, QComboBox, QTabBar, QHeaderView {
            font-size: 10px;
        }

            
        #status {
            padding: 0px;
            font-size: 12px;
            margin: 0px;
            max-height: 30px;
        }
        
        #indicator_list{
            padding: 1px;
            font-size: 11px;            
        }
        
        #delete_button{
            max-width: 15px;
            font-size: 10px;
            text-align: center;
        }
        
        #label_author {
            font-size: 12px;
            color: blue;
        }
        
        #label_desc{
            font-size: 11px;
            margin-bottom: 20px;        }
        }
        
        #label_img {
            margin-bottom: 30px;
        }
    
        
        """