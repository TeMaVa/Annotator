#ifndef VISUALIZER_H
#define VISUALIZER_H

#include <map>
#include <string>
#include <vector>
#include <fstream>

#include <boost/filesystem.hpp>
#include <boost/filesystem/fstream.hpp>

#include <QMainWindow>
#include "dnnclient.h"

namespace Ui {
class Visualizer;
}

class Visualizer : public QMainWindow
{
    Q_OBJECT

    typedef std::map<std::string, QVector<double> > file2vek_t;
    typedef std::vector<boost::filesystem::path> path_vek_t;
public:
    explicit Visualizer(QWidget *parent = 0);
    ~Visualizer();

private:
    Ui::Visualizer *ui;
	void connectAll();
	void createMenus();
	void createActions();
    void readProb(std::ifstream& inputS);
    void writeAnnotation(boost::filesystem::ofstream& outputStream);

    DnnClient *clientWindow;
	QMenu *fileMenu;
	QMenu *helpMenu;
    QMenu *settingsMenu;
	QAction *openAct;
    QAction *openClient;
	QAction *exitAct;
	QAction *aboutQtAct;
    QAction *settingsAct;
    file2vek_t file2vek;
    std::vector<std::string>::iterator fileit;
    std::vector<std::string> paths;
    boost::filesystem::path annotationPath;
    path_vek_t imgPaths;
    QVector<double> x;
    QString serverAddress_;
    int serverPort_;
    int n_packets_;
private slots:
	void seurBtnClick();
	void edelBtnClick();
    void open();
    void classify();
    void serverSettings();
};

#endif // VISUALIZER_H
