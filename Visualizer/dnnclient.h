#ifndef DNNCLIENT_H
#define DNNCLIENT_H

#include <QWidget>

namespace Ui {
class DnnClient;
}

class DnnClient : public QWidget
{
    Q_OBJECT

public:
    explicit DnnClient(QWidget *parent = 0);
    ~DnnClient();

    Ui::DnnClient *ui;

private:

    void createActions();
    void createMenus();
};

#endif // DNNCLIENT_H
