'''
Importamos las librerías necesarias para realizar el algoritmo evolutivo.
- random: librería para generar números aleatorios, será útil al realizar la mutación y crear el rompecabezas.
- time: librería para medir el tiempo de ejecución y de esta manera optimizarlo al variar los parámetros del algoritmo evolutivo.
'''
import random
import time

def copiar_matriz(matriz_original):
    """
    Crea una copia profunda de una matriz de objetos Pieza.
    Entrada:
    - matriz_original (list): Matriz de objetos Pieza a copiar.
    Salida:
    - copia_matriz (list): Nueva matriz con copias independientes de las piezas.
    """
    n = len(matriz_original)
    m = len(matriz_original[0])
    copia_matriz = [[None for _ in range(m)] for _ in range(n)]
    
    for i in range(n):
        for j in range(m):
            pieza_original = matriz_original[i][j]
            copia_pieza = pieza_original.copiar()  # Usamos el método copiar de la clase Pieza.
            copia_pieza.posicion = [i + 1, j + 1]  # Ajustamos la posición de la pieza copiada.
            copia_matriz[i][j] = copia_pieza
    
    return copia_matriz

class PiezaNoValidaError(Exception):
    '''
    Definimos una excepción personalizada para indicar cuando una pieza no es válida.
    '''
    def __init__(self, mensaje):
        self.mensaje = mensaje
        super().__init__(self.mensaje)  # Llama al constructor de la clase base para manejar el mensaje
    
    def __str__(self):
        return f"PiezaNoValidaError: {self.mensaje}" # Regresa el mensaje de error

class Matriz:
    '''
    Definimos la clase Matriz, la cual nos permitirá crear una matriz de N x M con valores secuenciales o aleatorios.
    Esto nos será útil para crear los rompecabezas (solución y aleatorio).
    '''
    def __init__(self, renglon, columna, aleatorio = False):
        '''
        Constructor de la clase Matriz.
        Entrada: renglon (int) número de renglones del rompecabezas, columna (int) número de columnas del rompecabezas, aleatorio (bool) indica si se desea crear una matriz aleatoria.
        Salida: Una matriz de N x M con valores secuenciales o aleatorios.
        '''
        self.columnas = columna
        self.renglones = renglon
        if aleatorio:
            self.matriz = self.crea_matriz_aleatoria(renglon,columna) # Creamos una matriz aleatoria.
        else:
            self.matriz = self.crea_matriz(renglon, columna) # Creamos una matriz con valores secuenciales.

    def __str__(self):
        '''
        Imprime la matriz.
        Entrada: Ninguna.
        Salida: La matriz en forma de cadena de texto.
        '''
        if not self.matriz: # Si la matriz está vacía, regresamos un mensaje indicando que está vacía.
            return "Matriz vacía"
        
        max_ancho = max(len(str(num)) for fila in self.matriz for num in fila) # Encontrar el número más largo para alinear correctamente.
        
        linea = '+' + '-' * (self.columnas * (max_ancho + 3) - 1) + '+' # Crear la línea superior.
        
        resultado = [linea] # Construir la representación de la matriz.
        for fila in self.matriz:
            numeros = [str(num).rjust(max_ancho) for num in fila] # Formatear cada número con el ancho máximo encontrado.
            resultado.append('| ' + ' | '.join(numeros) + ' |')
            resultado.append(linea)
        
        return '\n'.join(resultado)

    def crea_matriz(self, renglon, columna):
        '''
        Crea una matriz de N x M con valores secuenciales.
        Entrada: renglon (int) número de renglones del rompecabezas, columna (int) número de columnas del rompecabezas.
        Salida: Una matriz de N x M con valores secuenciales.
        '''
        matriz = []
        valor = 1
        for _ in range(renglon):
            ren = [] # Crear un nuevo renglón.
            for _ in range(columna):
                ren.append(valor) # Agregar el valor al renglón.
                valor += 1 # Incrementar el valor para que sea secuencial.
            matriz.append(ren)
        return matriz
    
    def crea_matriz_aleatoria(self, renglon, columna):
        '''
        Crea una matriz de N x M con valores aleatorios.
        Entrada: renglon (int) número de renglones del rompecabezas, columna (int) número de columnas del rompecabezas.
        Salida: Una matriz de N x M con valores aleatorios.
        '''
        numbers = list(range(1, renglon*columna + 1)) # Crear lista con números secuenciales del tamaño del rompecabezas.
        random.shuffle(numbers) # Desordenar la lista, de esta forma creamos una secuencia aleatoria.
        
        matriz = []
        indice = 0
        for _ in range(renglon):
            row = [] # Crear un nuevo renglón.
            for _ in range(columna):
                row.append(numbers[indice]) # Agregar el número al renglón.
                indice += 1 # Incrementar el índice para obtener el siguiente número.
            matriz.append(row)
        return matriz
    
