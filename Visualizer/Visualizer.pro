#-------------------------------------------------
#
# Project created by QtCreator 2014-08-03T13:13:14
#
#-------------------------------------------------

QMAKE_LFLAGS += -lboost_regex -lboost_filesystem -lboost_system

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets printsupport

TARGET = Visualizer
TEMPLATE = app


SOURCES += main.cpp\
        visualizer.cpp \
    qcustomplot.cpp \
    dnnclient.cpp

HEADERS  += visualizer.h \
    qcustomplot.h \
    dnnclient.h

FORMS    += visualizer.ui \
    dnnclient.ui

RESOURCES += \
    res.qrc

OTHER_FILES +=
