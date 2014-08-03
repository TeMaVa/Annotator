#include "visualizer.h"
#include "ui_visualizer.h"

Visualizer::Visualizer(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::Visualizer)
{
    ui->setupUi(this);
	createMenus();
	createActions();
	connectAll();
	ui->edelBtn->setShortcut(tr("c"));
	ui->seurBtn->setShortcut(tr("v"));
}

Visualizer::~Visualizer()
{
    delete ui;
}

void Visualizer::createMenus()
{
	fileMenu = ui->menuBar->addMenu(tr("&Tiedosto"));
	fileMenu->addAction(openAct);
	fileMenu->addSeparator();
	fileMenu->addAction(exitAct);

	helpMenu = ui->menuBar->addMenu(tr("&Apua"));
	helpMenu->addAction(aboutQtAct);
}

void Visualizer::createActions()
{

	openAct = new QAction(tr("&Avaa..."), this);
	openAct->setShortcuts(QKeySequence::Open);
	openAct->setStatusTip(tr("Avaa ennustustiedosto"));
	connect(openAct, SIGNAL(triggered()), this, SLOT(open()));

	exitAct = new QAction(tr("&Lopeta"), this);
	exitAct->setShortcuts(QKeySequence::Quit);
	exitAct->setStatusTip(tr("Poistu ohjelmasta"));
	connect(exitAct, SIGNAL(triggered()), this, SLOT(close()));

	aboutQtAct = new QAction(tr("Tietoja &Qt:sta"), this);
	aboutQtAct->setStatusTip(tr(""));
	connect(aboutQtAct, SIGNAL(triggered()), qApp, SLOT(aboutQt()));

	//    testAct = new QAction(this);
	//    connect(testAct, SIGNAL(triggered()), this, SLOT(incCounter()));
}

void Visualizer::connectAll()
{
	connect(ui->seurBtn, SIGNAL(clicked()), this, SLOT(seurBtnClick()));
	connect(ui->edelBtn, SIGNAL(clicked()), this, SLOT(edelBtnClick()));
}

void Visualizer::open()
{

}

void Visualizer::seurBtnClick()
{

}

void Visualizer::edelBtnClick()
{

}