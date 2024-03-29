#!/usr/bin/python

import os
import sys
from PyQt4 import QtCore, QtGui

from ftransc.utils import m3u_extract, check_deps

from ftransc.utils.constants import VERSION

class Window(QtGui.QDialog):
    def __init__(self, parent=None, cmdlinefiles=None):
        super(Window, self).__init__(parent)

        add_files_button = self.createButton("&Add Files", self.add_files)
        convert_button   = self.createButton("Conv&ert", self.convert)
        cancel_button    = QtGui.QPushButton("&Close")
        browse_button    = self.createButton("&Output Folder", self.browse)

        self.delete_original_checkbox = QtGui.QCheckBox("&Delete")
        self.overwrite_checkbox       = QtGui.QCheckBox("Over&write")
        self.unlock_checkbox          = QtGui.QCheckBox("&Unlock")
        self.foldername               = QtGui.QLabel("")
        self.foldername.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)

        head_layout = QtGui.QHBoxLayout()
        body_layout = QtGui.QVBoxLayout()
        foot_layout = QtGui.QHBoxLayout()
        browse_layout = QtGui.QHBoxLayout()
        codec_layout = QtGui.QHBoxLayout()

        head_layout.addWidget(add_files_button)
        head_layout.addWidget(browse_button)
        head_layout.addSpacing(500)

        browse_layout.addWidget(self.foldername)

        codec_label = QtGui.QLabel("Convert To:")
        self.codec_combobox = QtGui.QComboBox()
        formats = list(check_deps())
        formats.sort()
        for fmt in formats:
            self.codec_combobox.addItem(fmt)

        quality_label = QtGui.QLabel("Quality:")
        self.quality_combobox = QtGui.QComboBox()
        presets = ['Insane', 'Extreme', 'High', 'Normal', 'Low', 'Tiny']
        for idx, preset in enumerate(presets):
            self.quality_combobox.addItem(preset)
            if preset == 'Normal':
                self.quality_combobox.setCurrentIndex(idx)

        codec_layout.addWidget(codec_label)
        codec_layout.addWidget(self.codec_combobox)
        codec_layout.addWidget(quality_label)
        codec_layout.addWidget(self.quality_combobox)

        head_layout.addLayout(codec_layout)
        foot_layout.addWidget(self.delete_original_checkbox)
        foot_layout.addWidget(self.overwrite_checkbox)
        foot_layout.addWidget(self.unlock_checkbox)
        foot_layout.addSpacing(500)
        foot_layout.addWidget(convert_button)
        foot_layout.addWidget(cancel_button)

        self.createFilesTable()

        body_layout.addLayout(head_layout)
        body_layout.addLayout(browse_layout)
        body_layout.addWidget(self.filesTable)
        body_layout.addLayout(foot_layout)

        self.setLayout(body_layout)
        self.setWindowTitle("ftransc Audio Converter v%s" % VERSION)
        self.resize(700, 400)


        self.connect(cancel_button, 
                     QtCore.SIGNAL('clicked()'), 
                     QtGui.qApp, 
                     QtCore.SLOT('quit()'))

        if cmdlinefiles is not None:
            self.cmdlinefiles = cmdlinefiles
            self.add_files(noninteractive=True)
            self.cmdlinefiles = None


    def add_files(self, noninteractive=False):
        if noninteractive:
            files = self.cmdlinefiles
        else:
            filt = "All Files (*)";
            filt += ";;Audio Files (*.mp3 *.wma *.aac *.mp4 *.m4a *.flac *.ogg"
            filt += " *.mpc *.mka *.mp+ *.ape *.wv *.wav *.aiff)"
            filt += ";;Video Files (*.avi *.flv *.mpg *.mpeg *.vob *.divx *.mkv *.mp4)"
            files = QtGui.QFileDialog.getOpenFileNames(self,
                                                       'Add files to convert',
                                                       QtCore.QDir.currentPath(),
                                                       filt)

        for i in files:
            fname = QtGui.QTableWidgetItem(i)
            status = QtGui.QTableWidgetItem('Scheduled')
            row = self.filesTable.rowCount()
            self.filesTable.insertRow(row)
            self.filesTable.setItem(row, 0, fname)
            self.filesTable.setItem(row, 1, status)

    def browse(self):
        folder = QtGui.QFileDialog.getExistingDirectory(self,
                                                       'Add output folder',
                                                      QtCore.QDir.currentPath())
        if folder is not None or folder != '':
            self.foldername.setText(folder)

    def convert(self):
        row_count = self.filesTable.rowCount()
        audio_codec = str(self.codec_combobox.currentText()).lower()
        audio_quality = str(self.quality_combobox.currentText()).lower()
        for row in xrange(row_count):
            status = QtGui.QTableWidgetItem('Scheduled')
            self.filesTable.setItem(0, 1, status)
            self.filesTable.repaint()
        for row in xrange(row_count):
            filename = self.filesTable.item(0, 0).text()
            status = QtGui.QTableWidgetItem('Converting...')
            self.filesTable.setItem(0, 1, status)
            self.filesTable.repaint()
            self.filesTable.repaint()
            
            opts = "--format %s" % audio_codec
            opts += " --quality %s" % audio_quality
            if self.overwrite_checkbox.isChecked():
                opts += ' --over'
            if self.delete_original_checkbox.isChecked():
                opts += ' --remove'
            if self.unlock_checkbox.isChecked():
                opts += ' --unlock'
            if self.foldername.text():
                opts += ' --outdir %s' % self.foldername.text()

            self.filesTable.repaint()
            x = os.system('ftransc %s "%s" > /dev/null 2>&1' % (opts, filename))
            self.filesTable.removeRow(0)
            self.filesTable.repaint()


    def createFilesTable(self):
        self.filesTable = QtGui.QTableWidget(0, 2) 
        self.filesTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.filesTable.setHorizontalHeaderLabels(("Filename", "Status"))
        self.filesTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.filesTable.verticalHeader().hide()
        self.filesTable.setShowGrid(False)
        self.filesTable.setAlternatingRowColors(True)
        self.filesTable.setUpdatesEnabled(True)
        self.filesTable.keyPressEvent = self.delete_items

    def createButton(self, text, member):
        button = QtGui.QPushButton(text)
        button.clicked.connect(member)
        return button

    def delete_items(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            items = self.filesTable.selectedIndexes()
            if items:
                rows = [item.row() for item in items]
                rows = list(set(rows))
                rows.sort()
                rows.reverse()
                for row in rows:
                    self.filesTable.removeRow(row)
        else:
            return QtGui.QTableWidget.keyPressEvent(self.filesTable, event)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window(cmdlinefiles=m3u_extract(sys.argv[1:], mode='playlist'))
    window.show()
    sys.exit(app.exec_())

