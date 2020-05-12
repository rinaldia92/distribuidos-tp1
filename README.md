# Trabajo práctico N° 1: Code Searcher
## Sistemas Distribuidos I (75.74)

<h1 align="center">
  <img src="./images/logofiuba.jpg" alt="logo fiuba">
</h1>

## Autor: Alan Rinaldi
## Fecha: 12 de mayo 2020




## Indice:

   - [1- Objetivo](#1--objetivo)
   - [2- Arquitectura](#2--arquitectura)
     - [2.1- Diagrama de robustez](#21--diagrama-de-robustez)
     - [2.2- Diagrama de actividades](#22--diagrama-de-actividades)
     - [2.3- Diagrama de clases](#23--diagrama-de-clases)
   - [3- Codigo](#3--codigo)


## 1- Objetivo

Se solicita el diseño de un sistema distribuido que brinde una solución simple de busqueda en multiples repositorios Git.
Este debe poder aceptar peticiones de:
* Descargas de repositorios GitHub dada su url y branch.
* Busquedas de archivos que con al menos una ocurrencia de un patrón regex.

&nbsp;

## 2- Arquitectura

La arquitectura propuesta para este trabajo consiste en un servidor encargado de recibir las peticiones de los clientes, enviarlas hacia el procesador y responder al usuario, y un procesador encargado de recibir las peticiones y descargar los repositorios o realizar la busqueda segun corresponda.

### 2.1- Diagrama de robustez

#### General

#### Server

<img src="/images/robustez-server.svg">

El servidor posee 4 tipos de controladores para distribuir el procesamiento:
* downloader_controller: encargado de recibir las peticiones de descargas y reenviandolas al **procesador**.
* query_downloader: encargado de recibir las peticiones de busqueda, renviarlas al **procesador** y leer de la cola de resultados correspondiente para armar la respuesta al cliente.
* grep_results_controller: se encarga de recibir los mensajes de resultados del **procesador** y enviarlos a la cola de resultados correspondiente.
* thread_monitor_controller: se encarga de chequear si los demas threads estan en funcionamiento, sino para a todos.

Habrá tantas colas de resultados como threads que ejecuten el controlador de peticiones de busquedas.

#### Procesador

<img src="/images/robustez-procesador.svg">

El procesador consta de 7 tipos de controladores (de los cuales 3 se muestran separados de dicho grafico):
* download_controller: recibe la solicitud de descarga del **server**, descarga el repositorio, lo guarda y envia a la cola de nuevos repositorios informacion de que existe un nuevo repositorio disponible.
* updates_repositories_controller: lee de la cola de nuevos repositorios y actualiza el archivo `repositories_list` con la nueva información y le cambia el estado al repositorio antiguo si existe.
* query_controller: recibe los pedidos de busqueda, realiza un grep en `repositories_list` para saber que repositorios corresponden con la busqueda y los envia a la cola de greap_search.
* grep_files_controller: lee de la cola en que repositorios hay que buscar, realiza un grep con la regex pedida y envia los resultados al **server**


Los otros dos controladores son:
* monitor_controller: cada cierto tiempo verifica la cantidad de elementos que hay en la cola para saber la cantidad de pedidos que faltan procesar.
* garbage_collector_controller: cada cierto tiempo, lee el archivo `repositories_list` y busca los repositorios con `status = oldest`, elimina dichos repositorios y actualiza `repositories_list` dejando solo los demas repositorios.
* thread_monitor_controller: se encarga de chequear si los demas threads estan en funcionamiento, sino para a todos.

<img src="/images/robustez-monitor.svg">

<img src="/images/robustez-garbage-collector.svg">


El archivo `repositories_list` guarda el nombre del repositorio, branch, el nombre completo del repositorio (uuid + nombre + branch) y un status, el cual puede ser `actual`, `old` y `oldest`, `old` corresponde al anteultimo repositorio descargado, que luego pasa a `oldest` al descargarse nuevamente. Esto es por si aun queda en la cola `grep_search` algun pedido sobre ese repositorio justo cuando el garbage collector se activa. 

### 2.2- Diagrama de actividades

<img src="/images/actividades-procesador.svg">

<img src="/images/actividades-server.svg">


### 2.3- Diagrama de clases

En este diagrama se observan las 4 distintas clases que se utilizaron. Pero no hay interaccion entre ellas directamente, sino que son manejadas a traves de los distintos controladores.

<img src="/images/clases.svg">

## 3- Codigo

El código se divide de la siguiente manera:

* processor:
    * main.py: Encargado de levantar la configuracion inicial y lanzar los threads correspondientes.
    * common: carpeta donde se encuantran las clases `Server`, `Client`, `Thread` y `Lock`, codigo de los distintos controladores y funcionalidades utiles.
* server:
    * main.py: Encargado de levantar la configuracion inicial y lanzar los threads correspondientes.
    * common: carpeta donde se encuantran las clases `Server`, `Client` y `Thread` y codigo de los distintos controladores.
* client:
    * main.py:
        * branch master: Realiza muchas requests para probar concurrencia.
        * branch interactive: Es un pequeño cliente interactivo.


