#include <QInputDialog>

#include "visualizer.h"
#include "ui_visualizer.h"
#include "dnnclient.h"
#include "ui_dnnclient.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include <fstream>
#include <algorithm>

#include <boost/filesystem.hpp>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/regex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#include <boost/thread.hpp>
#include <boost/chrono.hpp>
#define foreach_ BOOST_FOREACH

const char* fifofile = "/tmp/DNNFIFO";

double stf(const std::string& arg)
{
    try
    {
        return boost::lexical_cast<double>(arg);
    }
    catch (boost::bad_lexical_cast e)
    {
        std::cout << "cannot convert string " << arg << std::endl;
        throw(e);
    }
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
    clientWindow = new DnnClient;
}

Visualizer::~Visualizer()
{
    delete ui;
    delete clientWindow;
}

void Visualizer::createMenus()
{
	fileMenu = ui->menuBar->addMenu(tr("&Tiedosto"));
	fileMenu->addAction(openAct);
    fileMenu->addAction(openClient);
	fileMenu->addSeparator();
	fileMenu->addAction(exitAct);

	helpMenu = ui->menuBar->addMenu(tr("&Apua"));
	helpMenu->addAction(aboutQtAct);
}

void Visualizer::createActions()
{

    openAct = new QAction(QIcon(":/images/open.png"), tr("&Avaa..."), this);
	openAct->setShortcuts(QKeySequence::Open);
    openAct->setStatusTip(tr("Avaa todennäköisyystiedosto"));
	connect(openAct, SIGNAL(triggered()), this, SLOT(open()));

    openClient = new QAction(tr("Luokita.."), this);
    openClient->setStatusTip(tr("Luokita kansion kuvat"));
    connect(openClient, SIGNAL(triggered()), this, SLOT(classify()));

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

void Visualizer::classify()
{
    bool debug = false;
    QString pathName = QFileDialog::getExistingDirectory(this, tr("Avaa kuvakansio"));
    if (!pathName.isEmpty())
    {
        bool ok;
        int packets = QInputDialog::getInt(this, tr("Kuvapakettien määrä"),
                                             tr("Kuvapakettien määrä:"),
                                             1, 1, 10000, 1, &ok);
        if (!ok)
            return;
        file2vek.clear();
        annotationPath = boost::filesystem::path(pathName.toStdString()) / "annotationClient.csv";
        boost::filesystem::path imgPath(pathName.toStdString());
        boost::filesystem::ofstream outputStream;
        outputStream.open(annotationPath, std::ios_base::out | std::ios_base::trunc);
        imgPaths.clear();
        boost::regex expression(".*.(jpg|png|bmp|jpeg)");
        boost::cmatch what;
        path_vek_t paths;
        std::copy(boost::filesystem::directory_iterator(imgPath), boost::filesystem::directory_iterator(), std::back_inserter(paths));
        std::sort(paths.begin(), paths.end());
        // Filter non-images out
        foreach_(boost::filesystem::path& elem, paths)
        {
            std::string filename = elem.string();
            if (boost::regex_search(filename.c_str(), what, expression))
            {
                imgPaths.push_back(elem);
            }
        }

        writeAnnotation(outputStream);

        // create named pipe
        mknod(fifofile, S_IFIFO|0666, 0);

        std::string receivedFile = "classification.csv";
        boost::filesystem::path absolutePath = boost::filesystem::absolute(boost::filesystem::path(receivedFile));
        const char* cmd;
        if (debug)
            cmd = ("python2 ../SendData.py "  "mylongest4annotation.csv" " " + receivedFile).c_str();
        else
            cmd = ("python2 ../SendData.py " + annotationPath.string() + " " + receivedFile + " " + boost::lexical_cast<std::string>(packets)).c_str();

        std::cout << "cmd: " << cmd << std::endl;
        boost::thread python_thread(std::system, cmd);
        std::ifstream fifoin(fifofile, std::ios::in);
        std::string line;
        boost::regex numExpression("([0-9]+)\\/([0-9]+) classified");
        while (true)
        {
            std::getline(fifoin, line);
            if (line.size() > 0)
            {
                //std::cout << "got line " << line << std::endl;
                boost::regex_search(line.c_str(), what, numExpression);
                //std::cout << "num1 = " << what[1].str() << " num2 = " << what[2].str() << std::endl;
                unsigned num1 = boost::lexical_cast<unsigned>(what[1].str());
                unsigned num2 = boost::lexical_cast<unsigned>(what[2].str());
                ui->image_n->display((int)num1);
                ui->N_images->display((int)num2);
                ui->progressBar->setValue((unsigned)((float)num1/(float)num2*100.0F));
                this->repaint();
                if (num1 >= num2-1)
                    break;
                std::cout << line << std::endl;
            }
            else
            {
                this->repaint();
                boost::this_thread::sleep_for(boost::chrono::milliseconds(100));
            }

        }

        python_thread.join();
        
        // delete fifos
        unlink(fifofile);
        //unlink("/tmp/DNNFIFO2");


        // read results to file2vek
        try
        {
            boost::filesystem::ifstream inputStream(absolutePath, std::ios::in) ;
            if (!inputStream) throw std::ios::failure("Virhe avatessa tiedostoa.");
            //std::cout << "opening " << absolutePath.string() << std::endl;
            readProb(inputStream);
            inputStream.close();
            seurBtnClick();
        }
        catch (const std::exception e) // file does not exist
        {
            QString virhestr = tr("Poikkeus: ") + QString(e.what());
            QMessageBox::critical(this, tr("VIRHE"), tr("Tiedostoa ") + QString(receivedFile.c_str()) + tr(" ei voitu lukea. ") + virhestr);
            qApp->exit(1);
            return;
        }
    }
}

void Visualizer::writeAnnotation(boost::filesystem::ofstream& outputStream)
{
    path_vek_t::iterator it;
    for (it = imgPaths.begin(); it != imgPaths.end(); it++)
    {
        outputStream << it->string() << "," << 0 << std::endl;
    }
    outputStream.close();
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
        seurBtnClick();
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
    ui->imgNameBox->setText(filename);
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
    ui->imgNameBox->setText(filename);
}
