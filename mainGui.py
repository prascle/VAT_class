
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QIODevice

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui_file_name = "main.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)
    window.tbw.setTabText(0, "Target overview")
    window.tbw.setTabText(1, "Fits contents specifications")
    window.tbw.setTabText(2, "Download data")
    for i in range(window.tbw.count()):
        window.tbw.setTabEnabled(i, False)
    window.tbw.setTabEnabled(0, True)
    window.tbw.setCurrentIndex(0)

    window.show()

    sys.exit(app.exec_())

# ---------------------------------------------------
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QIODevice

app = QApplication()

ui_file_name = "main.ui"
ui_file = QFile(ui_file_name)
loader = QUiLoader()
window = loader.load(ui_file)
ui_file.close()
window.tbw.setTabText(0, "Target overview")
window.tbw.setTabText(1, "Fits contents specifications")
window.tbw.setTabText(2, "Download data")
window.show()

sys.exit(app.exec_())
