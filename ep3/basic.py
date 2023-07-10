
#######################################
# IMPORTAR
#######################################

from strings_with_arrows import *

#######################################
# CONSTANTES
#######################################

DIGITO = '0123456789'

#######################################
# ERRO
#######################################

class Erro:
	def __init__(self, posicao_inicial, posicao_final, nome_erro, detalhes):
		self.posicao_inicial = posicao_inicial
		self.posicao_final = posicao_final
		self.nome_erro = nome_erro
		self.detalhes = detalhes
	
	def como_string(self):
		resultado  = f'{self.nome_erro}: {self.detalhes}\n'
		resultado += f'Arquivo {self.posicao_inicial.fn}, linha {self.posicao_inicial.ln + 1}'
		resultado += '\n\n' + string_com_setas(self.posicao_inicial.ftxt, self.posicao_inicial, self.posicao_final)
		return resultado

	class ErroCaractereIlegal(Erro):
	def __init__(self, posicao_inicial, posicao_final, detalhes):
		super().__init__(posicao_inicial, posicao_final, 'Caractere Ilegal', detalhes)

	class ErroSintaxeInvalida(Erro):
	def __init__(self, posicao_inicial, posicao_final, detalhes=''):
		super().__init__(posicao_inicial, posicao_final, 'Sintaxe Inválida', detalhes)

	class ErroTempoExecucao(Erro):
	def __init__(self, posicao_inicial, posicao_final, detalhes, contexto):
		super().__init__(posicao_inicial, posicao_final, 'Erro de Tempo de Execução', detalhes)
		self.contexto = contexto

	def como_string(self):
		resultado  = self.gerar_rastreamento()
		resultado += f'{self.nome_erro}: {self.detalhes}'
		resultado += '\n\n' + string_com_setas(self.posicao_inicial.ftxt, self.posicao_inicial, self.posicao_final)
		return resultado

	def gerar_rastreamento(self):
		resultado = ''
		posicao = self.posicao_inicial
		ctx = self.contexto

		while ctx:
			resultado = f'  Arquivo {posicao.fn}, linha {str(posicao.ln + 1)}, em {ctx.nome_exibicao}\n' + resultado
			posicao = ctx.posicao_entrada_pai
			ctx = ctx.pai

		return 'Rastreamento (chamada mais recente por último):\n' + resultado


#######################################
# POSICAO
#######################################

