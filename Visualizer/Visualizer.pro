#-------------------------------------------------
#
# Project created by QtCreator 2014-08-03T13:13:14
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets printsupport

TARGET = Visualizer
TEMPLATE = app


SOURCES += main.cpp\
        visualizer.cpp \
    qcustomplot.cpp

HEADERS  += visualizer.h \
    qcustomplot.h

FORMS    += visualizer.ui
