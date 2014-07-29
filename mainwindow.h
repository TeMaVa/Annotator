#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QtWidgets>

#include <vector>
#include <boost/filesystem.hpp>
#include <boost/filesystem/fstream.hpp>
#include <map>

class QAction;
class QMenu;
class QPlainTextEdit;
class QGraphicsView;
class QLCDNumber;
class QPushButton;

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

    typedef std::vector<boost::filesystem::path> path_vec;

public:
    //explicit MainWindow(QWidget *parent = 0);
    MainWindow();
    ~MainWindow();

private:
    Ui::MainWindow *ui;
    QMenu *fileMenu;
    QMenu *helpMenu;
    QAction *openAct;
    QAction *exitAct;
    QAction *aboutAct;
    QAction *aboutQtAct;
    QAction *testAct;
    QLCDNumber* annotCounter;
    QPlainTextEdit* textEdit;

    path_vec imgPaths;
    path_vec::iterator imgIt;
    boost::filesystem::ofstream annotationStream;
    boost::filesystem::path annotationPath;
    std::vector<QRadioButton*>selectionList;
    std::map<std::string, int> file2class;
    int annotCount;

    void connectAll();
    void createMenus();
    void createActions();
    void readAnnotation(boost::filesystem::ifstream& stream);
    void writeAnnotation();

private slots:
    void incCounter();
    void open();
    void about();
    void loadNext(bool extraCheck = false);
    void loadPrev();
    void ignoreImg();

    void on_nnforgeBtn_clicked();
};

#endif // MAINWINDOW_H