class Pieza:
    '''
    Definimos la clase Pieza, la cual nos permitirá crear las piezas del rompecabezas.
    '''
    def __init__(self, v_arriba=0, v_abajo=0, v_izquierda=0, v_derecha=0, id_pieza=0):
        '''
        Constructor de la clase Pieza.
        Entrada: v_arriba (int) valor del extremo superior, v_abajo (int) valor del extremo inferior, v_izquierda (int) valor del extremo izquierdo, v_derecha (int) valor del extremo derecho, id_pieza (int) identificador de la pieza. 
        Los valores permitidos de los extremos son 0 (borde plano), -1 (borde hacia adentro), 1 (borde hacia afuera) y 2 (control).
        Salida: Una pieza con los valores de los extremos, un diccionario con sus conexciones (vacías por el momento) y su identificador.
        '''
        valores = [v_arriba, v_abajo, v_izquierda, v_derecha]
        valores_permitidos = {0, -1, 1, 2}
        
        if not all(v in valores_permitidos for v in valores): # Si la pieza no se puede crear correctamente.
            raise PiezaNoValidaError(
                f"Los valores {valores} no son válidos. Solo se permiten 0, -1, 1 o 2."
            )
            
        valores_no_cero = sum(1 for v in valores if v != 0)
        if valores_no_cero < 2: # Si la pieza no tiene al menos dos valores diferentes de cero (no puede haber una pieza con tres bordes planos).
            raise PiezaNoValidaError(
                f"La pieza debe tener al menos dos valores diferentes de cero. Valores actuales: {valores}"
            )
        
        # arriba, abajo, izquierda y derecha son las conexiones de la pieza, por el momento vacías.
        self.arriba = None
        self.abajo = None
        self.izquierda = None
        self.derecha = None
        self.extremos = {"izq":v_izquierda, "der": v_derecha, "arr": v_arriba, "aba": v_abajo}
        self.id = id_pieza
        self.posicion = None  # (fila, columna), por el momento vacía pues no pertenece a ningún rompecabezas.
    
    def copiar(self):
        """
        Crea una copia de la pieza actual, sin las conexiones.
        Entrada: Ninguna.
        Salida: Una nueva instancia de Pieza con los mismos atributos, excepto las conexiones.
        """
        return Pieza(
            v_arriba=self.extremos["arr"],
            v_abajo=self.extremos["aba"],
            v_izquierda=self.extremos["izq"],
            v_derecha=self.extremos["der"],
            id_pieza=self.id
        )
    
    def conectar_con(self, otra_pieza, direccion):
        '''
        Conecta una pieza con otra.
        Entrada: otra_pieza (Pieza) pieza con la que se desea conectar, dirección (str) dirección en la que se desea conectar la pieza (arriba, abajo, izquierda, derecha).
        Salida: Ninguna.
        '''
        if direccion == "arriba":
            self.arriba = otra_pieza
            if otra_pieza != None: # Si la otra pieza no es vacía, es decir, es una pieza y no un indicador de fuera de rango.
                otra_pieza.abajo = self
        elif direccion == "abajo":
            self.abajo = otra_pieza
            if otra_pieza != None: # Si la otra pieza no es vacía, es decir, es una pieza y no un indicador de fuera de rango.
                otra_pieza.arriba = self
        elif direccion == "izquierda":
            self.izquierda = otra_pieza
            if otra_pieza != None: # Si la otra pieza no es vacía, es decir, es una pieza y no un indicador de fuera de rango.
                otra_pieza.derecha = self
        elif direccion == "derecha":
            self.derecha = otra_pieza
            if otra_pieza != None: # Si la otra pieza no es vacía, es decir, es una pieza y no un indicador de fuera de rango.
                otra_pieza.izquierda = self
    
    def __str__(self):
        '''
        Imprime el contenido de la pieza.
        Entrada: Ninguna.
        Salida: La pieza en forma de cadena de texto.
        '''
        return f"Pieza {self.id} ({self.posicion}) -> {self.extremos}"

