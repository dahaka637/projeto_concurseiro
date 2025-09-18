import customtkinter
import tkinter.messagebox
import json
import os
import webbrowser
from tkinter import Menu, filedialog
from PIL import Image

class MateriaisManager:
    def __init__(self, app, frame_principal):
        self.app = app
        self.frame_principal = frame_principal
        self.pasta_editais = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editais")
        self.img_diretorio = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
        self.disciplinas = {}
        self.materiais = {}
        self.mostrar_estudados = True  # Inicialmente mostrar todos

        # Carregar o arquivo JSON após a inicialização completa
        self.app.after(100, self.carregar_json_edital)

    def carregar_json_edital(self):
        """Carregar o arquivo JSON completo do edital e popular o seletor de matérias."""
        try:
            if hasattr(self.app, 'lista_editais'):
                arquivo_edital = self.app.lista_editais.get().replace(" ", "_") + ".json"
                caminho_arquivo = os.path.join(self.pasta_editais, arquivo_edital)

                if os.path.exists(caminho_arquivo):
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados_json = json.load(f)
                        self.disciplinas = dados_json.get("disciplinas", {})
                        self.materiais = dados_json.get("materiais", {})
                else:
                    self.disciplinas = {}
                    self.materiais = {}

                # Atualizar o seletor de matérias após carregar o JSON
                self.atualizar_seletor_materias()
                self.carregar_lista_materiais_filtrada()
            else:
                self.disciplinas = {}
                self.materiais = {}

        except Exception as e:
            self.disciplinas = {}
            self.materiais = {}


    def selecionar_arquivo(self):
        """Abrir o seletor de arquivos e definir o caminho no campo de entrada do link."""
        caminho_arquivo = filedialog.askopenfilename(title="Selecionar Arquivo")
        if caminho_arquivo:
            self.entry_link.delete(0, "end")  # Limpar o campo atual
            self.entry_link.insert(0, caminho_arquivo)  # Inserir o caminho no campo


    def atualizar_seletor_materias(self):
        """Atualizar o seletor de matérias com as disciplinas carregadas do JSON."""
        if hasattr(self, 'seletor_materias'):
            lista_materias = ["TODOS"] + list(self.disciplinas.keys())
            self.seletor_materias.configure(values=lista_materias)
            self.seletor_materias.set("TODOS")
            self.atualizar_seletor_ramificacoes()

    def atualizar_seletor_ramificacoes(self, materia="TODOS"):
        """Atualizar o seletor de ramificações baseado na matéria escolhida."""
        if materia == "TODOS":
            lista_ramificacoes = ["TODOS"]
        else:
            lista_ramificacoes = ["TODOS"] + list(self.disciplinas.get(materia, {}).keys())
        
        self.seletor_ramificacoes.configure(values=lista_ramificacoes)
        self.seletor_ramificacoes.set("TODOS")
        self.carregar_lista_materiais_filtrada()

    def create_menu(self):
        """Criar o menu de Materiais dentro do frame principal."""
        menu_materiais = customtkinter.CTkFrame(self.frame_principal, border_width=2)
        menu_materiais.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.6)

        # Seletor de Matérias na esquerda
        self.seletor_materias = customtkinter.CTkOptionMenu(menu_materiais, values=["Carregando..."], command=lambda x: self.atualizar_seletor_ramificacoes(self.seletor_materias.get()))
        self.seletor_materias.place(relx=0.02, rely=0.05, relwidth=0.4)

        # Seletor de Ramificações abaixo do seletor de matérias
        self.seletor_ramificacoes = customtkinter.CTkOptionMenu(menu_materiais, values=["TODOS"], command=self.carregar_lista_materiais_filtrada)
        self.seletor_ramificacoes.place(relx=0.02, rely=0.11, relwidth=0.4)

        # Botão para criar novo conteúdo
        botao_criar_conteudo = customtkinter.CTkButton(menu_materiais, text="Criar Conteúdo", command=self.mostrar_popup_criar_conteudo)
        botao_criar_conteudo.place(relx=0.58, rely=0.05, relwidth=0.4)

        # Checkbox para mostrar ou ocultar conteúdos estudados
        self.checkbox_estudado = customtkinter.CTkCheckBox(menu_materiais, text="Mostrar conteúdos estudados", command=self.carregar_lista_materiais_filtrada)
        self.checkbox_estudado.place(relx=0.58, rely=0.11)
        self.checkbox_estudado.select()  # Iniciar selecionado para mostrar todos

        # Frame com rolagem para os conteúdos
        self.frame_conteudo = customtkinter.CTkScrollableFrame(menu_materiais, border_width=2)
        self.frame_conteudo.place(relx=0.02, rely=0.18, relwidth=0.96, relheight=0.75)

        return menu_materiais

    def carregar_lista_materiais_filtrada(self, *args):
        """Filtrar e carregar a lista de materiais com base nos filtros aplicados."""
        # Obter a matéria e ramificação selecionadas
        materia_selecionada = self.seletor_materias.get()
        ramificacao_selecionada = self.seletor_ramificacoes.get()

        # Verificar se o checkbox de "mostrar estudados" está selecionado
        mostrar_estudados = self.checkbox_estudado.get() == 1

        # Limpar o frame de conteúdo existente
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

        # Filtrar os materiais com base nos critérios
        for titulo, detalhes in self.materiais.items():
            # Filtrar pela matéria e ramificação
            if materia_selecionada != "TODOS" and detalhes["materia"] != materia_selecionada:
                continue
            if ramificacao_selecionada != "TODOS" and detalhes["ramificacao"] != ramificacao_selecionada:
                continue
            
            # Filtrar pelo status de "estudado"
            if not mostrar_estudados and detalhes["estudado"]:
                continue

            # Adicionar o material que passou pelos filtros
            self.criar_item_material(titulo, detalhes)

    def criar_item_material(self, titulo, detalhes):
        """Criar um item de material no frame com rolagem."""
        # Definir ícone baseado no tipo de conteúdo
        icone_map = {
            "Curso": "livro.png",
            "PDF": "pdf.png",
            "Vídeo": "video.png",
            "Outros": "outros.png",
            "Anotações": "nota.png"
        }
        icone = icone_map.get(detalhes["tipo_conteudo"], "default.png")
        icone_path = os.path.join(self.img_diretorio, icone)

        material_frame = customtkinter.CTkFrame(self.frame_conteudo, corner_radius=10, fg_color="transparent", border_width=2)
        material_frame.pack(pady=10, padx=20, fill="x")

        # Carregar o ícone
        icone_imagem = customtkinter.CTkImage(Image.open(icone_path), size=(100, 100))

        # Adicionar ícone
        icone_label = customtkinter.CTkLabel(material_frame, image=icone_imagem, text="")
        icone_label.place(x=20, y=20)

        # Frame para título e demais informações
        frame_texto = customtkinter.CTkFrame(material_frame, fg_color="transparent")
        frame_texto.pack(fill="x", padx=150, pady=10)

        # Ajuste dinâmico da fonte do título
        max_width = 500  # Largura máxima que o título pode ocupar
        base_font_size = 25  # Tamanho base da fonte
        current_font_size = base_font_size

        # Verificar o comprimento do título e ajustar a fonte dinamicamente
        while True:
            label_titulo = customtkinter.CTkLabel(frame_texto, text=titulo, font=("Consolas", current_font_size, "bold"), text_color="#FFFFFF")
            label_titulo.update_idletasks()  # Atualizar o layout para medir o tamanho
            label_width = label_titulo.winfo_reqwidth()

            if label_width > max_width and current_font_size > 10:
                current_font_size -= 1  # Diminuir a fonte se o título for muito longo
            else:
                break

        # Adicionar o título com o tamanho de fonte ajustado
        label_titulo.pack(pady=1, anchor="center")

        # Limitar visualmente o link (caso seja muito longo)
        link = detalhes['link']
        if len(link) > 40:
            link_visual = f"{link[:37]}..."  # Limitar a visualização a 40 caracteres
        else:
            link_visual = link

        # Link do conteúdo (clicável)
        link_label = customtkinter.CTkLabel(material_frame, text=f"Link: {link_visual}", font=("Consolas", 18, "italic"), text_color="#87CEEB", cursor="hand2")
        link_label.pack(pady=2, anchor="center")
        link_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))

        # Ajuste dinâmico da fonte para a matéria
        base_font_size_materia = 18  # Tamanho base da fonte para a matéria
        current_font_size_materia = base_font_size_materia

        if detalhes["materia"] == "TODOS" and detalhes["ramificacao"] == "TODOS":
            materia_ramificacao = "Geral"
        elif detalhes["ramificacao"] == "TODOS":
            materia_ramificacao = detalhes["materia"]
        else:
            materia_ramificacao = f"{detalhes['materia']} > {detalhes['ramificacao']}"

        max_width_materia = 500  # Largura máxima para a matéria

        while True:
            label_materia = customtkinter.CTkLabel(material_frame, text=f"Matéria: {materia_ramificacao}", font=("Consolas", current_font_size_materia, "italic"), text_color="#4A90E2")
            label_materia.update_idletasks()
            label_width_materia = label_materia.winfo_reqwidth()

            if label_width_materia > max_width_materia and current_font_size_materia > 14:
                current_font_size_materia -= 1  # Diminuir a fonte se o texto for muito longo
            else:
                break

        # Adicionar o texto da matéria com a fonte ajustada
        label_materia.pack(pady=2, anchor="center")

        # Exibir se o conteúdo já foi estudado
        estudado_text = "Estudado" if detalhes["estudado"] else "Não Estudado"
        label_estudado = customtkinter.CTkLabel(material_frame, text=f"Status: {estudado_text}", font=("Consolas", 18, "italic"), text_color="#32CD32" if detalhes["estudado"] else "#FF6347")
        label_estudado.pack(pady=4, anchor="center")

        # Adicionar o menu contextual (clique com o botão direito)
        material_frame.bind("<Button-3>", lambda event: self.criar_menu_contextual(event, titulo, detalhes, label_estudado))
        label_titulo.bind("<Button-3>", lambda event: self.criar_menu_contextual(event, titulo, detalhes, label_estudado))



    def criar_menu_contextual(self, event, titulo, detalhes, label_estudado):
        """Criar menu contextual com opções de marcar como estudado e excluir."""
        menu = Menu(self.app, tearoff=0)
        menu.add_command(label="Marcar/Desmarcar como Estudado", command=lambda: self.marcar_como_estudado(titulo, detalhes, label_estudado))
        menu.add_command(label="Excluir", command=lambda: self.excluir_conteudo(titulo))
        menu.post(event.x_root, event.y_root)

    def marcar_como_estudado(self, titulo, detalhes, label_estudado):
        """Marcar ou desmarcar um conteúdo como estudado."""
        detalhes["estudado"] = not detalhes["estudado"]
        label_estudado.configure(text="Estudado" if detalhes["estudado"] else "Não Estudado",
                                 text_color="#32CD32" if detalhes["estudado"] else "#FF6347")
        self.salvar_materiais()

    def excluir_conteudo(self, titulo):
        """Excluir o conteúdo do JSON."""
        if tkinter.messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir o conteúdo '{titulo}'?"):
            del self.materiais[titulo]
            self.salvar_materiais()
            self.carregar_lista_materiais_filtrada()

    def salvar_materiais(self):
        """Salvar o estado atual dos materiais no arquivo JSON."""
        arquivo_edital = self.app.lista_editais.get().replace(" ", "_") + ".json"
        caminho_arquivo = os.path.join(self.pasta_editais, arquivo_edital)
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados_json = json.load(f)

            dados_json["materiais"] = self.materiais

            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_json, f, ensure_ascii=False, indent=4)

        except Exception as e:
            self.mostrar_erro(f"Erro ao salvar o conteúdo: {e}")

    def mostrar_erro(self, mensagem):
        """Exibir uma mensagem de erro em um popup."""
        tkinter.messagebox.showerror("Erro", mensagem)

    def mostrar_popup_criar_conteudo(self):
        """Exibir um frame popup para criar novo conteúdo."""
        self.popup_frame = customtkinter.CTkFrame(self.frame_principal, border_width=5)
        self.popup_frame.place(relx=0.2, rely=0.22, relwidth=0.6, relheight=0.75)

        # Seletor para o tipo de conteúdo
        label_tipo = customtkinter.CTkLabel(self.popup_frame, text="Selecione o tipo de conteúdo:")
        label_tipo.pack(pady=10)
        self.seletor_tipo_conteudo = customtkinter.CTkOptionMenu(self.popup_frame, values=["Vídeo", "Curso", "PDF", "Anotações", "Outros"])
        self.seletor_tipo_conteudo.pack(pady=5)

        # Campo de entrada para o título
        label_titulo = customtkinter.CTkLabel(self.popup_frame, text="Informe o título do conteúdo:")
        label_titulo.pack(pady=10)
        self.entry_titulo = customtkinter.CTkEntry(self.popup_frame, width=500)
        self.entry_titulo.pack(pady=5)

        # Campo de entrada para o link do conteúdo
        label_link = customtkinter.CTkLabel(self.popup_frame, text="Link do conteúdo:")
        label_link.pack(pady=10)

        self.entry_link = customtkinter.CTkEntry(self.popup_frame, width=500)
        self.entry_link.pack(pady=5)

        # Botão de busca abaixo do campo de entrada
        botao_lupa = customtkinter.CTkButton(self.popup_frame, text="Buscar na Máquina",  # Emoji + texto
                                            command=self.selecionar_arquivo, width=200, height=30)
        botao_lupa.pack(pady=5)  # Espaçamento abaixo do botão


        # Seletor de Matérias
        label_materia = customtkinter.CTkLabel(self.popup_frame, text="Selecione a matéria:")
        label_materia.pack(pady=10)
        self.seletor_materia_popup = customtkinter.CTkOptionMenu(self.popup_frame, width=350, values=["TODOS"] + list(self.disciplinas.keys()), command=self.atualizar_seletor_ramificacoes_popup)
        self.seletor_materia_popup.pack(pady=5)

        # Seletor de Ramificações
        label_ramificacao = customtkinter.CTkLabel(self.popup_frame, text="Selecione a ramificação:")
        label_ramificacao.pack(pady=10)
        self.seletor_ramificacoes_popup = customtkinter.CTkOptionMenu(self.popup_frame, width=350, values=["TODOS"])
        self.seletor_ramificacoes_popup.pack(pady=5)

        # Frame para botões de salvar e cancelar
        frame_botoes = customtkinter.CTkFrame(self.popup_frame, border_width=0, fg_color="transparent")
        frame_botoes.pack(pady=20)

        botao_salvar = customtkinter.CTkButton(frame_botoes, text="Salvar", command=self.salvar_conteudo)
        botao_salvar.pack(side="left", padx=10)

        botao_cancelar = customtkinter.CTkButton(frame_botoes, text="Cancelar", command=self.fechar_popup)
        botao_cancelar.pack(side="left", padx=10)

    def atualizar_seletor_ramificacoes_popup(self, materia):
        """Atualizar o seletor de ramificações no popup baseado na matéria escolhida."""
        if materia == "TODOS":
            lista_ramificacoes = ["TODOS"]
        else:
            lista_ramificacoes = ["TODOS"] + list(self.disciplinas.get(materia, {}).keys())
        
        self.seletor_ramificacoes_popup.configure(values=lista_ramificacoes)
        self.seletor_ramificacoes_popup.set("TODOS")

    def fechar_popup(self):
        """Fechar o popup de criar conteúdo."""
        self.popup_frame.place_forget()

    def salvar_conteudo(self):
        """Salvar o conteúdo criado no arquivo JSON."""
        titulo = self.entry_titulo.get().strip()
        link = self.entry_link.get().strip()
        materia = self.seletor_materia_popup.get()  # Matéria correta do popup
        ramificacao = self.seletor_ramificacoes_popup.get()
        tipo_conteudo = self.seletor_tipo_conteudo.get()  # Tipo de conteúdo

        # Verificações para campos obrigatórios
        if not titulo:
            self.mostrar_erro("Erro: O campo título é obrigatório.")
            return

        if not link:
            self.mostrar_erro("Erro: O campo de link é obrigatório.")
            return

        # Carregar o arquivo JSON atual
        arquivo_edital = self.app.lista_editais.get().replace(" ", "_") + ".json"
        caminho_arquivo = os.path.join(self.pasta_editais, arquivo_edital)
        
        try:
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
            else:
                dados_json = {"disciplinas": {}, "notas": {}, "materiais": {}}
            
            # Certificar que o campo 'materiais' existe no JSON
            if "materiais" not in dados_json:
                dados_json["materiais"] = {}

            # Verificar se o título já existe
            if titulo in dados_json["materiais"]:
                self.mostrar_erro(f"O conteúdo com o título '{titulo}' já existe.")
                return

            # Adicionar o novo conteúdo à estrutura 'materiais'
            dados_json["materiais"][titulo] = {
                "link": link,
                "materia": materia,
                "ramificacao": ramificacao,
                "tipo_conteudo": tipo_conteudo,
                "estudado": False
            }

            # Salvar o JSON atualizado
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_json, f, ensure_ascii=False, indent=4)

            self.fechar_popup()  # Fechar o popup após salvar

            # Atualizar a lista de materiais
            self.materiais[titulo] = dados_json["materiais"][titulo]
            self.carregar_lista_materiais_filtrada()

        except Exception as e:
            self.mostrar_erro(f"Ocorreu um erro ao salvar o conteúdo: {e}")
