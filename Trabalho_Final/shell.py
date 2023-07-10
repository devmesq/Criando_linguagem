import main

while True:
	texto = input('basic > ')
	resultado, erro = main.executar('<stdin>', texto)

	if erro:
		print(erro.as_string())
	else:
		print(resultado)
