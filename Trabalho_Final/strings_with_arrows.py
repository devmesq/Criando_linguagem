
def strings_with_arrows(texto, posicao_inicial, posicao_final):
    resultado = ''

    # Calcular índices
    idx_inicio = max(texto.rfind('\n', 0, posicao_inicial.idx), 0)
    idx_fim = texto.find('\n', idx_inicio + 1)
    if idx_fim < 0:
        idx_fim = len(texto)
    
    # Gerar cada linha
    quantidade_linhas = posicao_final.ln - posicao_inicial.ln + 1
    for i in range(quantidade_linhas):
        # Calcular colunas da linha
        linha = texto[idx_inicio:idx_fim]
        coluna_inicio = posicao_inicial.col if i == 0 else 0
        coluna_fim = posicao_final.col if i == quantidade_linhas - 1 else len(linha) - 1

        # Adicionar ao resultado
        resultado += linha + '\n'
        resultado += ' ' * coluna_inicio + '^' * (coluna_fim - coluna_inicio)

        # Recalcular índices
        idx_inicio = idx_fim
        idx_fim = texto.find('\n', idx_inicio + 1)
        if idx_fim < 0:
            idx_fim = len(texto)

    return resultado.replace('\t', '')