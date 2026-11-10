import sys
import PyQt6.QtWidgets as Widgets 
from PyQt6.QtCore import Qt
import validators
from validators import MODES, DEFAULT
from calculus import calculate_riemann_sum
from vis import generate_integral_image
from PIL.ImageQt import ImageQt
from PyQt6.QtGui import QPixmap
from styles import MAIN_WINDOWS_STYLE, ERROR_WINDOWS_STYLE

class MainWindow(Widgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ИНТЕГРАТРОН SAAS B2B PLATFORM ULTRA PRO ANALYTICS v2.0 🔥")
        self.resize(1000, 650)

        self.setStyleSheet(MAIN_WINDOWS_STYLE)

        self.main_layout = Widgets.QVBoxLayout()
        
        self.header_group = Widgets.QGroupBox("Полезный математичский софт📊", self)
        self.header_group.setSizePolicy(
            Widgets.QSizePolicy.Policy.Minimum, 
            Widgets.QSizePolicy.Policy.Maximum
        )
        header_layout = Widgets.QHBoxLayout()
        
        self.label = Widgets.QLabel("Интегрирование 😭", self.header_group)
        self.label.setStyleSheet("color: #FF00FF; font-size: 18px; text-decoration: underline;")
        
        self.answer = Widgets.QLabel("🎰 РЕЗУЛЬТАТ: NONE", self.header_group)
        self.answer.setStyleSheet("color: #FFFF00; font-size: 20px; border: 2px dotted #00FF00; padding: 5px;")
        
        header_layout.addWidget(self.label)
        header_layout.addWidget(self.answer)
        self.header_group.setLayout(header_layout)
        self.main_layout.addWidget(self.header_group)

        self.graphing_group = Widgets.QGroupBox("📉📉📉 Графики", self)
        graphing_layout = Widgets.QHBoxLayout()
        
        self.image_label = Widgets.QLabel(self.graphing_group)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.setSizePolicy(
            Widgets.QSizePolicy.Policy.Fixed, 
            Widgets.QSizePolicy.Policy.Fixed
        )
        self.image_label.setStyleSheet("border: 4px solid #00FF00; background-color: #050505;")
        graphing_layout.addWidget(self.image_label)        
        self.graphing_group.setLayout(graphing_layout)
        self.main_layout.addWidget(self.graphing_group)

        # --- INPUT GROUP ---
        self.input_group = Widgets.QGroupBox("Панель управления 🐘", self)
        self.input_group.setSizePolicy(
            Widgets.QSizePolicy.Policy.Minimum, 
            Widgets.QSizePolicy.Policy.Maximum
        )
        input_layout = Widgets.QHBoxLayout()
        input_layout.setSpacing(8)

        # Выбор режима
        self.mode_selection = Widgets.QComboBox(self)
        self.mode_selection.addItems(MODES)
        self.mode_selection.setCurrentIndex(DEFAULT)
        self.mode_selection.setFixedWidth(120)

        self.lbound_input = Widgets.QLineEdit(self.input_group)
        self.lbound_input.setPlaceholderText("L левая граница")
        
        self.rbound_input = Widgets.QLineEdit(self.input_group)
        self.rbound_input.setPlaceholderText("R правая граница (R > L)")
        
        self.n_input = Widgets.QLineEdit(self.input_group)
        self.n_input.setPlaceholderText("N число прямоугольников")
        
        self.start_button = Widgets.QPushButton(self)
        self.start_button.setText("🚀 СТАРТ!")
        self.start_button.clicked.connect(self.run)
        
        self.f_input = Widgets.QPlainTextEdit(self)
        self.f_input.setPlaceholderText("f(x) = ...")
        self.f_input.setSizePolicy(
            Widgets.QSizePolicy.Policy.Expanding,
            Widgets.QSizePolicy.Policy.Minimum
        )
        self.f_input.setMaximumHeight(60) # Сжали высоту, чтобы сидело аккуратно
        
        # Собираем всё в нижний ряд в логичном порядке
        input_layout.addWidget(self.mode_selection)
        input_layout.addWidget(self.lbound_input)
        input_layout.addWidget(self.rbound_input)
        input_layout.addWidget(self.n_input)
        input_layout.addWidget(self.f_input)
        input_layout.addWidget(self.start_button)

        self.input_group.setLayout(input_layout)
        self.main_layout.addWidget(self.input_group)

        self.setLayout(self.main_layout)

    class ErrorDialog(Widgets.QDialog):
        def __init__(self, parent=None, text="Ошибка 0000000"):
            super().__init__(parent)
            self.setWindowTitle("🚨 УЖАСНАЯ ОШИБКА 🚨")
            self.resize(350, 150)
            
            self.setStyleSheet(ERROR_WINDOWS_STYLE)

            layout = Widgets.QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            
            self.err_text = Widgets.QLabel(self)
            self.err_text.setText(f"FATAL ERROR:\n{text}")
            self.err_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.err_text.setWordWrap(True)
            
            self.close_btn = Widgets.QPushButton("ИГНОРИРОВАТЬ РИСКИ")
            self.close_btn.clicked.connect(self.accept)
            
            layout.addWidget(self.err_text)
            layout.addSpacing(10)
            layout.addWidget(self.close_btn)
            self.setLayout(layout)

    def show_error_window(self, err_text:str):
        dialog = self.ErrorDialog(self, text=err_text)
        dialog.exec()
        

    def run(self):
        from validators import is_nat, is_mode, check_bounds;
        data = {
            "method": self.mode_selection.currentText(),
            "L": self.lbound_input.text(),
            "R": self.rbound_input.text(),
            "N": self.n_input.text(),
            "F": self.f_input.toPlainText(),
        }

        if (not check_bounds(data['L'], data['R'])):
            self.show_error_window("Неверные границы.")
            return;
    
        data['L'] = float(data['L'])
        data['R'] = float(data['R'])

        if (not is_nat(data['N'])):
            self.show_error_window("Неверное число прямоугольников.")
            return;
        data['N'] = int(data['N'])

        if (not is_mode(data['method'])):
            self.show_error_window("Неверный режим (чзх).")
            return;

        f = lambda x: x;
        try:
            f = validators.create_vectorized_function(data['F'])
            f(1)
        except Exception as e:
            self.show_error_window("Проверьте корректность функции.")
            return;
        data["F"] = f

        integral_value, x_eval, y_eval, x_bar_pos, align, dx = calculate_riemann_sum(**data)
        print(integral_value)
        pil_image = generate_integral_image(data['F'], data['L'], data['R'], data['N'], data['method'], integral_value, x_eval, y_eval, x_bar_pos, align, dx)
        qt_image = ImageQt(pil_image)
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)
        self.answer.setText(f"РЕЗУЛЬТАТ: {str(integral_value)}")

# Стандартный блок запуска приложения
if __name__ == "__main__":
    app = Widgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