class Rompecabezas:
    '''
    Definimos la clase Rompecabezas, la cual nos permitirá realizar el algoritmo evolutivo para resolver el rompecabezas.
    '''
    def __init__(self, n, m, poblacion=1, ratio_mut=1):
        '''
        Constructor de la clase Rompecabezas, crea un rompecabezas solución a partir de una matriz secuencial y luego utiliza el algoritmo evolutivo para resolverlo. 
        Entrada: n (int) número de renglones del rompecabezas, m (int) número de columnas del rompecabezas.
        Salida: Un rompecabezas resuelto y visualizado.
        '''
        self.n = n
        self.m = m
        self.matriz_solucion = Matriz(n, m).matriz # Crear una matriz secuencial para el rompecabezas solución.
        self.tiempo_inicio = time.time() # Iniciar el contador de tiempo para optimizar parámetros.
        self.matriz_final = self.algoritmo_evolutivo(n, m, self.matriz_solucion, poblacion, ratio_mut) # Resolver el rompecabezas, a partir de la matriz solución y los parámetros de población y ratio de mutación.
        self.visualizar_rompecabezas(self.matriz_final) # Proyectar el rompecabezas resuelto.
        print(f"Tiempo Total: {time.time() - self.tiempo_inicio} segundos.") # Mostrar el tiempo total de ejecución.
    
    def crear_grafo_solucion(self, matriz_ids):
        """
        Crea un grafo solución a partir de una matriz de identificadores.
        Entrada: matriz_ids (matriz) matriz de identificadores de las piezas.
        Salida: lista de piezas y matriz de piezas.
        """
        n = len(matriz_ids)
        m = len(matriz_ids[0])
        piezas = {}
        matriz_piezas = [[None for _ in range(m)] for _ in range(n)]
        
        # Primera pasada: crear todas las piezas.
        for i in range(n):
            for j in range(m):
                # Determinar valores de los extremos.
                arriba = 0 if i == 0 else 2 # Si es la primera fila, el extremo superior es 0 (borde liso arriba), de lo contrario es 2 (control).
                abajo = 0 if i == n-1 else 2 # Si es la última fila, el extremo inferior es 0 (borde liso abajo), de lo contrario es 2 (control).
                izquierda = 0 if j == 0 else 2 # Si es la primera columna, el extremo izquierdo es 0 (borde liso izquierdo), de lo contrario es 2 (control).
                derecha = 0 if j == m-1 else 2 # Si es la última columna, el extremo derecho es 0 (borde liso derecho), de lo contrario es 2 (control).
                
                id_pieza = matriz_ids[i][j] # Obtener la posición matricial de la pieza.
                pieza = Pieza(arriba, abajo, izquierda, derecha, id_pieza)
                pieza.posicion = [i+1, j+1] # Asignar la posición matricial de la pieza para recordar dónde está en la solución.
                
                piezas[id_pieza] = pieza # Guardar la pieza en un diccionario por identificador.
                matriz_piezas[i][j] = pieza # Guardar la pieza en la matriz de piezas.
        
        # Segunda pasada: conectar piezas.
        for i in range(n):
            for j in range(m):
                pieza_actual = matriz_piezas[i][j]
                
                # Conectar con pieza de arriba si no es el borde superior.
                if i > 0:
                    pieza_actual.conectar_con(matriz_piezas[i-1][j], "arriba")
                
                # Conectar con pieza de la izquierda si no es el borde izquierdo.
                if j > 0:
                    pieza_actual.conectar_con(matriz_piezas[i][j-1], "izquierda")
        
        # Tercera pasada: asignar valores.
        for i in range(n):
            for j in range(m):
                pieza_actual = matriz_piezas[i][j]

                if pieza_actual.extremos['der'] == 2: # Si tiene un valor control, debemos asignar un valor aleatorio válido.
                    a = random.choice([-1,1])
                    pieza_actual.extremos['der'] = a
                    if a == 1: # Si el valor no es 0 (borde liso), debemos asignar el valor contrario a la pieza de la derecha.
                        matriz_piezas[i][j+1].extremos['izq'] = -1
                    else:
                         matriz_piezas[i][j+1].extremos['izq'] = 1

                if pieza_actual.extremos['izq'] == 2: # Si tiene un valor control, debemos asignar un valor aleatorio válido.
                    a = random.choice([-1,1])
                    pieza_actual.extremos['izq'] = a
                    if a == 1: # Si el valor no es 0 (borde liso), debemos asignar el valor contrario a la pieza de la izquierda.
                        matriz_piezas[i][j-1].extremos['der'] = -1
                    else:
                         matriz_piezas[i][j-1].extremos['der'] = 1
                        
                if pieza_actual.extremos['aba'] == 2: # Si tiene un valor control, debemos asignar un valor aleatorio válido.
                    a = random.choice([-1,1])
                    pieza_actual.extremos['aba'] = a
                    if a == 1: # Si el valor no es 0 (borde liso), debemos asignar el valor contrario a la pieza de abajo.
                        matriz_piezas[i+1][j].extremos['arr'] = -1
                    else:
                         matriz_piezas[i+1][j].extremos['arr'] = 1

                if pieza_actual.extremos['arr'] == 2: # Si tiene un valor control, debemos asignar un valor aleatorio válido.
                    a = random.choice([-1,1])
                    pieza_actual.extremos['arr'] = a
                    if a == 1: # Si el valor no es 0 (borde liso), debemos asignar el valor contrario a la pieza de arriba.
                        matriz_piezas[i-1][j].extremos['aba'] = -1
                    else:
                         matriz_piezas[i-1][j].extremos['aba'] = 1

        return list(piezas.values()), matriz_piezas
    
    def crear_grafo_aleatorio(self, matriz_ids, piezas_solucion):
        '''
        Crea un grafo aleatorio a partir de una matriz de identificadores aleatorios y las piezas solución.
        Entrada: matriz_ids (matriz) matriz de identificadores de las piezas, piezas_solucion (lista) lista de piezas solución.
        Salida: matriz de piezas.
        '''
        n = len(matriz_ids)
        m = len(matriz_ids[0])
        piezas = {}
        matriz_piezas = [[None for _ in range(m)] for _ in range(n)] # Crear matriz de piezas vacía.
        
        # Crear un diccionario de piezas solución por identificador.
        piezas_por_id = {pieza.id: pieza.copiar() for pieza in piezas_solucion}
        
        # Colocar las piezas según la matriz de identificadores aletorios.
        for i in range(n):
            for j in range(m):
                id_pieza = matriz_ids[i][j] # Obtenemos el identificador aleatorio de la pieza.
                pieza = piezas_por_id[id_pieza] # Obtenemos la pieza asociada a ese identificador.
                pieza.posicion = [i+1, j+1] # Indicamos su posición en la matriz.
                # Limpiamos las conexiones de la pieza.
                pieza.arriba = None
                pieza.abajo = None
                pieza.izquierda = None
                pieza.derecha = None
                
                piezas[id_pieza] = pieza
                matriz_piezas[i][j] = pieza # La agregamos a la matriz de piezas aleatorias.
        
        # Conectar las piezas según la nueva disposición.
        for i in range(n):
            for j in range(m):
                pieza_actual = matriz_piezas[i][j]
                
                if i > 0: # Conectar con pieza de arriba.
                    pieza_actual.conectar_con(matriz_piezas[i-1][j], "arriba")
                
                if j > 0: # Conectar con pieza de la izquierda.
                    pieza_actual.conectar_con(matriz_piezas[i][j-1], "izquierda")
        
        return matriz_piezas
    
    def verificar_conexiones(self, matriz_piezas):
        '''
        Verifica las conexiones de las piezas en la matriz.
        Entrada: matriz_piezas (matriz) matriz de piezas.
        Salida: lista de errores de conexión.
        '''
        n = len(matriz_piezas)
        m = len(matriz_piezas[0])
        conexiones_incorrectas = []
        
        for i in range(n):
            for j in range(m):
                pieza = matriz_piezas[i][j]
                
                # Verificar conexión superior
                if i > 0:
                    pieza_arriba = matriz_piezas[i-1][j]
                    if pieza.extremos["arr"] + pieza_arriba.extremos["aba"] != 0 or (pieza_arriba.extremos["aba"] == 0 and pieza.extremos["arr"] == 0):
                        conexiones_incorrectas.append(
                            f"Conexión incorrecta entre {pieza.id} y {pieza_arriba.id} (arriba)" # Indicar entre que piezas hay un error.
                        )
                
                # Verificar conexión izquierda
                if j > 0:
                    pieza_izq = matriz_piezas[i][j-1]
                    if pieza.extremos["izq"] + pieza_izq.extremos["der"] != 0 or (pieza_izq.extremos["der"] == 0 and pieza.extremos["izq"] == 0):
                        conexiones_incorrectas.append(
                            f"Conexión incorrecta entre {pieza.id} y {pieza_izq.id} (izquierda)" # Indicar entre que piezas hay un error.
                        )
        
        return conexiones_incorrectas
    
    def visualizar_rompecabezas(self, matriz_piezas, mostrar_errores=True):
        """
        Visualiza la matriz de piezas (rompecabezas) y sus conexiones, opcionalmente mostrando errores si los hay.
        Entrada: matriz_piezas (matriz) matriz de piezas, mostrar_errores (bool) indica si se deben mostrar los errores de conexión.
        """
        n = len(matriz_piezas)
        m = len(matriz_piezas[0])
        
        print("\nRompecabezas:")
        print("-" * (m * 20))
        
        for i in range(n):
            # Primera línea: extrremos superiores de las piezas.
            for j in range(m):
                print(f"      {matriz_piezas[i][j].extremos['arr']}      ", end="")
            print()
            
            # Segunda línea: extremos izquierdos y derechos de las piezas, junto con el identificador de la pieza.
            for j in range(m):
                print(f"{matriz_piezas[i][j].extremos['izq']}  ({matriz_piezas[i][j].id:2d})  {matriz_piezas[i][j].extremos['der']}", end=" ")
            print()
            
            # Tercera línea: extremos inferiores de las piezas
            for j in range(m):
                print(f"      {matriz_piezas[i][j].extremos['aba']}      ", end="")
            print()
            print("-" * (m * 20))
        
        if mostrar_errores: # Si queremos mostrar los errores.
            errores = self.verificar_conexiones(matriz_piezas)
            if errores:
                print("\nConexiones incorrectas:")
                for error in errores:
                    print(f"- {error}")
            else:
                print("\nTodas las conexiones son correctas!")

    def fitness(self, matriz_piezas):
        '''
        Calcula el fitness de una matriz de piezas, esto se realiza observando que tan cercano está el rompecabezas de estar resuelto.
        Entrada: matriz_piezas (matriz) matriz de piezas.
        Salida: contador_fit (int) valor de la función fitness de la matriz de piezas.
        '''
        contador_fit = 0 
        n=len(matriz_piezas)
        m=len(matriz_piezas[0])
        for i in range(n):
            for j in range(m):
                pieza_actual = matriz_piezas[i][j]
                
                # Los bordes tienen que ser 0.
                if i == 0 and pieza_actual.extremos['arr'] != 0:
                        contador_fit += 1
                if i == n-1 and pieza_actual.extremos['aba'] != 0:
                    contador_fit += 1
                if j == 0 and pieza_actual.extremos['izq'] != 0:
                        contador_fit += 1
                if j == m-1 and pieza_actual.extremos['der'] != 0:
                        contador_fit += 1

                # Verificar conexión superior.
                if i > 0:
                    pieza_arriba = matriz_piezas[i-1][j]
                    if pieza_actual.extremos["arr"] + pieza_arriba.extremos["aba"] != 0 or (pieza_arriba.extremos["aba"] == 0 and pieza_actual.extremos["arr"] == 0):
                        contador_fit += 1
                
                # Verificar conexión izquierda.
                if j > 0:
                    pieza_izq = matriz_piezas[i][j-1]
                    if pieza_actual.extremos["izq"] + pieza_izq.extremos["der"] != 0 or (pieza_izq.extremos["der"] == 0 and pieza_actual.extremos["izq"] == 0):
                        contador_fit += 1

                # Si la pieza no está en la posición correcta.
                if pieza_actual.id != (pieza_actual.posicion[0]-1)*m + pieza_actual.posicion[1]:
                    contador_fit += 4 

        return contador_fit

    def mutacion(self, matriz_original):
        '''
        Realiza una mutación en la matriz de piezas, intercambiando dos piezas aleatorias.
        Entrada: matriz_original (matriz) matriz de piezas original.
        Salida: matriz_piezas (matriz) matriz de piezas mutada.
        '''
        matriz_piezas = copiar_matriz(matriz_original) # Realizamos una copia de la matriz para no modificar la original.
        n = len(matriz_piezas)
        m = len(matriz_piezas[0])

        # Seleccionamos dos piezas aleatorias a través de índices aleatorios.
        i = random.randint(0,n-1) 
        j = random.randint(0,m-1)
        h = random.randint(0,n-1)
        k = random.randint(0,m-1)
        # Intercambiamos las piezas.
        aux = matriz_piezas[i][j]
        matriz_piezas[i][j] = matriz_piezas[h][k]
        matriz_piezas[h][k] = aux

        # Actualizamos las posiciones de las piezas.
        matriz_piezas[i][j].posicion[0] = i+1
        matriz_piezas[i][j].posicion[1] = j+1
        matriz_piezas[h][k].posicion[0] = h+1
        matriz_piezas[h][k].posicion[1] = k+1
        
        # Actualizamos las conexiones de las segunda pieza intercambiada.
        if i>0: # Si no es el borde superior, la conectamos con la pieza de arriba, de otra forma con una vacía.
            matriz_piezas[i][j].conectar_con(matriz_piezas[i-1][j], 'arriba')
        else:
            matriz_piezas[i][j].conectar_con(None, 'arriba') 

        if i<n-1: # Si no es el borde inferior, la conectamos con la pieza de abajo, de otra forma con una vacía.
            matriz_piezas[i][j].conectar_con(matriz_piezas[i+1][j], 'abajo')
        else:
            matriz_piezas[i][j].conectar_con(None, 'abajo')

        if j>0: # Si no es el borde izquierdo, la conectamos con la pieza de la izquierda, de otra forma con una vacía.
            matriz_piezas[i][j].conectar_con(matriz_piezas[i][j-1], 'izquierda')
        else:
            matriz_piezas[i][j].conectar_con(None, 'izquierda')

        if j<m-1: # Si no es el borde derecho, la conectamos con la pieza de la derecha, de otra forma con una vacía.
            matriz_piezas[i][j].conectar_con(matriz_piezas[i][j+1], 'derecha')
        else:
            matriz_piezas[i][j].conectar_con(None, 'derecha')

        # Actualizamos las conexiones de las primera pieza intercambiada.
        if h>0: # Si no es el borde superior, la conectamos con la pieza de arriba, de otra forma con una vacía.
            matriz_piezas[h][k].conectar_con(matriz_piezas[h-1][k], 'arriba')
        else:
            matriz_piezas[h][k].conectar_con(None, 'arriba')

        if h<n-1: # Si no es el borde inferior, la conectamos con la pieza de abajo, de otra forma con una vacía.
            matriz_piezas[h][k].conectar_con(matriz_piezas[h+1][k], 'abajo')
        else:
            matriz_piezas[h][k].conectar_con(None, 'abajo')

        if k > 0: # Si no es el borde izquierdo, la conectamos con la pieza de la izquierda, de otra forma con una vacía.
            matriz_piezas[h][k].conectar_con(matriz_piezas[h][k-1], 'izquierda')
        else:
            matriz_piezas[h][k].conectar_con(None, 'izquierda')

        if k<m-1: # Si no es el borde derecho, la conectamos con la pieza de la derecha, de otra forma con una vacía.
            matriz_piezas[h][k].conectar_con(matriz_piezas[h][k+1], 'derecha')
        else:
            matriz_piezas[h][k].conectar_con(None, 'derecha')
        
        return matriz_piezas

    def algoritmo_evolutivo(self, num_n, num_m, matriz_sol, poblacion=1, ratio_mut=1):
        '''
        Realiza el algoritmo evolutivo para resolver el rompecabezas.
        Entrada: 
            num_n (int) número de renglones del rompecabezas, 
            num_m (int) número de columnas del rompecabezas, 
            matriz_sol (matriz) matriz solución del rompecabezas, 
            poblacion (int): tamaño de la población inicial, 
            ratio_mut (float): proporción de rompecabezas mutados en cada generación.
        Salida: matriz_piezas (matriz) matriz de piezas resueltas.
        '''
        piezas_solucion, matriz_solucion = self.crear_grafo_solucion(matriz_sol)
        min_fitness = (num_n*num_m)*4 + (num_n*num_m) + (num_n-1)*num_m + (num_m-1)*num_n # Iniciamos el valor de fitness mínimo con el máximo posible.
        arreglo_rompecabezas = []
        
        while min_fitness !=0: # Mientras no se haya resuelto el rompecabezas, es decir, no hemos minimizado el valor de la función fitness.
            arreglo_fitness = []
            if not arreglo_rompecabezas: # Solo se crea en la primera generación.
                for i in range(poblacion): # Creamos la población inicial, es decir, pob-número de rompecabezas con las piezas aleatorizadas.
                    matriz_aleatoria = Matriz(num_n, num_m, True).matriz
                    rompecabezas_aleatorio = self.crear_grafo_aleatorio(matriz_aleatoria, piezas_solucion)
                    arreglo_rompecabezas.append(rompecabezas_aleatorio) # Guardamos el rompecabezas aleatoria en el arreglo.
                    
            
            num_mut = max(1, int(poblacion * ratio_mut)) # Definimos el número de mutaciones, dependiendo del tamaño de la población.
            random_list = [random.randint(0, len(arreglo_rompecabezas)-1) for _ in range(num_mut)] # Creamos una lista de índices aleatorios para mutar esos rompecabezas.
            
            for num in random_list:
                arreglo_rompecabezas.append(self.mutacion(arreglo_rompecabezas[num])) # Mutamos los rompecabezas y los añadimos a la población.
            
            for i in range(len(arreglo_rompecabezas)):
                arreglo_fitness.append(self.fitness(arreglo_rompecabezas[i])) # Calculamos el valor de la función fitness para cada rompecabezas y lo guardamos.
            
            indices_peores = obtener_indices_peores(arreglo_fitness, num_mut) # Obtenemos los índices de los peores rompecabezas según la función fitness.
            for indice in sorted(indices_peores, reverse=True):  # Eliminar de mayor a menor para no afectar los índices, es decir, nos quedamos con los mejores rompecabezas.
                arreglo_rompecabezas.pop(indice)
                arreglo_fitness.pop(indice)
            
            min_fitness = min(arreglo_fitness) # Obtenemos el valor mínimo de la función fitness de los rompecabezas de la población.
            indice = arreglo_fitness.index(min_fitness) # Obtenemos el rompecabezas con valor de función fitness mínimo.
            print(min_fitness) # Lo imprimimos para ver el avance hacia una solución.
        
        return arreglo_rompecabezas[indice] # Si el ciclo se termina, regresamos el rompecabezas resuelto.

