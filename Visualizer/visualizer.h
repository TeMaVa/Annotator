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
};

#endif // VISUALIZER_H
