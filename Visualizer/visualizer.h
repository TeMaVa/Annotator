#ifndef VISUALIZER_H
#define VISUALIZER_H

#include <map>
#include <string>
#include <vector>
#include <fstream>

#include <QMainWindow>

namespace Ui {
class Visualizer;
}

class Visualizer : public QMainWindow
{
    Q_OBJECT

    typedef std::map<std::string, QVector<double> > file2vek_t;
public:
    explicit Visualizer(QWidget *parent = 0);
    ~Visualizer();

private:
    Ui::Visualizer *ui;
	void connectAll();
	void createMenus();
	void createActions();
    void readProb(std::ifstream& inputS);

	QMenu *fileMenu;
	QMenu *helpMenu;
	QAction *openAct;
	QAction *exitAct;
	QAction *aboutQtAct;
    file2vek_t file2vek;
    std::vector<std::string>::iterator fileit;
    std::vector<std::string> paths;
    QVector<double> x;
private slots:
	void seurBtnClick();
	void edelBtnClick();
    void open();
};

#endif // VISUALIZER_H
