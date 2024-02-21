# Notas previas
Este repositorio se trata de un fork del repositorio original de YOLOv5, pero se le ha añadido una carpetra llamada DEE_addition que es donde están todas las cosas que se han hecho para el DEE.
Dentro de la carpeta DEE_addition estan tanto los ficheros para descargar conjuntos de datos y para realizar la detección, como el fichero de la apliación de carácter demostrativo que se ha desarrollado.

En el siguiente apartado se define un Tutorial que explica como crear el entrono de trabajo, como descargar los conjuntos de datos, como realizar el entrenamiento y como realizar la detección.

En cuanto a la aplicación de carácter demostrativo, se han hecho dos vídeos, uno donde se hace una demo de como funciona la aplicación y otro explicando el código. Los vídeos son los siguientes:
1. Vídeo demo del funcionamiento de la aplicación: [![DroneEngineeringEcosystem Badge](https://img.shields.io/badge/DEE-demo_app-pink.svg)](https://www.youtube.com/watch?v=Y6EWHlZRF-g)
2. Vídeo explicando el código de la aplicación:  [![DroneEngineeringEcosystem Badge](https://img.shields.io/badge/DEE-code_app-pink.svg)](https://www.youtube.com/watch?v=Svl8WfxM6Mw)

Para poner en funcionamiento la aplicación se requiere poner también en marcha un CameraService adaptado, que permite tomar imagenes de la webcam del portátil pero tambien de la picamera de una Raspberry Pi, e incluso reconocer objetos en el propio servicio de cámara. El repositorio con este servicio de cámara adaptado es este:  [![DroneEngineeringEcosystem Badge](https://img.shields.io/badge/DEE-camera_service_for_object_recognition-blue.svg)](https://github.com/dronsEETAC/CameraServiceForObjectRecognition)


# Tutoriales
## Introducción a la detección de objetos con redes neuronales y yolov5
Este es el video tutorial: [![DroneEngineeringEcosystem Badge](https://img.shields.io/badge/DEE-introduccion-pink.svg)](https://www.youtube.com/playlist?list=PLyAtSQhMsD4qWd33j4rxHd13iO_GUXK4N)

## Crear entorno, clonar repositorio y instalar requerimientos

1. Crear un entorno virtual con Python 3.8. 
Con el gestor de paquetes Conda de Anaconda, el entorno virtual se crearía con la siguiente línea en el Anaconda Prompt:
```bash
conda create -n yolov5 python=3.8
```

2. Una vez creado el entorno virtual, se tiene que activar. 
Con Conda se haría de la siguiente manera también en el Anaconda Prompt:
```bash
conda activate yolov5
```

3. Ahora clonamos el repositorio de GitHub y instalamos los requerimientos dentro del entorno virtual. Con Conda se haría de la siguiente manera también en el Anaconda Prompt (tarda unos minutos en instalar todo):
```bash
git clone https://github.com/underwaterIker/yolov5
cd yolov5
pip install -r requirements.txt
```

## Descargar conjunto de datos

4. Ahora que ya hemos clonado el repositorio e instalado los requerimientos, podemos abrir el proyecto con un editor de texto como PyCharm, y debemos abrir el fichero que está dentro de la carpeta “DEE\_addition” que se llama:
```
main_dataset.py
```

5. Una vez abierto ese fichero, debemos bajar hasta llegar a partir de la línea 71, que tiene el siguiente comentario:
```
# Setting parameters
```

6. A partir de la línea 71, tenemos los parámetros que podemos configurar para descargar el dataset. El que nos interesa es el de la línea 72, con el nombre de variable:
```
objects_selected
```
En esta variable deberemos poner los objetos que queramos detectar. Los objetos disponibles para poder poner en esta lista se pueden encontrar en la página web de Open Images V7, que están en inglés.
Si, por ejemplo escogiéramos "Bottle" y "Apple", la variable debería quedar de la siguiente forma en el código:
```
objects_selected = ["Bottle", "Apple"]
```
Es importante escribir los objetos tal y como se muestra arriba: en inglés y con la primera letra en mayúsculas.

7. El otro parámetro es el que define cuantas imágenes se quieren descargar por cada objeto seleccionado, y tiene el nombre de variable:
```
images_per_class
```

8. Ya le podemos dar a ejecutar el fichero main_dataset.py, asegurándonos que hemos configurado el editor de texto para que use como Interpreter el entorno virtual que hemos creado al principio.
Este va a tardar unos minutos en completarse, y como resultado nos va a descargar el dataset dentro de la carpeta "datasets", que a su vez se encuentra dentro de la carpeta "DEE\_addition". De las tres carpetas que nos ha descargado, nos interesa la carpeta zip con el nombre:
```
YOLOv5Dataset.zip
```


## Entrenamiento

9. Ahora debemos abrir el siguiente link: [Google Colab link](https://colab.research.google.com/drive/176VhxxlNbgM_pbAI3EU_MrrYsrIyPGwb?usp=drive_link)

10. Lo primero de todo que debemos hacer es darle a "Archivo" y darle a "Guardar una copia en Drive", de esta manera podremos editar el documento y se van a guardar los cambios en nuestro Drive.

11. Lo siguiente que debemos hacer es asegurarnos que tenemos seleccionada la "T4 GPU" como entorno de ejecución. Para ello debemos ir a la pestaña "Entorno de ejecución" y darle a "Cambiar tipo de entorno de ejecución", y ahí podremos seleccionar la "T4 GPU" y darle a "Guardar".

12. A continuación, ejecutamos la primera celda de código, que clona el repositorio de GitHub e instala las dependencias.

13. Una vez hecho esto, debemos copiar la carpeta zip que se ha mencionado en el punto 8 "YOLOv5Dataset.zip" a fuera de la carpeta "yolov5", es decir, arrastrarla al lado de la carpeta "yolov5" para que no se meta dentro de esa carpeta.

14. Cuando la carpeta zip ya haya acabado de subirse, deberemos ejecutar la segunda celda de código, que es la que descomprime la carpeta que acabamos de subir.

15. Una vez tenemos la carpeta descomprimida, podemos ejecutar la tercera celda de código, que es la que realiza el entrenamiento. En ella están los parámetros configurables del entrenamiento, pero se pueden dejar por defecto.

16. Una vez finalice el entrenamiento, debemos ir a la carpeta "yolov5", abrir la carpeta "runs", abrir la carpeta "train", y dentro de esta carpeta abrir la última carpeta que se llamará "exp" seguido de un número, pues debemos abrir la que tenga el número más grande, que será la que pertenece al último entrenamiento realizado (si solo hay una carpeta llamada "exp" sin número, es esa carpeta en la que debemos entrar). Dentro de esta carpeta abrimos la carpeta "weights" y descargamos el archivo "best.pt", que es el archivo con los pesos y sesgos que ha dado como resultado el entrenamiento.


## Detección

17. Una vez descargado el archivo "best.pt", tenemos que volver a nuestro proyecto de "yolov5" y poner el archivo dentro de la carpeta "weights", que se encuentra dentro de la carpeta "DEE_addition". Deberemos asegurarnos de que nuestro archivo "best.pt" sea el único presente en esa carpeta, es decir, si hay otro archivo "best.pt" en la carpeta deberemos borrarlo y sustituirlo por nuestro archivo "best.pt".

18. Cuando tengamos el archivo "best.pt" dentro de la carpeta "weights" (que está dentro de la carpeta "DEE_addition"), deberemos abrir el fichero main_detection.py, que se encuentra también dentro de la carpeta "DEE_addition" y ejecutarlo. Este programa abrirá una ventana mostrando vídeo en directo desde nuestra webcam y detectando los objetos que hayamos especificado en el entrenamiento.
Para cerrar la ventana o parar la detección, pulsar la tecla "q" o darle al botón de parar ejecución de nuestro editor de texto, ya que si solo cerramos la ventana ésta se volverá a abrir y la ejecución no parará.
