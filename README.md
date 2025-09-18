# Projeto Concurseiro

## Visão Geral
O **Projeto Concurseiro** é um aplicativo desktop desenvolvido em **Python** com **CustomTkinter**, criado para auxiliar no estudo de concursos públicos.  
A ferramenta permite organizar disciplinas, tópicos, questões e anotações, monitorando o progresso do aluno e fornecendo estatísticas de desempenho.

---
<img width="1220" height="797" alt="image" src="https://github.com/user-attachments/assets/a36c6008-4224-4d3b-bceb-7bbc8b421a60" />

## Funcionalidades Principais
- **Gerenciamento de Editais**
  - Carrega editais estruturados em JSON com disciplinas, ramificações e tópicos.
  - Permite resetar progresso e marcar tópicos concluídos.

- **Controle de Progresso**
  - Progresso exibido por disciplina e ramificação com cores dinâmicas.
  - Percentuais de conclusão calculados automaticamente.

- **Gestão de Questões**
  - Registro de acertos, erros e “não faz ideia”.
  - Estatísticas por disciplina e por ramificação.
  - Feedback visual colorido indicando desempenho.

- **Notas Pessoais**
  - Criação e exclusão de anotações organizadas em abas.
  - Armazenamento persistente em arquivos JSON.

- **Edição de Editais**
  - Editor textual para modificar disciplinas e tópicos.
  - Validações automáticas para evitar dados inválidos.

- **Interface Customizada**
  - Estilo configurável via `visual.json`.
  - Frames roláveis, popups e navegação intuitiva.

---
<img width="1218" height="842" alt="image" src="https://github.com/user-attachments/assets/8d0e197c-fbc7-4fd0-a63c-a33405644bda" />

## Arquitetura do Projeto
O sistema segue uma arquitetura modular:

- **`main.py`** → Ponto de entrada da aplicação, inicializa a interface principal.
- **`disciplinas.py`** → Gerencia os editais, disciplinas e cálculo de progresso.
- **`questoes.py`** → Sistema de estatísticas de questões e relatórios por matéria.
- **`notas.py`** → Módulo de gerenciamento de anotações do usuário.
- **`materiais.py`** → Suporte para materiais extras (apostilas, links, docs).
- **`editar.py`** → Editor textual de editais em JSON.
- **`visual.json`** → Configuração visual (cores, labels, botões).
- **`Agente_Administrativo.json`** → Exemplo de edital para estudo.

---

## Estrutura de Diretórios

```
📂 projeto_concurseiro
 ┣ main.py -> Arquivo inicial que carrega a aplicação.
 ┣ disciplinas.py -> Gerencia disciplinas e progresso.
 ┣ questoes.py -> Estatísticas de questões e relatórios.
 ┣ notas.py -> Gerenciamento de notas/anotações.
 ┣ materiais.py -> Suporte para materiais complementares.
 ┣ editar.py -> Editor de editais JSON.
 ┣ visual.json -> Configuração visual da interface.
 ┗ Agente_Administrativo.json -> Exemplo de edital com disciplinas/tópicos.
```

---
<img width="1204" height="820" alt="image" src="https://github.com/user-attachments/assets/8676c206-b092-4cde-9ff1-c92f9f466fa6" />

## Tecnologias Utilizadas
- **Python 3.10+**
- **CustomTkinter** (interface gráfica)
- **JSON** (armazenamento de dados de editais, progresso e notas)

---

## Execução do Projeto
Pré-requisitos:
- Python 3.10+
- Instalar dependências:
  ```bash
  pip install customtkinter
  ```

Execução:
```bash
python main.py
```

---

