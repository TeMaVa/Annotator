#include <QtWidgets>

#include <vector>
#include <string>
#include <algorithm>
#include <fstream>

#include <boost/filesystem.hpp>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/regex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#define foreach_ BOOST_FOREACH

#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QDebug>

//MainWindow::MainWindow(QWidget *parent) :
//    QMainWindow(parent),

bool isSelected(const QRadioButton* btn)
{
    return btn->isChecked();
}

MainWindow::MainWindow() :
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    annotCounter = ui->lcdNumber;
    textEdit = ui->plainTextEdit;
    annotCount = 0;
    //TODO: if file exists, read it and set file pointer
    //annotationPath = boost::filesystem::path("annotation.csv");
    selectionList.push_back(ui->hAutoBtn);
    selectionList.push_back(ui->pAutoBtn);
    selectionList.push_back(ui->kAutoBtn);

    createActions();
    createMenus();
    connectAll();

    ui->nnforgeBtn->setShortcut(tr("n"));
    ui->edellinenBtn->setShortcut(tr("c)"));
    ui->seuraavaBtn->setShortcut(tr("v"));
    ui->hAutoBtn->setShortcut(tr("1"));
    ui->pAutoBtn->setShortcut(tr("2"));
    ui->kAutoBtn->setShortcut(tr("3"));
}

MainWindow::~MainWindow()
{
    writeAnnotation();
    delete ui;
    annotationStream.close();
}

void MainWindow::createMenus()
{
    fileMenu = ui->menuBar->addMenu(tr("&Tiedosto"));
    fileMenu->addAction(openAct);
    fileMenu->addSeparator();
    fileMenu->addAction(exitAct);

    helpMenu = ui->menuBar->addMenu(tr("&Apua"));
    helpMenu->addAction(aboutAct);
    helpMenu->addAction(aboutQtAct);
}

void MainWindow::createActions()
{

    openAct = new QAction(QIcon(":/images/open.png"), tr("&Avaa..."), this);
    openAct->setShortcuts(QKeySequence::Open);
    openAct->setStatusTip(tr("Avaa kuvakansio"));
    connect(openAct, SIGNAL(triggered()), this, SLOT(open()));

    exitAct = new QAction(tr("&Lopeta"), this);
    exitAct->setShortcuts(QKeySequence::Quit);
    exitAct->setStatusTip(tr("Exit the application"));
    connect(exitAct, SIGNAL(triggered()), this, SLOT(close()));

    aboutAct = new QAction(tr("&Ohje"), this);
    aboutAct->setStatusTip(tr("Näytä käyttöohje"));
    connect(aboutAct, SIGNAL(triggered()), this, SLOT(about()));

    aboutQtAct = new QAction(tr("Tietoja &Qt:sta"), this);
    aboutQtAct->setStatusTip(tr("Show the Qt library's About box"));
    connect(aboutQtAct, SIGNAL(triggered()), qApp, SLOT(aboutQt()));

//    testAct = new QAction(this);
//    connect(testAct, SIGNAL(triggered()), this, SLOT(incCounter()));
}

void MainWindow::connectAll()
{
    //connect(ui->nnforgeBtn, SIGNAL(clicked()), this, SLOT(on_nnforgeBtn_clicked()));
    connect(ui->edellinenBtn, SIGNAL(clicked()), this, SLOT(loadPrev()));
    connect(ui->seuraavaBtn, SIGNAL(clicked()), this, SLOT(loadNext()));

}

void MainWindow::about()
{
   QMessageBox::about(this, tr("Ohje"),
            tr("dummy"));
}

void MainWindow::open()
{
    QString pathName = QFileDialog::getExistingDirectory(this, tr("Avaa kuvakansio"));
    //QString fileName = QFileDialog::getOpenFileName(this);
    if (!pathName.isEmpty())
    {
        file2class.clear();
        annotationPath = boost::filesystem::path(pathName.toStdString()) / "annotation.csv";
        boost::filesystem::ifstream existingStream;
        existingStream.exceptions(std::ifstream::failbit);
        try
        {
            existingStream.open(annotationPath, std::ios_base::in);
            readAnnotation(existingStream);
            existingStream.close();
        }
        catch (std::ifstream::failure) // file does not exist
        {
            // do nothing
        }
        imgPaths.clear();
        boost::filesystem::path imgPath(pathName.toStdString());
        boost::regex expression(".*.(jpg|png|bmp|jpeg)");
        boost::cmatch what;
        path_vec paths;
        std::copy(boost::filesystem::directory_iterator(imgPath), boost::filesystem::directory_iterator(), std::back_inserter(paths));
        std::sort(paths.begin(), paths.end());
        //QString output = textEdit->toPlainText();
        foreach_(boost::filesystem::path& elem, paths)
        {
            std::string filename = elem.string();
            if (boost::regex_search(filename.c_str(), what, expression))
            {
                imgPaths.push_back(elem);
                //output.append(tr(filename.c_str()) + "\n");
            }
        }
        // set iterator to final image from existing file
        if (!file2class.empty())
        {
            std::string lastFile = file2class.rbegin()->first;
            boost::filesystem::path lastPath = boost::filesystem::path(lastFile);
            imgIt = std::find(imgPaths.begin(), imgPaths.end(), lastPath);
            if (imgIt == imgPaths.end())
            {
                QMessageBox::critical(this, tr("Virhe"), tr("Annotaatiotiedostossa ja kansiossa olevat kuvat eivät täsmää. Ohjelma sulkeutuu."));
                close();
                qApp->quit();
                return;
            }
        }
        else
        {
            imgIt = imgPaths.begin()-1;
        }
        std::string outputStr = boost::lexical_cast<std::string>(imgPaths.size()) + " kuvaa ladattu.\n";
        textEdit->setPlainText(tr(outputStr.c_str()));
        annotationStream.open(annotationPath, std::ios_base::out | std::ios_base::trunc);
        loadNext(true);

        //textEdit->setPlainText(fileName);
//        ui->imgName->setText(fileName);
//        QImage image(fileName);
//        QImage scaled = image.scaled(ui->imBox->width(), ui->imBox->height());
//        ui->imBox->setPixmap(QPixmap::fromImage(scaled));
        //ui->imBox->adjustSize();
    }
}

