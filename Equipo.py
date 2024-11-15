'''
SI LAS PIEZAS EMPATAN, CHECAS LA IMAGEN (ESTO ES -1 Y 1 LUEGO CHECAS POR ID SOLO SI ESTA CONDICION OCURRE)
'''
import random
from copy import deepcopy
import time

# Definimos una excepción personalizada
class PiezaNoValidaError(Exception):
    pass
    

class Matriz:
    def __init__(self, renglon, columna, aleatorio = False):
        self.columnas = columna
        self.renglones = renglon
        if aleatorio:
            self.matriz = self.crea_matriz_aleatoria(renglon,columna)
        else:
            self.matriz = self.crea_matriz(renglon, columna)

    def __str__(self):
        if not self.matriz:
            return "Matriz vacía"
        
        # Encontrar el número más largo para alinear correctamente
        max_width = max(len(str(num)) for fila in self.matriz for num in fila)
        
        # Crear la línea superior
        linea = '+' + '-' * (self.columnas * (max_width + 3) - 1) + '+'
        
        # Construir la representación de la matriz
        result = [linea]
        for fila in self.matriz:
            # Formatear cada número con el ancho máximo encontrado
            numeros = [str(num).rjust(max_width) for num in fila]
            result.append('| ' + ' | '.join(numeros) + ' |')
            result.append(linea)
        
        return '\n'.join(result)

    def crea_matriz(self,renglon, columna):
        matrix = []
        value = 1
        for _ in range(renglon):
            row = []
            for _ in range(columna):
                row.append(value)
                value += 1
            matrix.append(row)
        return matrix
    
    def crea_matriz_aleatoria(self,renglon, columna):
        # Crear lista con números secuenciales
        numbers = list(range(1, renglon*columna + 1))
        # Desordenar la lista
        random.shuffle(numbers)
        
        # Crear la matriz
        matrix = []
        index = 0
        for _ in range(renglon):
            row = []
            for _ in range(columna):
                row.append(numbers[index])
                index += 1
            matrix.append(row)
        return matrix

class Pieza:
    def __init__(self, v_arriba=0, v_abajo=0, v_izquierda=0, v_derecha=0, id_pieza=0):
        valores = [v_arriba, v_abajo, v_izquierda, v_derecha]
        valores_permitidos = {0, -1, 1, 2}
        
        if not all(v in valores_permitidos for v in valores):
            raise PiezaNoValidaError("Los valores solo pueden ser 0, -1, 1 o 2")
            
        valores_no_cero = sum(1 for v in valores if v != 0)
        
        if valores_no_cero < 2:
            raise PiezaNoValidaError("La pieza debe tener al menos dos valores diferentes de cero")
        
        self.arriba = None
        self.abajo = None
        self.izquierda = None
        self.derecha = None
        self.extremos = {"izq":v_izquierda, "der": v_derecha, "arr": v_arriba, "aba": v_abajo}
        self.id = id_pieza
        self.posicion = None  # (fila, columna)
    
    def conectar_con(self, otra_pieza, direccion):
        """Conecta esta pieza con otra independientemente de los valores"""
        if direccion == "arriba":
            self.arriba = otra_pieza
            if otra_pieza != None:
                otra_pieza.abajo = self
        elif direccion == "abajo":
            self.abajo = otra_pieza
            if otra_pieza != None:
                otra_pieza.arriba = self
        elif direccion == "izquierda":
            self.izquierda = otra_pieza
            if otra_pieza != None:
                otra_pieza.derecha = self
        elif direccion == "derecha":
            self.derecha = otra_pieza
            if otra_pieza != None:
                otra_pieza.izquierda = self
    
    def __str__(self):
        return f"Pieza {self.id} ({self.posicion}) -> {self.extremos}"

