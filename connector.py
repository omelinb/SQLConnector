#!/usr/bin/env python3

from PyQt5.QtCore import QAbstractTableModel, QVariant, Qt
from PyQt5.QtWidgets import (QWidget, QPushButton, QPlainTextEdit, QLineEdit,
                             QMessageBox, QApplication, QDesktopWidget,
                             QTableView, QComboBox, QGridLayout, QLabel)

import psycopg2

import logging
import sqlite3
import sys
import os


BASEDIR = os.path.dirname(os.path.abspath(__file__))


class Connector:
    def __init__(self, connstring, db_type):
        """
        Args:
            connstring: a string
            db_type: a string
        """
        self.connstring = connstring
        self.connector = db_type
        self.description = None
        self.result = None

    def execute(self, query):
        with self.connector.connect(self.connstring) as connect:
            cursor = connect.cursor()
            cursor.execute(query)
            connect.commit()
            self.description = cursor.description
            self.result = cursor.fetchmany(size=100)

    def get_headers(self):
        if self.description:
            return [col[0] for col in self.description]
        return None

    def get_data(self):
        return self.result


class ResultTableModel(QAbstractTableModel):
    def __init__(self, data, headers, parent=None):
        """
        Args:
            data: a list of lists
            headers: a list of strings
        """
        QAbstractTableModel.__init__(self, parent)
        self.data = data
        self.headers = headers

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        elif not self.data:
            return QVariant()
        return QVariant(self.data[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headers[col])
        return QVariant()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.resize(700, 500)
        self.center()
        self.setWindowTitle('SQL Connector')

        grid = QGridLayout()
        grid.setSpacing(20)

        self.connStringLabel = QLabel('Connection', self)
        self.queryFieldLabel = QLabel('Query field', self)
        self.resultTableLabel = QLabel('Result', self)

        self.connString = QLineEdit(':memory:', self)

        self.typesList = QComboBox(self)
        self.typesList.addItem('sqlite3')
        self.typesList.addItem('postgres')

        self.queryField = QPlainTextEdit(self)

        self.resultTable = QTableView(self)

        self.launchButton = QPushButton('Launch', self)

        grid.addWidget(self.connStringLabel, 0, 0)
        grid.addWidget(self.connString, 0, 1)
        grid.addWidget(self.typesList, 0, 2)

        grid.addWidget(self.queryFieldLabel, 1, 0)
        grid.addWidget(self.queryField, 1, 1, 2, 1)

        grid.addWidget(self.resultTableLabel, 4, 0)
        grid.addWidget(self.resultTable, 4, 1, 2, 1)

        grid.addWidget(self.launchButton, 7, 2)

        self.launchButton.clicked.connect(self.on_click)
        self.setLayout(grid)

    def show_message(self, message, title='Message'):
        messageBox = QMessageBox()
        messageBox.setText(message)
        messageBox.setWindowTitle(title)
        messageBox.exec_()

    def on_click(self):
        connString = self.connString.text()
        query = self.queryField.toPlainText()
        dbType = self.typesList.currentText()

        if not connString:
            connString = ':memory:'

        if dbType == 'sqlite3' and connString != ':memory:':
            if not connString.startswith('/'):
                connString = os.path.join(BASEDIR, connString)
            if not os.path.isfile(connString):
                self.show_message('There is no such database file.')
                return

        connector = get_connector(dbType, connString)
        try:
            connector.execute(query)
            data, headers = connector.get_data(), connector.get_headers()

            if not headers:
                self.show_message('There is no result for your query.')

            model = ResultTableModel(data, headers)
            self.resultTable.setModel(model)
        except (psycopg2.ProgrammingError, sqlite3.OperationalError) as e:
            self.show_message(str(e)[0].capitalize() + str(e)[1:], 'Error!')
            logging.error(e)
        except psycopg2.OperationalError as e:
            self.show_message(str(e)[0].capitalize() + str(e)[1:], 'Error!')
            logging.error(e)

    def center(self):
        frameGeometry = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frameGeometry.moveCenter(centerPoint)
        self.move(frameGeometry.topLeft())


def get_connector(dbType, connstring):
    dbTypes = {
        'sqlite3': sqlite3,
        'postgres': psycopg2}
    return Connector(connstring, dbTypes[dbType])


def main():
    formatstring = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        filename='connector.log', level=logging.INFO, format=formatstring)
    app = QApplication(sys.argv)
    mainWidget = MainWidget()
    mainWidget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
