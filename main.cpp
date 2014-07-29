#include "mainwindow.h"
#include <QApplication>

int main(int argc, char *argv[])
{
//    QApplication a(argc, argv);
//    MainWindow w;
//    w.show();

//    return a.exec();
    Q_INIT_RESOURCE(annotator);

    QApplication app(argc, argv);
    app.setOrganizationName("QtProject");
    app.setApplicationName("Application Example");
    MainWindow mainWin;
    mainWin.show();
    return app.exec();
}