def crear_grafo_solucion(matriz_ids):
    """
    Crea un grafo solución a partir de una matriz de IDs.
    """
    n = len(matriz_ids)
    m = len(matriz_ids[0])
    piezas = {}
    matriz_piezas = [[None for _ in range(m)] for _ in range(n)]
    
    # Primera pasada: crear todas las piezas
    for i in range(n):
        for j in range(m):
            # Determinar valores de los extremos
            arriba = 0 if i == 0 else 2
            abajo = 0 if i == n-1 else 2
            izquierda = 0 if j == 0 else 2
            derecha = 0 if j == m-1 else 2
            
            id_pieza = matriz_ids[i][j]
            pieza = Pieza(arriba, abajo, izquierda, derecha, id_pieza)
            pieza.posicion = [i+1, j+1]
            
            piezas[id_pieza] = pieza
            matriz_piezas[i][j] = pieza
    
    # Segunda pasada: conectar piezas
    for i in range(n):
        for j in range(m):
            pieza_actual = matriz_piezas[i][j]
            
            # Conectar con pieza de arriba
            if i > 0:
                pieza_actual.conectar_con(matriz_piezas[i-1][j], "arriba")
            
            # Conectar con pieza de la izquierda
            if j > 0:
                pieza_actual.conectar_con(matriz_piezas[i][j-1], "izquierda")
    
    # Tercera pasada: asignar valores
    for i in range(n):
        for j in range(m):
            pieza_actual = matriz_piezas[i][j]

            if pieza_actual.extremos['der'] == 2:
                a = random.choice([-1,1])
                pieza_actual.extremos['der'] = a
                if a == 1:
                    matriz_piezas[i][j+1].extremos['izq'] = -1
                else:
                     matriz_piezas[i][j+1].extremos['izq'] = 1

            if pieza_actual.extremos['izq'] == 2:
                a = random.choice([-1,1])
                pieza_actual.extremos['izq'] = a
                if a == 1:
                    matriz_piezas[i][j-1].extremos['der'] = -1
                else:
                     matriz_piezas[i][j-1].extremos['der'] = 1
                    
            if pieza_actual.extremos['aba'] == 2:
                a = random.choice([-1,1])
                pieza_actual.extremos['aba'] = a
                if a == 1:
                    matriz_piezas[i+1][j].extremos['arr'] = -1
                else:
                     matriz_piezas[i+1][j].extremos['arr'] = 1

            if pieza_actual.extremos['arr'] == 2:
                a = random.choice([-1,1])
                pieza_actual.extremos['arr'] = a
                if a == 1:
                    matriz_piezas[i-1][j].extremos['aba'] = -1
                else:
                     matriz_piezas[i-1][j].extremos['aba'] = 1
  

    return list(piezas.values()), matriz_piezas


def crear_grafo_random(matriz_ids, piezas_solucion):
    """
    Crea un grafo reorganizando las piezas de la solución según la matriz_ids dada.
    Mantiene los valores de los extremos de cada pieza pero las coloca en nuevas posiciones.
    """
    n = len(matriz_ids)
    m = len(matriz_ids[0])
    piezas = {}
    matriz_piezas = [[None for _ in range(m)] for _ in range(n)]
    
    # Crear un diccionario de piezas solución por ID
    piezas_por_id = {pieza.id: deepcopy(pieza) for pieza in piezas_solucion}
    
    # Colocar las piezas según la matriz_ids
    for i in range(n):
        for j in range(m):
            id_pieza = matriz_ids[i][j]
            pieza = piezas_por_id[id_pieza]
            pieza.posicion = [i+1, j+1]
            pieza.arriba = None
            pieza.abajo = None
            pieza.izquierda = None
            pieza.derecha = None
            
            piezas[id_pieza] = pieza
            matriz_piezas[i][j] = pieza
    
    # Conectar las piezas según la nueva disposición
    for i in range(n):
        for j in range(m):
            pieza_actual = matriz_piezas[i][j]
            
            if i > 0:  # Conectar con pieza de arriba
                pieza_actual.conectar_con(matriz_piezas[i-1][j], "arriba")
            
            if j > 0:  # Conectar con pieza de la izquierda
                pieza_actual.conectar_con(matriz_piezas[i][j-1], "izquierda")
    
    return matriz_piezas