def obtener_indices_peores(lista_fitness, num_mut):
    '''
    Obtiene los índices de los peores valores de fitness de nuestra lista de romepcabezas.
    Obtenemos los num_mut peores valores de fitness para que la población de la siguiente generación tenga el mismo tamaño.
    Entrada: lista_fitness (lista) lista de valores de fitness, num_mut (int) número de mutaciones.
    Salida: indices_peores (lista) lista de índices de los peores valores de fitness.
    '''

   # Crear lista de tuplas (valor, índice)
    valores_indices = [(valor, i) for i, valor in enumerate(lista_fitness)]
    
    # Ordenar por valor de fitness (mayor a menor)
    valores_indices.sort(reverse=True)
    
    # Tomar los primeros num_mut índices
    indices_peores = [i for _, i in valores_indices[:num_mut]]
    
    return indices_peores

class Optimizar:
    '''
    Clase que crea un objeto Optimizar para optimizar los parámetros de población y ratio de mutación en el algoritmo evolutivo.
    '''
    def __init__(self, n, m):
        """
        Inicializa el objeto Optimizar con las dimensiones del rompecabezas.
        Entrada:
        - n (int): Número de renglones.
        - m (int): Número de columnas.
        """
        self.n = n
        self.m = m
        self.matriz_solucion = Matriz(n, m).matriz  # Matriz solución base.
    
    def optimizar_parametros(self, generaciones=10):
        """
        Optimiza los parámetros de población y ratio de mutación utilizando un algoritmo evolutivo.
        Entrada:
        - generaciones (int): Número de generaciones para ejecutar el algoritmo.
        Salida:
        - (dict): Diccionario con los parámetros óptimos y el tiempo que tardó el mejor conjunto.
        """
        mejor_tiempo = float('inf') # Asignamos el mejor tiempo como el máximo posible.
        mejores_parametros = None

        # Inicializamos los parámetros como una lista de tuplas (población, ratio_mutación). 
        # Se crean aleatoriamente para probar diferentes combinaciones.
        poblacion_parametros = [
            {"poblacion": random.randint(1, 50), "ratio_mutacion": random.uniform(0.1, 1)}
            for _ in range(10)
        ]

        # Realizamos el algorimto evolutivo tantas veces como generaciones deseamos.
        for generacion in range(generaciones):
            tiempos_poblacion = [] 
            
            # Evaluar el tiempo de ejecución para cada conjunto de parámetros.
            for params in poblacion_parametros:
                print(f"[Generación {generacion + 1}] Probando parámetros: "
                      f"Población={params['poblacion']}, Ratio Mutación={params['ratio_mutacion']:.2f}")
                
                rompecabezas = Rompecabezas(self.n, self.m)
                inicio = time.time()
                rompecabezas.algoritmo_evolutivo(
                    self.n, self.m, self.matriz_solucion,
                    poblacion=params["poblacion"],
                    ratio_mut=params["ratio_mutacion"]
                )
                tiempo = time.time() - inicio
                tiempos_poblacion.append((tiempo, params))
                
                if tiempo < mejor_tiempo: # Si es el mejor tiempo hasta ahora, guardamos el tiempo y los parámetros que lo crearon.
                    mejor_tiempo = tiempo
                    mejores_parametros = params

            # Selección: Retener los mejores parámetros.
            tiempos_poblacion.sort(key=lambda x: x[0])  # Ordenar por tiempo.
            poblacion_parametros = [item[1] for item in tiempos_poblacion[:len(poblacion_parametros) // 2]] # Nos quedamos con la mitad de los mejores parámetros según su tiempo.

            # Mutación y cruce: crear nuevos parámetros.
            nuevos_parametros = []
            for _ in range(10 - len(poblacion_parametros)): # Creamos la otra mitad de parámetros.
                padre = random.choice(poblacion_parametros)
                nuevo_parametro = {
                    "poblacion": max(1, padre["poblacion"] + random.randint(-5, 5)), # Aseguramos que la población sea al menos 1, agregamos una variación.
                    "ratio_mutacion": max(0.1, min(1, max(0.1, padre["ratio_mutacion"] + random.uniform(-0.2, 0.2)))) # Aseguramos que el ratio de mutación esté entre 0.1 y 1, agregamos una variación.
                }
                nuevos_parametros.append(nuevo_parametro)
            
            poblacion_parametros.extend(nuevos_parametros) # Agregamos los nuevos parámetros a la población.
            print(f"[Generación {generacion + 1}] Mejor tiempo: {mejor_tiempo:.2f} segundos")
        
        print("\nOptimización completada.")
        print(f"Mejores parámetros encontrados: {mejores_parametros} con tiempo {mejor_tiempo:.2f} segundos")
        return mejores_parametros["poblacion"], mejores_parametros["ratio_mutacion"]

def main():
    # Dimensiones del rompecabezas.
    n, m = 20, 10
    #Argumentos por si no queremos optimizar.
    poblacion_optima = 1
    ratio_mutacion_optimo = 1
    
    '''
    # Crear una instancia de Optimizar con las dimensiones del rompecabezas. Se recomienda usar menos de 200 piezas.
    optimizador = Optimizar(n, m)
    
    # Ejecutar la optimización.
    poblacion_optima, ratio_mutacion_optimo = optimizador.optimizar_parametros(generaciones=10)
    
    # Imprimir los resultados óptimos.
    print("\nParámetros óptimos encontrados:")
    print(f"Población: {poblacion_optima}")
    print(f"Ratio de mutación: {ratio_mutacion_optimo:.2f}")
    '''
    
    # Crear un rompecabezas con los parámetros óptimos, para que lo solucione lo más rápido posible.
    Rompecabezas(n, m, poblacion_optima, ratio_mutacion_optimo) 
    print(f"parámetros: \n población: {poblacion_optima} \n ratio de mutación: {ratio_mutacion_optimo}")
    
if __name__ == "__main__":
    main()