import re


def validar(dados, schema):
    erros = []
    for campo, regras in schema.items():
        valor = dados.get(campo)

        if regras.get('required') and not valor and valor != 0:
            erros.append(f"{campo}: campo obrigatório")
            continue

        if valor is None or valor == '':
            if 'default' in regras:
                dados[campo] = regras['default']
            continue

        if 'coerce' in regras:
            try:
                valor = regras['coerce'](valor)
                dados[campo] = valor
            except (ValueError, TypeError):
                erros.append(f"{campo}: valor inválido")
                continue

        if 'type' in regras and not isinstance(valor, regras['type']):
            erros.append(f"{campo}: tipo inválido")
            continue

        if 'min' in regras and isinstance(valor, (int, float)) and valor < regras['min']:
            erros.append(f"{campo}: valor mínimo é {regras['min']}")
        if 'max' in regras and isinstance(valor, (int, float)) and valor > regras['max']:
            erros.append(f"{campo}: valor máximo é {regras['max']}")

        if 'maxlen' in regras and isinstance(valor, str) and len(valor) > regras['maxlen']:
            erros.append(f"{campo}: máximo {regras['maxlen']} caracteres")
        if 'minlen' in regras and isinstance(valor, str) and len(valor) < regras['minlen']:
            erros.append(f"{campo}: mínimo {regras['minlen']} caracteres")

        if 'pattern' in regras and isinstance(valor, str):
            if not re.match(regras['pattern'], valor):
                erros.append(f"{campo}: formato inválido")

        if 'choices' in regras and valor not in regras['choices']:
            erros.append(f"{campo}: valor inválido. Opções: {', '.join(regras['choices'])}")

    return erros