void MainWindow::incCounter()
{
    annotCounter->display(++annotCount);
}

void MainWindow::loadNext(bool extraCheck)
{
    if(imgPaths.empty())
    {
        QMessageBox::information(this,QString("Virhe"),QString("Kuvia ei ole ladattu"));
        return;
    }

    if (imgIt >= imgPaths.begin())
    {
        boost::filesystem::path currPath = imgPaths.at(imgIt - imgPaths.begin());
        if (extraCheck)
        {
            // try to read old label
            try
            {
                int label = file2class.at(currPath.string());
                selectionList.at(label)->setChecked(true);
            }
            catch (std::out_of_range) {}
        }
        std::vector<QRadioButton*>::iterator it;
        it = std::find_if(selectionList.begin(), selectionList.end(), isSelected);
        file2class[currPath.string()] = it - selectionList.begin();
        annotCounter->display((int)file2class.size());
        //annotationStream << currPath.string() << "," << it - selectionList.begin() << std::endl;
    }
    if (imgIt+1 >= imgPaths.end())
    {
        //ui->imBox->setPixmap();
        //imgIt = imgPaths.end();
        QMessageBox::information(this, tr("FYI"), tr("Kaikki kuvat annotoitu."));
        return;
    }
    imgIt++;
    boost::filesystem::path currPath = imgPaths.at(imgIt - imgPaths.begin());
    // try to read old label
    try
    {
        int label = file2class.at(currPath.string());
        selectionList.at(label)->setChecked(true);
    }
    catch (std::out_of_range)
    {

    }
    QString filename = tr(currPath.string().c_str());
    QImage image = QImage(filename).scaled(ui->imBox->width(), ui->imBox->height());
    ui->imBox->setPixmap(QPixmap::fromImage(image));
    ui->imgName->setText(tr(currPath.string().c_str()));
}

void MainWindow::loadPrev()
{

    if(imgPaths.empty())
    {
        QMessageBox::information(this,QString("Virhe"),QString("Kuvia ei ole ladattu"));
        return;
    }


    if (imgIt < imgPaths.end())
    {
        boost::filesystem::path currPath = imgPaths.at(imgIt - imgPaths.begin());
        std::vector<QRadioButton*>::iterator it;
        it = std::find_if(selectionList.begin(), selectionList.end(), isSelected);
        file2class[currPath.string()] = it - selectionList.begin();
        annotCounter->display((int)file2class.size());
    }
    if (imgIt-1 < imgPaths.begin())
    {
        //imgIt = imgPaths.begin()-1;
        //ui->imBox->setPixmap();
        //ui->imBox->setText(tr("kaikki kuvat annotoitu"));
        return;
    }
    imgIt--;
    boost::filesystem::path currPath = imgPaths.at(imgIt - imgPaths.begin());
    // try to read old label
    try
    {
        int label = file2class.at(currPath.string());
        selectionList.at(label)->setChecked(true);
    }
    catch (std::out_of_range)
    {

    }
    QString filename = tr(currPath.string().c_str());
    QImage image = QImage(filename).scaled(ui->imBox->width(), ui->imBox->height());
    ui->imBox->setPixmap(QPixmap::fromImage(image));
    ui->imgName->setText(tr(currPath.string().c_str()));
}

void MainWindow::writeAnnotation()
{
    //QMessageBox::information(this, tr("FYI"), tr("Kirjoitetaan annotaatiotiedosto."));
    std::map<std::string, int>::iterator it;
    for (it = file2class.begin(); it != file2class.end(); it++)
    {
        annotationStream << it->first << "," << it->second << std::endl;
    }
}

void MainWindow::readAnnotation(boost::filesystem::ifstream &stream)
{
    std::string str;
    while (true)
    {
        std::getline(stream, str); // read a line from .csv
        if (str.size() == 0) // end of file
            break;
        std::vector<std::string> strs;
        boost::split(strs, str, boost::is_any_of(","));
        file2class[strs[0]] = boost::lexical_cast<int>(strs[1]);
    }
}

void MainWindow::on_nnforgeBtn_clicked()
{
    std::system("python predict_autoclasses.py");
}
