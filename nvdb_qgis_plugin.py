# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NvdbQgisPlugin
                                 A QGIS plugin
 Fetch data from nvdb and visualize it in QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-02-16
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Erlend Ellefsen
        email                : ekbe_97@hotmail.no
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
# NVDB
from PyQt5.QtWidgets import QListWidgetItem
from nvdbapiv3 import nvdbFagdata
from nvdbapiV3qgis3 import nvdbsok2qgis
from .nvdbobjects import *

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the dialog
from .nvdb_qgis_plugin_dialog import NvdbQgisPluginDialog


class NvdbQgisPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # Save reference to the QGIS interface
        self.dlg = NvdbQgisPluginDialog()
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'NvdbQgisPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&NVDB QGIS')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('NvdbQgisPlugin', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/nvdb_qgis_plugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'nvdb_test'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&NVDB QGIS'),
                action)
            self.iface.removeToolBarIcon(action)

    def comboBox_itemChanged(self, index):
        items = getObjInCat(index)
        self.dlg.comboBox_choices.clear()
        self.dlg.comboBox_choices.addItems(items)

    def addItem(self):
        text = str(self.dlg.comboBox_choices.currentText())
        item = QListWidgetItem(text)
        self.dlg.listWidget.addItem(item)

    def removeItem(self):
        current_item = self.dlg.listWidget.currentItem().text()
        if not current_item:
            pass
        else:
            items_list = self.dlg.listWidget.findItems(current_item, QtCore.Qt.MatchExactly)
            for item in items_list:
                r = self.dlg.listWidget.row(item)
                self.dlg.listWidget.takeItem(r)

    def run(self):
        if self.first_start:
            self.first_start = False

        # Clear the contents of the comboBox from previous runs
        self.dlg.comboBox.clear()
        # Populate the comboBox with names of all the loaded layers
        self.dlg.comboBox.addItems(sortCategories())
        # Show the dialog
        self.dlg.show()
        self.dlg.comboBox.currentIndexChanged[str].connect(self.comboBox_itemChanged)
        self.dlg.addButton.clicked.connect(self.addItem)
        self.dlg.removeButton.clicked.connect(self.removeItem)
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            item_list = [str(self.dlg.listWidget.item(i).text()) for i in range(self.dlg.listWidget.count())]
            for item in item_list:
                item_text = item
                item_id = getID(item)
                item = nvdbFagdata(item_id)
                item.filter({'fylke': 38, 'vegsystemreferanse': ['F']})
                nvdbsok2qgis(item, lagnavn=item_text)
            self.dlg.listWidget.clear()
