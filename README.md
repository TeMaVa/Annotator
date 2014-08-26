Annotator
=========
Sisältää ohjelmat

* Annotator : ohjelma autokuvatiedostojen annotointiin
* Visualizer : ohjelma luokitustodennäköisyyksien tarkasteluun
* SendData.py : luokittimen asiakasohjelma
* DnnServer.py : luokittimen palvelinohjelma

Riippuvuudet
------------

* clang
* qt + qtcreator
* python2.7
* nnForge / pylearn2

Visualizerin käyttö
-------------------
Tiedosto->Avaa näyttää luokitustiedoston todennäköisyydet graafisesti.
Tiedosto->Luokita lähettää annetun kansion kaikki kuvat palvelimelle, joka
kutsuu luokitinta. Luokitustodennäköisyydet tulevat paluuviestinä,
ja ne näytetään graafisesti.
