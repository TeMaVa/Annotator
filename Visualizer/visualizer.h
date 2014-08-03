#ifndef VISUALIZER_H
#define VISUALIZER_H

#include <QMainWindow>

namespace Ui {
class Visualizer;
}

class Visualizer : public QMainWindow
{
    Q_OBJECT

public:
    explicit Visualizer(QWidget *parent = 0);
    ~Visualizer();

private:
    Ui::Visualizer *ui;
	void connectAll();
	void createMenus();
	void createActions();
	void open();

	QMenu *fileMenu;
	QMenu *helpMenu;
	QAction *openAct;
	QAction *exitAct;
	QAction *aboutQtAct;
private slots:
	void seurBtnClick();
	void edelBtnClick();
};

#endif // VISUALIZER_H
