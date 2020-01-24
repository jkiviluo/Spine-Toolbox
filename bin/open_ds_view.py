import sys
import locale
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QApplication
import spinetoolbox.resources_icons_rc  # pylint: disable=unused-import
from spinetoolbox.spine_db_manager import SpineDBManager
from spinetoolbox.widgets.data_store_widget import DataStoreForm
from spinetoolbox.helpers import spinedb_api_version_check, pyside2_version_check


def main(argv):
    """Launches Data Store view as it's own application.

    Args:
        argv (list): Command line arguments
    """
    if not pyside2_version_check():
        return 0
    if not spinedb_api_version_check():
        return 0
    try:
        path = argv[1]
    except IndexError:
        return 0
    app = QApplication(argv)
    QFontDatabase.addApplicationFont(":/fonts/fontawesome5-solid-webfont.ttf")
    locale.setlocale(locale.LC_NUMERIC, 'C')
    url = f"sqlite:///{path}"
    db_mngr = SpineDBManager()
    tree = DataStoreForm(db_mngr, (url, "main"))
    tree.show()
    return_code = app.exec_()
    return return_code


if __name__ == '__main__':
    sys.exit(main(sys.argv))