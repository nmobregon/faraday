# -*- coding: utf-8 -*-
import gi
import re

from gi.repository import Gtk
from persistence.persistence_managers import CouchDbManager
from utils.common import checkSSL
from config.configuration import getInstanceConfiguration

gi.require_version('Gtk', '3.0')

CONF = getInstanceConfiguration()

"""This could probably be made much better with just a little effort.
It'd be probably a good idea to make a super class Dialog from which
all the dialogs inherit from with the common methods used (particularly the
OK and Cancel buttons). Good starting point if we continue on with the idea
of using GTK"""


class PreferenceWindowDialog(Gtk.Window):
    """Sets up a preference dialog with basically nothing more than a
    label, a text entry to input your CouchDB IP and a couple of buttons"""

    def __init__(self):
        Gtk.Window.__init__(self, title="Preferences")
        self.set_size_request(200, 200)
        self.timeout_id = None

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.label = Gtk.Label()
        self.label.set_text("Your Couch IP")
        vbox.pack_start(self.label, True, True, 0)

        self.entry = Gtk.Entry()
        self.entry.set_text("Preferences")
        vbox.pack_start(self.entry, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_end(hbox, False, True, 0)

        self.OK_button = Gtk.Button.new_with_label("OK")
        self.OK_button.connect("clicked", self.on_click_OK)

        hbox.pack_start(self.OK_button, False, True, 0)

        self.cancel_button = Gtk.Button.new_with_label("Cancel")
        self.cancel_button.connect("clicked", self.on_click_cancel)
        hbox.pack_end(self.cancel_button, False, True, 0)

    def on_click_OK(self, button):
        repourl = self.entry.get_text()

        if not CouchDbManager.testCouch(repourl):
            print("NOT A VALID URL")
        if repourl.startswith("https://"):
            if not checkSSL(repourl):
                print("SSL CERTIFICATE VALIDATION FAILED")

        CONF.setCouchUri(repourl)
        CONF.saveConfig()

    def on_click_cancel(self, button):
        self.destroy()


class NewWorkspaceDialog(Gtk.Window):
    def __init__(self, callback=None,  workspace_manager=None):

        Gtk.Window.__init__(self, title="Create New Workspace")
        self.set_size_request(200, 200)
        self.timeout_id = None
        self.callback = callback

        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.nameBox = Gtk.Box(spacing=6)
        self.name_label = Gtk.Label()
        self.name_label.set_text("Name: ")
        self.name_entry = Gtk.Entry()
        self.nameBox.pack_start(self.name_label, False, False, 10)
        self.nameBox.pack_end(self.name_entry, True, True, 10)
        self.nameBox.show()

        self.descrBox = Gtk.Box(spacing=6)
        self.descr_label = Gtk.Label()
        self.descr_label.set_text("Description: ")
        self.descr_entry = Gtk.Entry()
        self.descrBox.pack_start(self.descr_label, False, False, 10)
        self.descrBox.pack_end(self.descr_entry, True, True, 10)
        self.descrBox.show()

        self.typeBox = Gtk.Box(spacing=6)
        self.type_label = Gtk.Label()
        self.type_label.set_text("Type: ")
        self.comboBox = Gtk.ComboBoxText()
        for w in workspace_manager.getAvailableWorkspaceTypes():
            self.comboBox.append_text(w)
        self.typeBox.pack_start(self.type_label, False, False, 10)
        self.typeBox.pack_end(self.comboBox, True, True, 10)
        self.typeBox.show()

        self.buttonBox = Gtk.Box(spacing=6)
        self.OK_button = Gtk.Button.new_with_label("OK")
        self.OK_button.connect("clicked", self.on_click_OK)
        self.cancel_button = Gtk.Button.new_with_label("Cancel")
        self.cancel_button.connect("clicked", self.on_click_cancel)
        self.buttonBox.pack_start(self.OK_button, False, False, 10)
        self.buttonBox.pack_end(self.cancel_button, False, False, 10)
        self.buttonBox.show()

        self.mainBox.pack_start(self.nameBox, False, False, 0)
        self.mainBox.pack_start(self.descrBox, False, False, 0)
        self.mainBox.pack_start(self.typeBox, False, False, 0)
        self.mainBox.pack_end(self.buttonBox, False, False, 0)

        self.mainBox.show()
        self.add(self.mainBox)

    def on_click_OK(self, button):
        letters_or_numbers = r"^[a-z][a-z0-9\_\$()\+\-\/]*$"
        res = re.match(letters_or_numbers, str(self.name_entry.get_text()))
        if res:
            if self.callback is not None:
                self.__name_txt = str(self.name_entry.get_text())
                self.__desc_txt = str(self.descr_entry.get_text())
                self.__type_txt = str(self.comboBox.get_active_text())
                self.callback(self.__name_txt,
                              self.__desc_txt,
                              self.__type_txt)
                self.destroy()
            else:
                self._main_window.showPopup("A workspace must be named with "
                                            "all lowercase letters (a-z), digi"
                                            "ts(0-9) or any of the _$()+-/ "
                                            "characters. The name has to start"
                                            " with a lowercase letter")

    def on_click_cancel(self, button):
        self.destroy()


class OpenWorkspaceDialog(Gtk.Window):
    def __init__(self, callback, workspace_manager):
        Gtk.Window.__init__(self, title="Open Workspace")
        self.set_size_request(200, 200)
        self.workspace_manager = workspace_manager
        self.callback = callback

        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.chooseWorkspace = Gtk.ComboBoxText()
        self.populateWorkspaceList()

        self.mainBox.pack_start(self.chooseWorkspace, True, True, 0)

        self.buttonBox = Gtk.Box(spacing=6)
        self.OK_button = Gtk.Button.new_with_label("OK")
        self.OK_button.connect("clicked", self.on_click_OK)
        self.cancel_button = Gtk.Button.new_with_label("Cancel")
        self.cancel_button.connect("clicked", self.on_click_cancel)
        self.buttonBox.pack_start(self.OK_button, False, False, 10)
        self.buttonBox.pack_end(self.cancel_button, False, False, 10)
        self.buttonBox.show()

        self.mainBox.pack_end(self.buttonBox, False, False, 0)

        self.mainBox.show()
        self.add(self.mainBox)

    def populateWorkspaceList(self):
        for w in self.workspace_manager.getWorkspacesNames():
            self.chooseWorkspace.append_text(w)

    def on_click_OK(self, button):
        self.callback(self.chooseWorkspace.get_active_text())
        self.destroy()

    def on_click_cancel(self, button):
        self.destroy()


class PluginOptionsDialog(Gtk.Window):
    def __init__(self, plugin_manager):

        Gtk.Window.__init__(self, title="Plugins Options")
        self.set_size_request(200, 200)
        plugin_info = self.createPluginInfo(plugin_manager)
        pluginList = self.createPluginListView(plugin_info)

        infoBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        nameBox, versionBox, pluginVersionBox = [Gtk.Box() for i in range(3)]

        nameLabel, versionLabel, pluginVersionLabel = [Gtk.Label()
                                                       for i in range(3)]

        self.nameEntry, self.versionEntry, self.pluginVersionEntry = [
                                                Gtk.Entry() for i in range(3)]

        nameLabel.set_text("Name: ")
        versionLabel.set_text("Version: ")
        pluginVersionLabel.set_text("Plugin version: ")

        nameBox.pack_start(nameLabel, False, False, 5)
        nameBox.pack_start(self.nameEntry, True, True, 5)
        versionBox.pack_start(versionLabel, False, False, 5)
        versionBox.pack_start(self.versionEntry, True, True, 5)
        pluginVersionBox.pack_start(pluginVersionLabel, False, False, 5)
        pluginVersionBox.pack_start(self.pluginVersionEntry, True, True, 5)

        infoBox.pack_start(nameBox, False, False, 5)
        infoBox.pack_start(versionBox, False, False, 5)
        infoBox.pack_start(pluginVersionBox, False, False, 5)

        self.pluginSpecsBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.pluginSpecsBox.pack_start(infoBox, False, False, 5)

        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(pluginList, False, False, 5)
        self.mainBox.pack_end(self.pluginSpecsBox, True, True, 5)

        self.add(self.mainBox)

    def create_entry_box(self, plugin_name, plugin_tool, plugin_version):
        entry_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.name_entry = Gtk.Entry()
        self.name_entry.set_text(plugin_name)
        self.name_entry.set_editable(False)

        self.tool_entry = Gtk.Entry()
        self.tool_entry.set_text(plugin_tool)
        self.tool_entry.set_editable(False)

        self.version_entry = Gtk.Entry()
        self.version_entry.set_text(plugin_version)
        self.version_entry.set_editable(False)

        entry_box.pack_start(self.name_entry, True, True, 6)
        entry_box.pack_start(self.tool_entry, True, True, 6)
        entry_box.pack_end(self.version_entry, True, True, 6)

        return entry_box

    def createPluginInfo(self, plugin_manager):
        plugin_info = Gtk.TreeStore(str, str, str)
        if plugin_manager is not None:
            self.plugin_settings = plugin_manager.getSettings()
        else:
            self.plugin_settings = {}

        for plugin_id, params in self.plugin_settings.iteritems():
            plugin_info.append(None, [params["name"],
                                      params["version"],
                                      params["plugin_version"]])

        return plugin_info

    def createPluginListView(self, plugin_info):
        """Creates the view for the left-hand side list of the dialog.
        It uses an instance of the plugin manager to get a list
        of all available plugins"""

        plugin_list_view = Gtk.TreeView(plugin_info)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=0)
        plugin_list_view.append_column(column)

        selection = plugin_list_view.get_selection()
        selection.connect("changed", self.on_plugin_selection)

        return plugin_list_view

    def on_plugin_selection(self, selection):
        """When the user selects a plugin, it will change the text
        displeyed on the entries to their corresponding values"""

        model, treeiter = selection.get_selected()

        self.nameEntry.set_text(model[treeiter][0])
        self.versionEntry.set_text(model[treeiter][1])
        self.pluginVersionEntry.set_text(model[treeiter][2])
