# sistema.py (CÓDIGO FINAL E COMPLETO)
import uuid
from datetime import date, timedelta
import random

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


# ==============================================================================
# 1. CLASSES BASE E HERANÇA (SQLAlchemy Models) - CORREÇÃO DE TYPERROR
# ==============================================================================
class Pessoa(db.Model):
    """Classe base (mãe) para Leitor e Funcionario, usando STI."""
    __tablename__ = 'pessoas'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    
    tipo = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'pessoa', 'polymorphic_on': tipo}

    # CONSTRUTOR FINAL: Apenas **kwargs para não conflitar com argumentos posicionais do DB
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 

class Leitor(Pessoa):
    """Classe Leitor: Herda de Pessoa e mapeada via STI."""
    __mapper_args__ = {'polymorphic_identity': 'leitor'}
    
    matricula = db.Column(db.String(20), unique=True, index=True, default=lambda: f"L-{random.randint(1000, 9999)}")
    limite_livros = db.Column(db.Integer, default=3)
    
    # CONSTRUTOR CORRIGIDO: Passa TUDO explicitamente como palavra-chave (kwargs) para super()
    def __init__(self, nome: str, cpf: str = "", limite_livros: int = 3, **kwargs):
        # Passa nome e cpf como palavra-chave para Pessoa.__init__ via super()
        super().__init__(nome=nome, cpf=cpf, limite_livros=limite_livros, **kwargs)
        self.limite_livros = limite_livros
    
    def fazer_locacao(self, livro, funcionario):
        from app import db 
        if not livro.disponivel:
            return None, f"ERRO: Livro '{livro.titulo}' indisponível."
        
        db.session.flush() 
        # Recalcula locações ativas
        ativas = Locacao.query.filter_by(leitor_id=self.id).join(Livro).filter(Livro.disponivel == False).count()
        
        if ativas >= self.limite_livros:
            return None, f"ERRO: Leitor {self.nome} atingiu o limite de {self.limite_livros} locações."
            
        locacao = Locacao(leitor=self, livro=livro, funcionario=funcionario, prazo_dias=self.get_prazo())
        livro.emprestar() 
        
        return locacao, None

    def devolver_livro(self, locacao_registro, data_real: date):
        if locacao_registro.livro.devolver():
            locacao_registro.registrar_devolucao(data_real) 
            multa = locacao_registro.calcular_multa()
            return multa
        return 0.0
        
    def get_prazo(self):
        return 7

class Funcionario(Pessoa):
    """Classe Funcionario: Herda de Pessoa e mapeada via STI."""
    __mapper_args__ = {'polymorphic_identity': 'funcionario'}
    
    id_funcionario = db.Column(db.String(20), unique=True, index=True, default=lambda: f"F-{random.randint(100, 999)}")
    cargo = db.Column(db.String(50))
    
    # CONSTRUTOR CORRIGIDO: Passa TUDO explicitamente como palavra-chave (kwargs) para super()
    def __init__(self, nome: str, cpf: str = "", cargo: str = "", **kwargs):
        super().__init__(nome=nome, cpf=cpf, cargo=cargo, **kwargs)
        self.cargo = cargo

    def registrar_locacao(self, leitor: Leitor, livro):
        return leitor.fazer_locacao(livro, self)

# ==============================================================================
# 2. CLASSES PARA POLIMORFISMO E ASSOCIAÇÃO
# ==============================================================================
class Livro(db.Model):
    """Classe Livro (base para Polimorfismo), usando STI."""
    __tablename__ = 'livros'
    
    isbn = db.Column(db.String(20), primary_key=True, unique=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100))
    disponivel = db.Column(db.Boolean, default=True)
    multa_diaria = db.Column(db.Float, default=1.00)

    tipo = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'livro_comum', 'polymorphic_on': tipo}

    def emprestar(self) -> bool:
        self.disponivel = False
        return True

    def devolver(self) -> bool:
        self.disponivel = True
        return True

    def get_valor_multa_diaria(self) -> float:
        return self.multa_diaria

class LivroReferencia(Livro):
    """Subclasse (Polimorfismo): Multa maior para livros de referência."""
    __mapper_args__ = {'polymorphic_identity': 'livro_referencia'}
    
    # CONSTRUTOR CORRIGIDO: Aceita **kwargs
    def __init__(self, titulo: str, autor: str, isbn: str, **kwargs):
        super().__init__(titulo=titulo, autor=autor, isbn=isbn, **kwargs)
        self.multa_diaria = 5.00 

class Locacao(db.Model):
    """Classe de Associação (Tabela Separada): Conecta Leitor, Livro e Funcionario."""
    __tablename__ = 'locacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    data_locacao = db.Column(db.Date, default=date.today)
    data_devolucao_prevista = db.Column(db.Date)
    data_devolucao_real = db.Column(db.Date, nullable=True)

    leitor_id = db.Column(db.String, db.ForeignKey('pessoas.id'), nullable=False) 
    livro_isbn = db.Column(db.String(20), db.ForeignKey('livros.isbn'), nullable=False) 
    funcionario_id = db.Column(db.String, db.ForeignKey('pessoas.id'), nullable=False)
    
    leitor = db.relationship('Leitor', backref='locacoes_feitas', foreign_keys=[leitor_id])
    livro = db.relationship('Livro', backref='registros_locacao', foreign_keys=[livro_isbn])
    funcionario = db.relationship('Funcionario', backref='locacoes_registradas', foreign_keys=[funcionario_id])

    # CONSTRUTOR CORRIGIDO: Aceita **kwargs
    def __init__(self, leitor: Leitor, livro: Livro, funcionario: Funcionario, prazo_dias: int = 7, **kwargs):
        super().__init__(**kwargs)
        self.leitor = leitor
        self.livro = livro
        self.funcionario = funcionario
        self.data_devolucao_prevista = self.data_locacao + timedelta(days=prazo_dias)

    def calcular_multa(self) -> float:
        if self.data_devolucao_real and self.data_devolucao_real > self.data_devolucao_prevista:
            dias_atraso = (self.data_devolucao_real - self.data_devolucao_prevista).days
            valor_multa = dias_atraso * self.livro.get_valor_multa_diaria()
            return float(valor_multa)
        return 0.0

    def registrar_devolucao(self, data_real: date):
        self.data_devolucao_real = data_real

# ==============================================================================
# 3. FUNÇÕES UTILITÁRIAS
# ==============================================================================
def parse_date(date_str: str):
    """Converte string (AAAA-MM-DD) para objeto date."""
    try:
        return date.fromisoformat(date_str)
    except Exception:
        return None

from flask import Flask, render_template, request, redirect, url_for
from sistema import db, Pessoa, Leitor, Funcionario, Livro, LivroReferencia, Locacao, parse_date

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)