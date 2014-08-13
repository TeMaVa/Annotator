#include "dnnclient.h"
#include "ui_dnnclient.h"

DnnClient::DnnClient(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::DnnClient)
{
    ui->setupUi(this);

    createActions();
    createMenus();
    ui->edelBtn->setShortcut(tr("c"));
    ui->seurBtn->setShortcut(tr("v"));
}

DnnClient::~DnnClient()
{
    delete ui;
}

void DnnClient::createMenus()
{

}
void DnnClient::createActions()
{


}
