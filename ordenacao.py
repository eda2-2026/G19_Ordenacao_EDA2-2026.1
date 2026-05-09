def counting_sort(arr, chave):

    if not arr:
        return []

    max_val = max(arr, key=lambda x: x[chave])[chave]

    count = [0] * (max_val + 1)
    output = [None] * len(arr)

    for item in arr:
        valor = item[chave]
        count[valor] += 1

    for i in range(1, len(count)):
        count[i] += count[i - 1]

    for i in range(len(arr) - 1, -1, -1):
        item = arr[i]
        valor = item[chave]
        output[count[valor] - 1] = item
        count[valor] -= 1

    return output

def counting_sort_por_digito(arr, chave, exp):

    n = len(arr)
    output = [None] * n
    count = [0] * 10

    for i in range(n):
        index = arr[i][chave] // exp
        count[index % 10] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        index = arr[i][chave] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1

    for i in range(n):
        arr[i] = output[i]

def radix_sort(arr, chave):

    if not arr:
        return arr

    max_val = max(arr, key=lambda x: x[chave])[chave]

    exp = 1
    while max_val // exp > 0:
        counting_sort_por_digito(arr, chave, exp)
        exp *= 10
        
    return arr

def merge_sort(arr, chave):

    if len(arr) <= 1:
        return arr
        
    meio = len(arr) // 2
    esquerda = merge_sort(arr[:meio], chave)
    direita = merge_sort(arr[meio:], chave)
    
    return merge(esquerda, direita, chave)

def merge(esquerda, direita, chave):
    resultado = []
    i = j = 0
    
    while i < len(esquerda) and j < len(direita):

        valor_esq = str(esquerda[i].get(chave, '')).lower()
        valor_dir = str(direita[j].get(chave, '')).lower()
        
        if valor_esq <= valor_dir:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1

    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    
    return resultado