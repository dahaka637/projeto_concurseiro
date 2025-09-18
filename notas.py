import customtkinter
import json
import os

class NotasManager:
    def __init__(self, app, frame_principal, dados_json):
        self.app = app
        self.frame_principal = frame_principal
        self.dados_json = dados_json
        self.pasta_editais = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editais")

        # Inicializar o dicionário de notas e o controle de abas
        self.notas = {}
        self.abas = []  # Lista para armazenar as abas criadas

        # Carregar o arquivo JSON após a inicialização completa
        self.app.after(100, self.carregar_json_edital)

    def carregar_json_edital(self):
        """Carregar o arquivo JSON completo do edital."""
        try:
            if hasattr(self.app, 'lista_editais'):
                arquivo_edital = self.app.lista_editais.get().replace(" ", "_") + ".json"
                caminho_arquivo = os.path.join(self.pasta_editais, arquivo_edital)


                if os.path.exists(caminho_arquivo):
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        self.dados_json = json.load(f)

                    # Chamar o método para carregar as notas existentes
                    self.carregar_notas_existentes()

                else:
                    self.dados_json = {}
                    # Limpar as notas se o arquivo não for encontrado
                    self.notas.clear()
                    self.tabview.delete_all()
            else:
                pass
        except Exception as e:
            self.dados_json = {}


    def create_menu(self):
        """Criar o menu de Notas dentro do frame principal."""
        menu_notas = customtkinter.CTkFrame(self.frame_principal, border_width=2)
        menu_notas.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.6)

        self.botao_criar_nota = customtkinter.CTkButton(menu_notas, text="Criar Nota", command=self.mostrar_frame_titulo)
        self.botao_criar_nota.place(relx=0.02, rely=0.02, relwidth=0.3)

        self.botao_salvar = customtkinter.CTkButton(menu_notas, text="Salvar", command=self.salvar_nota_selecionada)
        self.botao_salvar.place(relx=0.35, rely=0.02, relwidth=0.3)

        self.botao_excluir = customtkinter.CTkButton(menu_notas, text="Excluir", command=self.excluir_nota_selecionada)
        self.botao_excluir.place(relx=0.68, rely=0.02, relwidth=0.3)

        self.tabview = customtkinter.CTkTabview(menu_notas)
        self.tabview.place(relx=0.02, relwidth=0.96, relheight=0.85, rely=0.1)

        self.frame_titulo = customtkinter.CTkFrame(menu_notas, border_width=2)
        self.frame_titulo.place(relx=0.2, rely=0.3, relwidth=0.6, relheight=0.3)
        self.frame_titulo.lower()

        label_titulo = customtkinter.CTkLabel(self.frame_titulo, text="Informe o título da nota:")
        label_titulo.pack(pady=10)

        self.entry_titulo_nota = customtkinter.CTkEntry(self.frame_titulo, width=250)
        self.entry_titulo_nota.pack(pady=10)

        frame_botoes = customtkinter.CTkFrame(self.frame_titulo)
        frame_botoes.pack(pady=5)

        botao_salvar_titulo = customtkinter.CTkButton(frame_botoes, text="Salvar", command=self.salvar_nota_com_titulo)
        botao_salvar_titulo.pack(side="left", padx=5)

        botao_cancelar_titulo = customtkinter.CTkButton(frame_botoes, text="Cancelar", command=self.cancelar_criacao_nota)
        botao_cancelar_titulo.pack(side="left", padx=5)

        self.app.after(200, self.carregar_notas_existentes)

        return menu_notas

    def carregar_notas_existentes(self):
        """Carregar as notas existentes no JSON."""
        # Deletar todas as abas existentes, verificando a lista de abas criadas
        for aba in self.abas:
            self.tabview.delete(aba)

        # Limpar a lista de abas armazenadas
        self.abas.clear()

        if "notas" in self.dados_json and self.dados_json["notas"]:
            for titulo_nota, conteudo_nota in self.dados_json["notas"].items():
                self.adicionar_aba(titulo_nota)
                # Limpar o conteúdo antes de inserir para evitar duplicações
                self.notas[titulo_nota].delete("1.0", "end")
                self.notas[titulo_nota].insert("1.0", conteudo_nota)
        else:
            pass




    def mostrar_frame_titulo(self):
        """Mostrar o frame para inserir o título da nova nota."""
        self.frame_titulo.lift()

    def salvar_nota_com_titulo(self):
        """Salvar a nota com o título fornecido pelo usuário."""
        titulo_nota = self.entry_titulo_nota.get()

        if titulo_nota:
            if "notas" not in self.dados_json:
                self.dados_json["notas"] = {}

            self.dados_json["notas"][titulo_nota] = ""
            self.adicionar_aba(titulo_nota)

            self.frame_titulo.lower()
            self.entry_titulo_nota.delete(0, 'end')

            self.salvar_json_edital()

            self.exibir_feedback_criar()  # Feedback visual para criar nota

    def cancelar_criacao_nota(self):
        """Cancelar a criação de uma nova nota."""
        self.frame_titulo.lower()
        self.entry_titulo_nota.delete(0, 'end')

    def adicionar_aba(self, nome_nota):
        """Adicionar uma nova aba com o nome da nota."""
        # Verificar se a aba já existe na lista de abas
        if nome_nota not in self.abas:
            nova_aba = self.tabview.add(nome_nota)
            campo_texto = customtkinter.CTkTextbox(nova_aba, wrap="word")
            campo_texto.pack(expand=True, fill="both", padx=10, pady=10)
            self.notas[nome_nota] = campo_texto
            self.abas.append(nome_nota)  # Adicionar o nome da aba na lista de abas

            if nome_nota in self.dados_json["notas"]:
                self.notas[nome_nota].delete("1.0", "end")  # Garantir que não haja duplicação
                self.notas[nome_nota].insert("1.0", self.dados_json["notas"][nome_nota])


    def excluir_nota_selecionada(self):
        """Excluir a nota atualmente selecionada."""
        nota_selecionada = self.tabview.get()
        if nota_selecionada in self.dados_json["notas"]:
            del self.dados_json["notas"][nota_selecionada]
            self.tabview.delete(nota_selecionada)
            del self.notas[nota_selecionada]
            self.salvar_json_edital()
            self.exibir_feedback_excluir()

    def salvar_nota_selecionada(self):
        """Salvar a nota atualmente selecionada."""
        nota_selecionada = self.tabview.get()
        if nota_selecionada in self.notas:
            conteudo = self.notas[nota_selecionada].get("1.0", "end-1c")
            self.dados_json["notas"][nota_selecionada] = conteudo
            self.salvar_json_edital()
            self.exibir_feedback_salvo()

    # Métodos de feedback visual

    def exibir_feedback_criar(self):
        """Exibir feedback visual de que a nota foi criada."""
        self.botao_criar_nota.configure(text="Criado com sucesso", fg_color="#4CAF50")  # Verde
        self.app.after(3000, self.resetar_botao_criar)

    def exibir_feedback_salvo(self):
        """Exibir feedback visual de que a nota foi salva."""
        self.botao_salvar.configure(text="Salvo com sucesso", fg_color="#4CAF50")  # Verde
        self.app.after(3000, self.resetar_botao_salvar)

    def exibir_feedback_excluir(self):
        """Exibir feedback visual de que a nota foi excluída."""
        self.botao_excluir.configure(text="Excluído com sucesso", fg_color="#FF5733")  # Vermelho
        self.app.after(3000, self.resetar_botao_excluir)

    # Métodos para resetar os botões ao estado original

    def resetar_botao_criar(self):
        """Resetar o botão de criar nota ao estado original."""
        self.botao_criar_nota.configure(text="Criar Nota", fg_color="#4A90E2")

    def resetar_botao_salvar(self):
        """Resetar o botão de salvar ao estado original."""
        self.botao_salvar.configure(text="Salvar", fg_color="#4A90E2")

    def resetar_botao_excluir(self):
        """Resetar o botão de excluir ao estado original."""
        self.botao_excluir.configure(text="Excluir", fg_color="#4A90E2")

    def salvar_json_edital(self):
        """Salvar o conteúdo do JSON no arquivo do edital."""
        try:
            arquivo_edital = self.app.lista_editais.get().replace(" ", "_") + ".json"
            caminho_arquivo = os.path.join(self.pasta_editais, arquivo_edital)


            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados_existentes = json.load(f)
                dados_existentes["notas"] = self.dados_json["notas"]
            else:
                dados_existentes = self.dados_json

            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

        except Exception as e:
            pass