def verificar_conexiones(matriz_piezas):
    """
    Verifica qué conexiones entre piezas son correctas e incorrectas
    """
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
                        f"Conexión incorrecta entre {pieza.id} y {pieza_arriba.id} (arriba)"
                    )
            
            # Verificar conexión izquierda
            if j > 0:
                pieza_izq = matriz_piezas[i][j-1]
                if pieza.extremos["izq"] + pieza_izq.extremos["der"] != 0 or (pieza_izq.extremos["der"] == 0 and pieza.extremos["izq"] == 0):
                    conexiones_incorrectas.append(
                        f"Conexión incorrecta entre {pieza.id} y {pieza_izq.id} (izquierda)"
                    )
    
    return conexiones_incorrectas

def visualizar_matriz(matriz_piezas, mostrar_errores=True):
    """
    Visualiza la matriz de piezas y sus conexiones, opcionalmente mostrando errores
    """
    n = len(matriz_piezas)
    m = len(matriz_piezas[0])
    
    print("\nMatriz de Piezas:")
    print("-" * (m * 20))
    
    for i in range(n):
        # Primera línea: valores superiores
        for j in range(m):
            print(f"      {matriz_piezas[i][j].extremos['arr']}      ", end="")
        print()
        
        # Segunda línea: valores izquierda y derecha
        for j in range(m):
            print(f"{matriz_piezas[i][j].extremos['izq']}  ({matriz_piezas[i][j].id:2d})  {matriz_piezas[i][j].extremos['der']}", end=" ")
        print()
        
        # Tercera línea: valores inferiores
        for j in range(m):
            print(f"      {matriz_piezas[i][j].extremos['aba']}      ", end="")
        print()
        print("-" * (m * 20))
    
    if mostrar_errores:
        errores = verificar_conexiones(matriz_piezas)
        if errores:
            print("\nConexiones incorrectas:")
            for error in errores:
                print(f"- {error}")
        else:
            print("\nTodas las conexiones son correctas!")


'''
MUTACION: INTERCAMBIAR BLOQUE DE NXM DENTRO DE SI MISMA 
APAREAMIENTO:  INTERCAMBIAR BLOQUE DE NXM CON OTRA MATRIZ HACIA EL MISMO LUGAR
'''

