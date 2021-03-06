from os import path

from PyQt5.QtGui import QPixmap, QPainter, QTransform, QBrush, QColor, QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QSize, QRect

from mindpong.model.mathexercise import MathMode
from mindpong.model.services.mathquestionutils import MathQuestionDifficulty

STYLE_SHEET_PATH = path.join(path.dirname(__file__), "styles.css")

class MathQuestions(QWidget):

    BACKGROUND_COLOR_CODE = '#cfdef7'
    INITIALIZING_TITLE = "Initializing..."
    CHECK_ANSWER_BUTTON_TITLE = 'Check Answer'
    NEXT_QUESTION_BUTTON_TITLE = 'Next Question'
    CONCENTRATION_OBJ_NAME = "toggle_concentration"
    CONCENTRATION_BUTTON_TITLE = 'Switch to Concentration Mode'
    RELAXATION_OBJ_NAME = "toggle_relaxation"
    RELAXATION_BUTTON_TITLE = 'Switch to Relaxation Mode'
    RELAXATION_TITLE = "Please relax now..."
    RELAXATION_BODY = "✋✋ 🧠🧠 ✋✋"

    def __init__(self):
        super().__init__()
        self.setFixedHeight(self.height() - 10)
        self.is_relaxation_activated = False 
        self.init_ui()

    def init_ui(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self._set_labels()
        self._set_configuration_panel()

    def _set_labels(self):
        # Question Label
        self._math_question = QLabel(self.INITIALIZING_TITLE)
        self._math_question.setFont(QFont("Times", 16, QFont.Bold))
        self._math_question.setMargin(70)
        self._math_question.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.grid.addWidget(self._math_question, 0, 0, 1, 1)

        # Equation label
        self._equation_label = QLabel(self.INITIALIZING_TITLE)
        self._equation_label.setFont(QFont("Times", 30, QFont.Bold))
        self.grid.addWidget(self._equation_label, 1, 0, (Qt.AlignCenter))

    def _set_configuration_panel(self):
        self.config_panel_layout = QVBoxLayout()

        self.mode_combo_box = self._init_combo_box(
            [mode.value for mode in MathMode],
            changed_callback=self._mode_changed,
            tooltip="Change the math exercise type"
        )
        self.difficulty_combo_box = self._init_combo_box(
            [diff.value for diff in MathQuestionDifficulty],
            changed_callback=self._difficulty_changed,
            tooltip="Change the math equation's difficulty"
        )

        # Check answer button
        self.check_answer_button = QPushButton(self.CHECK_ANSWER_BUTTON_TITLE)
        self.check_answer_button.setObjectName("check_answer")
        self.check_answer_button.setMaximumWidth(self.check_answer_button.width() * 0.5)
        self.check_answer_button.setStyleSheet(open(STYLE_SHEET_PATH).read())
        self.check_answer_button.clicked.connect(self._on_click_answer_button)

        # Toggle concentration button
        self.toggle_mode_button = QPushButton(self.RELAXATION_BUTTON_TITLE)
        self.toggle_mode_button.setObjectName(self.RELAXATION_OBJ_NAME)
        self.toggle_mode_button.setMaximumWidth(self.toggle_mode_button.width() * 0.5)
        self.toggle_mode_button.setStyleSheet(open(STYLE_SHEET_PATH).read())
        self.toggle_mode_button.clicked.connect(self._on_click_toggle_mode)

        self.config_panel_layout.addWidget(self.mode_combo_box)
        self.config_panel_layout.addWidget(self.difficulty_combo_box)
        self.config_panel_layout.addSpacing(80)
        self.config_panel_layout.addWidget(self.check_answer_button)
        self.config_panel_layout.addWidget(self.toggle_mode_button)
        self.grid.addLayout(self.config_panel_layout, 0, 1, 2, 1, (Qt.AlignVCenter))

    def _init_combo_box(self, items, changed_callback, tooltip):
        combo_box = QComboBox()
        combo_box.setStyleSheet(open(STYLE_SHEET_PATH).read())
        combo_box.setToolTip(tooltip)
        combo_box.addItems(items)
        combo_box.setMinimumWidth(combo_box.width() * 0.35)
        combo_box.setMinimumHeight(combo_box.height() * 0.15)
        combo_box.currentTextChanged.connect(changed_callback)
        return combo_box

    def set_delegate(self, delegate):
        self.delegate = delegate
        self._exercice_model = self.delegate.game.math_exercices
        self._link_model()

    def _link_model(self):
        self._math_question.setText(self._exercice_model.get_question())
        self._equation_label.setText(self._exercice_model.get_equation())

    def _on_click_answer_button(self, event):
        if self._exercice_model.has_shown_answer:
            # show new exercice
            self._exercice_model.update_question()
            self._equation_label.setText(self._exercice_model.get_equation())
            self.check_answer_button.setText(self.CHECK_ANSWER_BUTTON_TITLE)
            self._exercice_model.has_shown_answer = False
        else: 
            # show answer
            self._equation_label.setText(self._exercice_model.get_answer())
            self.check_answer_button.setText(self.NEXT_QUESTION_BUTTON_TITLE)
            self._exercice_model.has_shown_answer = True

    def _on_click_toggle_mode(self, event):
        if self.is_relaxation_activated:
            self._link_model()
            self.toggle_mode_button.setText(self.RELAXATION_BUTTON_TITLE)
            self.toggle_mode_button.setObjectName(self.RELAXATION_OBJ_NAME)
            self.toggle_mode_button.setStyleSheet(open(STYLE_SHEET_PATH).read())
            self._enable_configuration_panel(False)
            self.is_relaxation_activated = False
            self._exercice_model.has_shown_answer = False
        else:
            self._math_question.setText(self.RELAXATION_TITLE)
            self._equation_label.setText(self.RELAXATION_BODY)
            self.toggle_mode_button.setText(self.CONCENTRATION_BUTTON_TITLE)
            self.toggle_mode_button.setObjectName(self.CONCENTRATION_OBJ_NAME)
            self.toggle_mode_button.setStyleSheet(open(STYLE_SHEET_PATH).read())
            self._enable_configuration_panel(True)
            self.is_relaxation_activated = True

    def _mode_changed(self, text):
        new_mode = MathMode(text)
        if new_mode is not self._exercice_model.mode:
            self._exercice_model.has_shown_answer = False
            self._exercice_model.mode = MathMode(text)
            self._exercice_model.update_question()
            self._link_model()

    def _difficulty_changed(self, text):
        new_diff = MathQuestionDifficulty(text)
        if new_diff is not self._exercice_model.difficulty:
            self._exercice_model.has_shown_answer = False
            self._exercice_model.difficulty = MathQuestionDifficulty(text)
            self._exercice_model.update_question()
            self._link_model()

    def _enable_configuration_panel(self, enable: bool):
        self.check_answer_button.setDisabled(enable)
        self.mode_combo_box.setDisabled(enable)
        self.difficulty_combo_box.setDisabled(enable)
    
    def sizeHint(self):
        return QSize(self.width(), self.height())


    def paintEvent(self, e):
        """ paints the background with the blue border """
        painter = QPainter()
        painter.begin(self)
        
        color = QColor()
        color.setNamedColor(self.BACKGROUND_COLOR_CODE)
        painter.setBrush(QBrush(color, Qt.Dense2Pattern))
        painter.setPen(Qt.darkBlue)
        painter.drawRoundedRect(0, 5, self.width()-5, self.height()-7, 3, 3);

        painter.end()

