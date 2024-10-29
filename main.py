import multiprocessing
import re
import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, pyqtSignal
import pyperclip
from QT_ui import Ui_main
from search_fun import Cal_fin, read_data


class Worker(QThread):
    finished = pyqtSignal(tuple)

    def __init__(self, patterns, all_data):
        super().__init__()
        self.patterns = patterns
        self.all_data = all_data

    def run(self):
        sequences, time_cal, count_numbers, len_data = Cal_fin(self.patterns, self.all_data)
        self.finished.emit((sequences, time_cal, count_numbers, len_data))


class MainWindow(QtWidgets.QWidget):
    send_text = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker = None
        self.sequences = ''
        self.time_cal = 0
        self.gailv = 0
        self.f_gailv = ''
        self.f_geshu = ''
        self.all_data = ''

        self.ui = Ui_main.Ui_Form()
        self.ui.setupUi(self)
        self.ui.Cal_button.clicked.connect(self.to_cal)
        self.ui.Down_button.clicked.connect(self.copy_sequences)
        self.ui.Console_button.clicked.connect(self.copy_Console)
        self.ui.time_button.clicked.connect(self.time_button)
        self.ui.gailv_button.clicked.connect(self.gailv_fun)
        self.ui.fgailv_button.clicked.connect(self.f_gailv_fun)
        self.ui.geshu_button.clicked.connect(self.geshu_fun)

    def geshu_fun(self):
        pyperclip.copy(str(self.f_geshu))

    def gailv_fun(self):
        pyperclip.copy(str(self.gailv))

    def f_gailv_fun(self):
        pyperclip.copy(str(self.f_gailv))

    def time_button(self):
        pyperclip.copy(str(self.time_cal))

    def copy_sequences(self):
        pyperclip.copy(self.sequences)

    def copy_Console(self):
        pyperclip.copy(self.ui.information.toPlainText())

    def to_cal(self):
        self.gailv = 0
        self.f_gailv = ''

        input_text = self.ui.Cal_textEdit.toPlainText()
        fruit_list = re.split('[，,\n\s*]', input_text)
        patterns = [fruit for fruit in fruit_list if fruit]
        if self.all_data == '':
            try:
                self.ui.information.append('加载初始化数据')
                self.all_data = read_data('./Data')
                # self.ui.information.append('\n')
            except Exception as e:
                print(e)
                # 在这里处理异常，例如打印错误消息或者显示错误对话框
        if self.all_data == '':
            self.ui.information.append('加载数据失败，Data文件夹是否存在？')
        else:
            self.ui.information.append("查询：" + str(patterns))
            self.ui.information.append('正在计算')
            self.worker = Worker(patterns, self.all_data)
            self.worker.finished.connect(self.handle_result)
            self.worker.start()

    def handle_result(self, result):
        sequences, time_cal, count_numbers, len_data = result
        self.sequences = sequences
        self.time_cal = time_cal

        if len(sequences) > 5000:
            self.ui.Down_textEdit.setPlainText(sequences[:5000] + '......')
        else:
            self.ui.Down_textEdit.setPlainText(sequences)

        self.ui.information.append("执行时间: " + str(time_cal))

        temp_count = sum(count_numbers.values())  # 计算总数量

        temp_f_geshu_count = '\n'.join(map(str, count_numbers.values()))  # 使用map和join代替for循环
        self.f_geshu = temp_f_geshu_count
        self.ui.information.append('总共查询到 ' + str(temp_count) + ' 个')
        if temp_count != 0:
            self.ui.information.append('\n'.join([num + ' 查询到 ' + str(count) + ' 个' for num, count in count_numbers.items()]))  # 使用列表推导式和join
            self.ui.information.append('\n'.join([num + ' 概率为 ' + str(100 * (len(str(num)) * count) / len_data) + ' %' for num, count in count_numbers.items()]))  # 使用列表推导式和join
            self.f_gailv = '\n'.join([str(100 * (len(str(num)) * count) / len_data) for num, count in count_numbers.items()])  # 使用列表推导式和join
        self.gailv = sum([100 * (len(str(num)) * count) / len_data for num, count in count_numbers.items()])  # 使用列表推导式和sum

        self.ui.information.append('总出现概率为 ' + str(self.gailv) + ' %\n')

    def closeEvent(self, event):
        sys.stdout = sys.__stdout__
        super().closeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
