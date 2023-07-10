import basic

while True:
	texto = input('basic > ')
	resultado, erro = basic.executar('<stdin>', texto)

	if erro:
		print(erro.as_string())
	else:
		print(resultado)
