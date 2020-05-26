# Trabajo práctico N° 1: Code Searcher
## Sistemas Distribuidos I (75.74)

<h1 align="center">
  <img src="./images/logofiuba.jpg" alt="logo fiuba">
</h1>

## Autor: Alan Rinaldi
## Fecha: 12 de mayo 2020
## Fecha reentrega: 26 de mayo 2020




## Indice:

   - [1- Objetivo](#1--objetivo)
   - [2- Arquitectura](#2--arquitectura)
     - [2.1- Diagrama de robustez](#21--diagrama-de-robustez)
     - [2.2- Diagrama de actividades](#22--diagrama-de-actividades)
        - [2.2.1- Diagrama de actividades del server](#221--diagrama-de-actividades-del-server)
        - [2.2.2- Diagrama de actividades del processor](#222--diagrama-de-actividades-del-processor)
     - [2.3- Diagrama de clases](#23--diagrama-de-clases)
        - [2.3.1- Diagrama de clases del server](#231--diagrama-de-clases-del-server)
        - [2.3.2- Diagrama de clases del processor](#232--diagrama-de-clases-del-processor)
   - [3- Codigo](#3--codigo)
   - [4- Cosas a mejorar](#4--cosas-a-mejorar)


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
* process_controller: se encarga de chequear si los demas procesos estan en funcionamiento, sino para a todos. (Corre en el proceso principal).

Habrá tantas colas de resultados como procesos que ejecuten el controlador de peticiones de busquedas.

#### Procesador

<img src="/images/robustez-procesador.svg">

El procesador consta de 7 tipos de controladores (de los cuales 3 se muestran separados de dicho grafico):
* download_controller: recibe la solicitud de descarga del **server**, descarga el repositorio, lo guarda y envia a la cola de nuevos repositorios informacion de que existe un nuevo repositorio disponible.
* updates_repositories_controller: lee de la cola de nuevos repositorios y actualiza el archivo `repositories_list` con la nueva información y le cambia el estado al repositorio antiguo si existe.
* query_controller: recibe los pedidos de busqueda, realiza un grep en `repositories_list` para saber que repositorios corresponden con la busqueda y los envia a la cola de greap_search.
* grep_files_controller: lee de la cola en que repositorios hay que buscar, realiza un grep con la regex pedida y envia los resultados al **server**


Los otros tres controladores son:
* monitor_controller: cada cierto tiempo verifica la cantidad de elementos que hay en la cola para saber la cantidad de pedidos que faltan procesar.
* garbage_collector_controller: cada cierto tiempo, lee el archivo `repositories_list` y busca los repositorios con `status = oldest`, elimina dichos repositorios y actualiza `repositories_list` dejando solo los demas repositorios.
* process_controller: se encarga de chequear si los demas threads estan en funcionamiento, sino para a todos.

<img src="/images/robustez-monitor.svg">

<img src="/images/robustez-garbage-collector.svg">


El archivo `repositories_list` guarda el nombre del repositorio, branch, el nombre completo del repositorio (uuid + nombre + branch) y un status, el cual puede ser `actual`, `old` y `older`, `old` corresponde al anteultimo repositorio descargado, que luego pasa a `older` al descargarse nuevamente. Esto es por si aun queda en la cola `grep_search` algun pedido sobre ese repositorio justo cuando el garbage collector se activa. 

### 2.2- Diagrama de actividades

### 2.2.1- Diagrama de actividades del server

<img src="/images/actividades-procesador.svg">

### 2.2.2- Diagrama de actividades del processor

<img src="/images/actividades-server.svg">


### 2.3- Diagrama de clases

En este diagrama se observan las principales clases que se utilizaron y su interaccion.

### 2.3.1- Diagrama de clases del server

<img src="/images/clases-server.svg">

### 2.3.2- Diagrama de clases del processor

<img src="/images/clases-procesador.svg">

## 3- Codigo

El código se divide de la siguiente manera:

* common: (clases compartidas entre los distintos modulos)
  * client.py: Implementación de socket como cliente.
  * controller.py: Clase padre de un controller con los principales metodos definidos.
  * dispatcher.py: Clase que nos abstrae la creacion de un cliente, el envio del mensaje y cerrado de la conexion. 
  * middleware.py: Clase que funciona como interface para recibir un mensaje de un socket cliente y poder responderle.
  * process_controller.py: Clase para monitorear si los procesos estan corriendo, si alguno no lo está para al resto.
  * server.py: Implementacion de socket como server, devuelve una instancia de middleware al aceptar una conexión.
* processor:
  * main.py: Encargado de levantar la configuracion inicial y lanzar los controllers correspondientes.
  * common: carpeta donde se encuentran los distintos controladores y funcionalidades utiles.
    * download_controller.py: Instancia un nuevo proceso que se encarga de recibir las solicitudes enviadas por el server, descarga el repositorio, lo guarda y envia a la cola de que un nuevo repositorio esta disponible.
    * query_controller.py: Instancia un nuevo proceso que se encarga de recibir las solicitudes enviadas por el server, busca los repositorios en donde se deberá realizar la busqueda y los envia a la cola de repositorios para realizar el grep.
    * grep_files_controller.py: Instancia un nuevo proceso que se encarga de realizar el grep sobre los repositorios y enviar los resultados al server.
    * update_repositories_controller.py: Instancia un nuevo proceso que se encarga de actualizar los repositorios disponibles para realizar la busqueda.
    * monitor_controller.py: Instancia un nuevo proceso que se encarga de revisar la cantidad de elementos que hay en cada cola.
    * garbage_collector_controller.py: Instancia un nuevo proceso que se encarga de borrar los repositorios mas viejos.
    * lock.py: Instancia un lock para poder leer o escribir en un archivo desde distintos procesos.
    * util.py: Funcionalidades extras, como grep, git clone, lectura y escritura de archivos.
* server:
  * main.py: Encargado de levantar la configuracion inicial y lanzar los threads correspondientes.
  * common: carpeta donde se encuantran los distintos controladores.
    * download_controller.py: Instancia un nuevo proceso encargado de recibir peticiones de descargas del cliente y reenviarlas al procesador.
    * query_controller.py: Instancia un nuevo proceso encargado de recibir peticiones de busquedas del cliente, reenviarlas al procesador y esperar las respuestas de este para responderle al cliente.
    * grep_results_controller.py: Instancia un nuevo proceso encargado de recibir las respuestas del procesador y enviarlas a la cola de resultados correspondiente.
* client:
  * main.py:
    * branch master: Realiza muchas requests para probar concurrencia.
    * branch interactive: Es un pequeño cliente interactivo.

## 4- Cosas a mejorar

Las principales cosas a mejorar son:
* Cambiar el main del procesador para que sea configurable la cantidad de download_controller, query_controller y grep_results_controller que se deban instanciar.
* El lock para darle prioridad a la escritura del archivo ya que seran mucho menores en cantidad que las lecturas.
* El garbage collector ya que el sistema actual puede fallar ante mucha demanda de requests.