class Rompecabezas:
    def __init__(self):
        pass

    def fitness(self, matriz_piezas):
        contador_fit = 0
        n=len(matriz_piezas)
        m=len(matriz_piezas[0])
        for i in range(n):
            for j in range(m):
                pieza_actual = matriz_piezas[i][j]
                
                # Los bordes tienen que ser 0
                if i == 0:
                    if pieza_actual.extremos['arr'] != 0:
                        contador_fit += 1
                if i==n-1:
                    if pieza_actual.extremos['aba'] != 0:
                        contador_fit += 1
                if j == 0:
                    if pieza_actual.extremos['izq'] != 0:
                        contador_fit += 1
                if j == m-1:
                    if pieza_actual.extremos['der'] != 0:
                        contador_fit += 1

                # Verificar conexión superior 
                # falta checar que la conexion con indices sea buena
                if i > 0:
                    pieza_arriba = matriz_piezas[i-1][j]
                    if pieza_actual.extremos["arr"] + pieza_arriba.extremos["aba"] != 0 or (pieza_arriba.extremos["aba"] == 0 and pieza_actual.extremos["arr"] == 0):
                        contador_fit += 1
                
                # Verificar conexión izquierda
                if j > 0:
                    pieza_izq = matriz_piezas[i][j-1]
                    if pieza_actual.extremos["izq"] + pieza_izq.extremos["der"] != 0 or (pieza_izq.extremos["der"] == 0 and pieza_actual.extremos["izq"] == 0):
                        contador_fit += 1

                if pieza_actual.id != (pieza_actual.posicion[0]-1)*m + pieza_actual.posicion[1]:
                    contador_fit += 4 # Modificar peso a futuro

        return contador_fit

    def mutacion(self, matriz_original):
        matriz_piezas = deepcopy(matriz_original)
        n = len(matriz_piezas)
        m = len(matriz_piezas[0])

        n_mut = random.randint(1,5)
        for _ in range(n_mut):
            i = random.randint(0,n-1)
            j = random.randint(0,m-1)
            h = random.randint(0,n-1)
            k = random.randint(0,m-1)
            aux = matriz_piezas[i][j]
            matriz_piezas[i][j] = matriz_piezas[h][k]
            matriz_piezas[h][k] = aux

            matriz_piezas[i][j].posicion[0] = i+1
            matriz_piezas[i][j].posicion[1] = j+1

            matriz_piezas[h][k].posicion[0] = h+1
            matriz_piezas[h][k].posicion[1] = k+1
            
            if i>0:
                matriz_piezas[i][j].conectar_con(matriz_piezas[i-1][j], 'arriba')
            else:
                matriz_piezas[i][j].conectar_con(None, 'arriba')

            if i<n-1:
                matriz_piezas[i][j].conectar_con(matriz_piezas[i+1][j], 'abajo')
            else:
                matriz_piezas[i][j].conectar_con(None, 'abajo')

            if j>0:
                matriz_piezas[i][j].conectar_con(matriz_piezas[i][j-1], 'izquierda')
            else:
                matriz_piezas[i][j].conectar_con(None, 'izquierda')

            if j<m-1:
                matriz_piezas[i][j].conectar_con(matriz_piezas[i][j+1], 'derecha')
            else:
                matriz_piezas[i][j].conectar_con(None, 'derecha')


            if h>0:
                matriz_piezas[h][k].conectar_con(matriz_piezas[h-1][k], 'arriba')
            else:
                matriz_piezas[h][k].conectar_con(None, 'arriba')

            if h<n-1:
                matriz_piezas[h][k].conectar_con(matriz_piezas[h+1][k], 'abajo')
            else:
                matriz_piezas[h][k].conectar_con(None, 'abajo')

            if k > 0:
                matriz_piezas[h][k].conectar_con(matriz_piezas[h][k-1], 'izquierda')
            else:
                matriz_piezas[h][k].conectar_con(None, 'izquierda')

            if k<m-1:
                matriz_piezas[h][k].conectar_con(matriz_piezas[h][k+1], 'derecha')
            else:
                matriz_piezas[h][k].conectar_con(None, 'derecha')
        
        return matriz_piezas

    def algoritmo_evolutivo(self, num_n, num_m, matriz_sol):
        piezas_solucion, matriz_solucion = crear_grafo_solucion(matriz_sol)
        min_fitness = num_m*num_n
        arreglo_matriz = []
        pob = 50
        while min_fitness !=0:
            arreglo_fitness = []
            if not arreglo_matriz:
                for i in range(pob):
                    matriz_random = Matriz(num_n, num_m, True)
                    matriz_random = matriz_random.matriz
                    matriz_random = crear_grafo_random(matriz_random, piezas_solucion)
                    arreglo_matriz.append(matriz_random)
            
            num_mut = random.randint(1,pob)
            random_list = [random.randint(0, pob-1) for _ in range(num_mut)]
            for num in random_list:
                arreglo_matriz.append(self.mutacion(arreglo_matriz[num]))
            
            for i in range(len(arreglo_matriz)):
                arreglo_fitness.append(self.fitness(arreglo_matriz[i]))
            
            indices_peores = obtener_indices_peores(arreglo_fitness, num_mut)

            for indice in sorted(indices_peores, reverse=True):  # Eliminar de mayor a menor para no afectar los índices
                arreglo_matriz.pop(indice)
                arreglo_fitness.pop(indice)
            
            min_fitness = min(arreglo_fitness)
            indice = arreglo_fitness.index(min_fitness)
            print(min_fitness)
        
        return arreglo_matriz[indice]

def obtener_indices_peores(lista_fitness, num_mut):
    
   # Crear lista de tuplas (valor, índice)
    valores_indices = [(valor, i) for i, valor in enumerate(lista_fitness)]
    
    # Ordenar por valor de fitness (mayor a menor)
    valores_indices.sort(reverse=True)
    
    # Tomar los primeros num_mut índices
    indices_peores = [i for _, i in valores_indices[:num_mut]]
    
    return indices_peores


def main():
    n = 10
    m = 8
    matriz_o = Matriz(n,m)
    matriz_o = matriz_o.matriz

    rompe = Rompecabezas()
    start_time = time.time()
    matriz_final = rompe.algoritmo_evolutivo(n,m, matriz_o)
    visualizar_matriz(matriz_final)
    print(f"Tiempo Total: {time.time()-start_time}")

# Ejemplo de uso
if __name__ == "__main__":
    main()