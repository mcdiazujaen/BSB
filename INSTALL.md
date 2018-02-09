## Dependencias

El prototipo usa Python 3 y algunos paquetes adicionales

```bash
$ sudo apt install python3
$ sudo apt install python3-pip
$ pip3 install flask
$ pip3 install scholarly
$ pip3 install elasticsearch
$ pip3 install networkx
```

## INSTALACIÓN

### Instalar extensión en Chrome

  1. Abrimos la pestaña de extensiones en *Más herramientas > Extensiones*

  2. Activamos el *modo desarrollador*

  3. Pulsamos sobre el botón *Cargar extensión descomprimida...*

  4. Seleccionamos la carpeta `hackathon-bsb/chrome-extension`

  5. ¡Listo!

### Instalación de bases de conocimiento (UMLS, Medline, CIE-10)

Para algunos de estos recursos en necesario disponer de una licencia, por lo que
deberá ser solicitada al proveedor de dicho recurso.

Los pasos para generar almacenar los recursos necesarios del sistema son:

1. Generar los ficheros de conceptos de cada base de conocimiento con una línea por concepto. Cada línea contiene el texto del concepto y el código o referencia asociada separado por punto y coma (;):
  
    1.1. **`UMLS_concept.txt`**. Ejemplo:

    ```
    Absceso nasal;C0264263
    ácido palmítico;C0030234
    ...
    Zygophyllum;C1026054
    Zygoptera;C1015377
    ```

    1.2. **`Medline.txt`**. Ejemplo:

    ```
    Abdomen hinchado;https://medlineplus.gov/spanish/ency/article/003122.htm
    Ablación endometrial;https://medlineplus.gov/spanish/ency/article/007632.htm
    ...
    Vulvodinia;https://medlineplus.gov/spanish/ency/article/007699.htm
    Xantoma;https://medlineplus.gov/spanish/ency/article/001447.htm
    ```

    1.3. **`CIE-10.txt`**. Ejemplo:

    ```
    Cólera;A00
    Shigelosis;A03
    ...
    Traumatismo de nervios craneales;S04
    Xerosis del cutis;L853
    ```
    1.4. **`relations.txt`**. Fichero con tripletas para el grafo.Ejemplo:

    ```
    C0000167;PAR_inverse_isa;C0582125
    C0000167;RO_has_component;C0202112
    ...
    C0000726;RN_part_of;C1760038
    C0000726;RO_analyzes;C0488570
    ```

2. Copiar los ficheros generados en la carpeta: `/flask/data`

### Instalación de librerías de NLTK

  1. Descargar de la página de Stanford (https://nlp.stanford.edu/software/tagger.shtml#Download) los datos necesarios para el analizador sintáctico en español.

    https://nlp.stanford.edu/software/stanford-postagger-full-2017-06-09.zip

  2. Decomprimir en la carpeta `/flask/nltk_analysis/stanford-postagger-full-2017-06-09/`