class Posicao:
	def __init__(self, idx, ln, col, fn, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.fn = fn
		self.ftxt = ftxt

	def avancar(self, caractere_atual=None):
		self.idx += 1
		self.col += 1

		if caractere_atual == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copiar(self):
		return Posicao(self.idx, self.ln, self.col, self.fn, self.ftxt)


#######################################
# TOKENS
#######################################



TT_INT     = 'INT'
TT_FLOAT   = 'FLOAT'
TT_PLUS    = 'MAIS'
TT_MINUS   = 'MENOS'
TT_MUL     = 'MULTIPLICACAO'
TT_DIV     = 'DIVISAO'
TT_LPAREN  = 'ABRE_PARENTESES'
TT_RPAREN  = 'FECHA_PARENTESES'
TT_EOF     = 'FIM_DE_ARQUIVO'

class Token:
	def __init__(self, tipo, valor=None, posicao_inicio=None, posicao_fim=None):
		self.tipo = tipo
		self.valor = valor

		if posicao_inicio:
			self.posicao_inicio = posicao_inicio.copiar()
			self.posicao_fim = posicao_inicio.copiar()
			self.posicao_fim.avancar()

		if posicao_fim:
			self.posicao_fim = posicao_fim
	
	def __repr__(self):
		if self.valor:
			return f'{self.tipo}:{self.valor}'
		return f'{self.tipo}'


#######################################
# LEXER
#######################################

class Lexer:
	def __init__(self, fn, texto):
		self.fn = fn
		self.texto = texto
		self.pos = Posicao(-1, 0, -1, fn, texto)
		self.caractere_atual = None
		self.avancar()
	
	def avancar(self):
		self.pos.avancar(self.caractere_atual)
		self.caractere_atual = self.texto[self.pos.idx] if self.pos.idx < len(self.texto) else None

	def criar_tokens(self):
		tokens = []

		while self.caractere_atual is not None:
			if self.caractere_atual in ' \t':
				self.avancar()
			elif self.caractere_atual in DIGITOS:
				tokens.append(self.criar_numero())
			elif self.caractere_atual == '+':
				tokens.append(Token(TT_MAIS, pos_start=self.pos))
				self.avancar()
			elif self.caractere_atual == '-':
				tokens.append(Token(TT_MENOS, pos_start=self.pos))
				self.avancar()
			elif self.caractere_atual == '*':
				tokens.append(Token(TT_MULTIPLICACAO, pos_start=self.pos))
				self.avancar()
			elif self.caractere_atual == '/':
				tokens.append(Token(TT_DIVISAO, pos_start=self.pos))
				self.avancar()
			elif self.caractere_atual == '(':
				tokens.append(Token(TT_ABRE_PARENTESES, pos_start=self.pos))
				self.avancar()
			elif self.caractere_atual == ')':
				tokens.append(Token(TT_FECHA_PARENTESES, pos_start=self.pos))
				self.avancar()
			else:
				pos_start = self.pos.copiar()
				char = self.caractere_atual
				self.avancar()
				return [], ErroCaractereIlegal(pos_start, self.pos, "'" + char + "'")

		tokens.append(Token(TT_FIM_DE_ARQUIVO, pos_start=self.pos))
		return tokens, None

		def criar_numero(self):
		num_str = ''
		contagem_ponto = 0
		pos_start = self.pos.copiar()

		while self.caractere_atual is not None and self.caractere_atual in DIGITOS + '.':
			if self.caractere_atual == '.':
				if contagem_ponto == 1:
					break
				contagem_ponto += 1
				num_str += '.'
			else:
				num_str += self.caractere_atual
			self.avancar()

		if contagem_ponto == 0:
			return Token(TT_INT, int(num_str), pos_start, self.pos)
		else:
			return Token(TT_FLOAT, float(num_str), pos_start, self.pos)


#######################################
# NODES
#######################################

class NoNumero:
	def __init__(self, tok):
		self.tok = tok

		self.posicao_inicio = self.tok.posicao_inicio
		self.posicao_fim = self.tok.posicao_fim

	def __repr__(self):
		return f'{self.tok}'

class NoOpBinario:
	def __init__(self, no_esquerdo, op_tok, no_direito):
		self.no_esquerdo = no_esquerdo
		self.op_tok = op_tok
		self.no_direito = no_direito

		self.posicao_inicio = self.no_esquerdo.posicao_inicio
		self.posicao_fim = self.no_direito.posicao_fim

	def __repr__(self):
		return f'({self.no_esquerdo}, {self.op_tok}, {self.no_direito})'

class NoOpUnario:
	def __init__(self, op_tok, no):
		self.op_tok = op_tok
		self.no = no

		self.posicao_inicio = self.op_tok.posicao_inicio
		self.posicao_fim = no.posicao_fim

	def __repr__(self):
		return f'({self.op_tok}, {self.no})'


#######################################
# PARSE RESULT
#######################################

class ResultadoAnalise:
	def __init__(self):
		self.erro = None
		self.no = None

	def registrar(self, res):
		if isinstance(res, ResultadoAnalise):
			if res.erro: self.erro = res.erro
			return res.no

		return res

	def sucesso(self, no):
		self.no = no
		return self

	def falha(self, erro):
		self.erro = erro
		return self


#######################################
# PARSER
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self, ):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != TT_EOF:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*' or '/'"
			))
		return res

	###################################

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_PLUS, TT_MINUS):
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))
		
		elif tok.type in (TT_INT, TT_FLOAT):
			res.register(self.advance())
			return res.success(NumberNode(tok))

		elif tok.type == TT_LPAREN:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TT_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int or float"
		))

	def term(self):
		return self.bin_op(self.factor, (TT_MUL, TT_DIV))

	def expr(self):
		return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

	###################################

	def bin_op(self, func, ops):
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(func())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)

#######################################
# RUNTIME RESULT
#######################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

#######################################
# VALUES
#######################################

class Number:
	def __init__(self, value):
		self.value = value
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Division by zero',
					self.context
				)

			return Number(self.value / other.value).set_context(self.context), None

	def __repr__(self):
		return str(self.value)

#######################################
# CONTEXT
#######################################

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos

#######################################
# INTERPRETER
#######################################

class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	###################################

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_BinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left_node, context))
		if res.error: return res
		right = res.register(self.visit(node.right_node, context))
		if res.error: return res

		if node.op_tok.type == TT_PLUS:
			result, error = left.added_to(right)
		elif node.op_tok.type == TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_tok.type == TT_MUL:
			result, error = left.multed_by(right)
		elif node.op_tok.type == TT_DIV:
			result, error = left.dived_by(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.error: return res

		error = None

		if node.op_tok.type == TT_MINUS:
			number, error = number.multed_by(Number(-1))

		if error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))

#######################################
# RUN
#######################################

def run(fn, text):
	# Generate tokens
	lexer = Lexer(fn, text)
	tokens, error = lexer.make_tokens()
	if error: return None, error
	
	# Generate AST
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error: return None, ast.error

	# Run program
	interpreter = Interpreter()
	context = Context('<program>')
	result = interpreter.visit(ast.node, context)

	return result.value, result.error
