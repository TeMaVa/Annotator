#-------------------------------------------------
#
# Project created by QtCreator 2014-07-26T10:44:42
#
#-------------------------------------------------

QMAKE_LFLAGS += -lboost_regex -lboost_filesystem -lboost_system
QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = Annotator2
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp

HEADERS  += mainwindow.h

FORMS    += mainwindow.ui

RESOURCES += \
    annotator.qrc

OTHER_FILES +=
