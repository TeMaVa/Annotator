#include "visualizer.h"
#include "ui_visualizer.h"

#include <fstream>
#include <algorithm>

#include <boost/filesystem.hpp>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/regex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#include <boost/lambda/lambda.hpp>
#include <boost/lambda/bind.hpp>
#define foreach_ BOOST_FOREACH

using namespace boost::lambda;

double stf(const std::string& arg)
{
    return boost::lexical_cast<double>(arg);
}

Visualizer::Visualizer(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::Visualizer)
{
    ui->setupUi(this);
    createActions();
	createMenus();
	connectAll();
	ui->edelBtn->setShortcut(tr("c"));
	ui->seurBtn->setShortcut(tr("v"));
    ui->plotBox->addGraph();
    x << 1.0 << 2.0 << 3.0 << 4.0;
    QVector<double> xtick;
    xtick << 1.0 << 2.0 << 3.0 << 4.0;
    QVector<QString> labels;
    labels << "henkilöauto" << "pakettiauto" << "kuorma-auto" << "linja-auto";
    ui->plotBox->xAxis->setLabel("luokka");
    ui->plotBox->yAxis->setLabel("P(luokka)");
    ui->plotBox->xAxis->setRange(0, 5);
    ui->plotBox->xAxis->setAutoTicks(false);
    ui->plotBox->xAxis->setTickVector(xtick);
    ui->plotBox->xAxis->setAutoTickLabels(false);
    ui->plotBox->xAxis->setTickVectorLabels(labels);
    ui->plotBox->yAxis->setRange(0, 1.3);
    ui->plotBox->graph(0)->setLineStyle(QCPGraph::lsImpulse);
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
    openAct->setStatusTip(tr("Avaa todennäköisyystiedosto"));
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
    QString fileName = QFileDialog::getOpenFileName(this, tr("Avaa todennäköisyystiedosto"), "",
                                                    tr("comma separated values (*.csv)"));
    if (!fileName.isEmpty())
    {
        std::ifstream inputS;
        inputS.open(fileName.toStdString().c_str());
        readProb(inputS);
        inputS.close();
    }
}

void Visualizer::readProb(std::ifstream& inputS)
{
    file2vek.clear();
    paths.clear();
    std::string line;
    std::vector<std::string> strs;
    while (true)
    {
        std::getline(inputS, line);
        //std::cout << "reading line " << line << std::endl;
        if (line.size() == 0)
        {
            //std::cout << "breaking" << std::endl;
            break;
        }
        boost::split(strs, line, boost::is_any_of(","));
        std::string filename = strs[0];
        QVector<double> veke(strs.size()-1);
        std::transform(strs.begin()+1, strs.end(), veke.begin(), stf);
        file2vek[filename] = veke;
        //std::cout << file2vek.size() << std::endl;
        paths.push_back(filename);
    }
    std::sort(paths.begin(), paths.end());
    fileit = paths.begin()-1;
    seurBtnClick();
}

void Visualizer::seurBtnClick()
{
    if (file2vek.empty())
    {
        QMessageBox::information(this, tr("Virhe"), tr("Kuvia ei ole ladattu"));
        return;
    }
    if (fileit+1 >= paths.end())
    {
        return;
    }
    fileit++;
    QString filename = tr(fileit->c_str());
    QImage image = QImage(filename).scaled(ui->kuvaBox->width(), ui->kuvaBox->height());
    ui->kuvaBox->setPixmap(QPixmap::fromImage(image));
    ui->plotBox->graph(0)->setData(x, file2vek[*fileit]);
    ui->plotBox->replot();
}

void Visualizer::edelBtnClick()
{
    if (file2vek.empty())
    {
        QMessageBox::information(this, tr("Virhe"), tr("Kuvia ei ole ladattu"));
        return;
    }
    if (fileit-1 < paths.begin())
    {
        return;
    }
    fileit--;
    QString filename = tr(fileit->c_str());
    QImage image = QImage(filename).scaled(ui->kuvaBox->width(), ui->kuvaBox->height());
    ui->kuvaBox->setPixmap(QPixmap::fromImage(image));
    ui->plotBox->graph(0)->setData(x, file2vek[*fileit]);
    ui->plotBox->replot();
}
