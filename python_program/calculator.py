
while True:
    line = input("Digite números separados por espaço (ou 'sair' para encerrar): ")
    if line.strip().lower() in ('sair', 'exit', 'q', 'quit'):
        print('Encerrando calculadora.')
        break
    parts = line.replace(',', ' ').split()
    nums = []
    for p in parts:
        try:
            nums.append(float(p))
        except ValueError:
            print(f"Entrada inválida '{p}', ignorando.")
    if not nums:
        print('Nenhum número válido informado. Tente novamente.')
        continue

    sinal = input("Digite o sinal da operação (+, -, *, /): ")

    if sinal == "+":
        resultado = sum(nums)
        print("O resultado da soma é:", resultado)
    elif sinal == "-":
        a = nums[0]
        for n in nums[1:]:
            a = a - n
        print("O resultado da subtração é:", a)
    elif sinal == "*":
        a = 1
        for n in nums:
            a = a * n
        print("O resultado da multiplicação é:", a)
    elif sinal == "/":
        a = nums[0]
        erro = False
        for n in nums[1:]:
            if n == 0:
                print('Erro: divisão por zero detectada. Operação cancelada.')
                erro = True
                break
            a = a / n
        if not erro:
            print("O resultado da divisão é:", a)
    else:
        print('Operação inválida. Use + - * /.')