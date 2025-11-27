# Sistema de Biblioteca POO

Uma aplicação web de gerenciamento de biblioteca desenvolvida com Flask e SQLAlchemy, demonstrando conceitos de Programação Orientada a Objetos (OOP): **herança, polimorfismo e associação**.

## 🏗️ Arquitetura OOP

### Herança
- `Pessoa` → `Leitor`, `Funcionario`
- `Livro` → `LivroReferencia`

### Polimorfismo
- Single Table Inheritance (STI) para diferenciação de tipos
- `LivroReferencia` sobrescreve `multa_diaria` (5.00 vs 1.00)

### Associação
- Tabela `Locacao` conecta `Leitor` ↔ `Livro` ↔ `Funcionario`
- Relações muitos-para-muitos via tabela de associação

## 📋 Funcionalidades

✅ Cadastrar Leitores, Funcionários, Livros e Livros de Referência  
✅ Locar livros para leitores  
✅ Devolver livros com cálculo de multa por atraso  
✅ Status do sistema (resumo, listas, locações ativas)  
✅ Pesquisar locações por matrícula de leitor  
✅ Feedback visual com mensagens de sucesso/erro  

## 🚀 Deploy no Render.com

### Pré-requisitos
1. Repositório GitHub com o código: `fabzera2007/bibliotecaPOO`
2. Conta no [Render.com](https://render.com) (gratuita)

### Passos de Deploy

1. **Acesse [render.com](https://render.com)** e faça login com sua conta GitHub

2. **Clique em "New +"** → **"Web Service"**

3. **Selecione o repositório**:
   - Procure por `bibliotecaPOO`
   - Clique em "Connect"

4. **Configure o serviço**:
   - **Name**: `biblioteca-poo` (ou qualquer nome)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Free Plan** (ou pago, se preferir)

5. **Clique em "Deploy"**

6. **Aguarde** (~2-5 minutos). Você verá a URL da sua app como:
   ```
   https://biblioteca-poo.onrender.com
   ```

### Notas Importantes

- O banco de dados SQLite é local (Render não persiste arquivos entre reinicializações)
- Para dados persistentes, integre com PostgreSQL (oferecido pelo Render)
- Mensagens de flash funcionam com sessões (secret_key configurada)

## 💻 Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar a aplicação
python app.py
# Acesse: http://localhost:5000
```

## 📁 Estrutura do Projeto

```
bibliotecaPOO/
├── app.py              # Routes Flask
├── sistema.py          # Modelos ORM
├── requirements.txt    # Dependências
├── render.yaml         # Configuração Render
├── .gitignore          # Arquivos ignorados
├── static/
│   └── style.css       # Estilos
└── templates/
    ├── base.html       # Layout base
    ├── index.html      # Home
    ├── cadastrar.html  # Cadastros
    ├── locar.html      # Locação
    ├── devolver.html   # Devolução
    └── status.html     # Status
```

## 🔧 Tecnologias

- **Backend**: Flask 2.3.3
- **ORM**: Flask-SQLAlchemy 3.0.5
- **Servidor**: Gunicorn 21.2.0
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript

---

**Desenvolvido com conceitos de POO (Herança, Polimorfismo, Associação)**
