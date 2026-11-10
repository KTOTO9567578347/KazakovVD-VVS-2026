MAIN_WINDOWS_STYLE = """
            QWidget {
                background-color: #000080;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                color: #00FF00;
            }
            
            QGroupBox {
                border: 3px dashed #FF00FF;
                margin-top: 15px;
                padding: 10px;
                background-color: #000044;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #FFFF00;
                font-size: 14px;
            }

            QLabel {
                color: #00FF00;
                font-size: 16px;
                background: transparent;
            }

            QLineEdit, QComboBox, QPlainTextEdit {
                background-color: #000000;
                border: 2px solid #00FFFF;
                color: #FFFF00;
                font-size: 13px;
                selection-background-color: #FF00FF;
            }
            
            QLineEdit:focus, QPlainTextEdit:focus {
                border: 2px solid #FF00FF;
                background-color: #111111;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 2px;
                border-left-color: #00FFFF;
                border-left-style: solid;
                background-color: #FF00FF;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF0000, stop:1 #880000); /* Кровавый B2B градиент */
                border: 3px outset #FFFFFF;
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                padding: 5px 15px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF00FF, stop:1 #00FFFF); /* Сваг-наведение */
                color: #000000;
                border: 3px inset #FFFFFF;
            }

            QPushButton:pressed {
                background-color: #FFFF00;
                color: #FF0000;
            }
        """

ERROR_WINDOWS_STYLE = """
                QDialog { background-color: #880000; border: 5px solid #FF0000; }
                QLabel { color: #FFFFFF; font-size: 14px; font-weight: bold; }
                QPushButton { background-color: #000000; border: 2px solid #FFFFFF; color: #FF0000; }
                QPushButton:hover { background-color: #FF0000; color: #000000; }
            """