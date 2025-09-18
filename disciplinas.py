###################
#..DISCIPLINAS.PY....
###################
import os
import json
import customtkinter
from tkinter import Menu  

class DisciplinaManager:
    def __init__(self, app, frame):
        self.app = app
        self.frame = frame
        self.pasta_editais = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editais")
        self.dados_json = {}

    ##########################
    #  Listar Arquivos JSON  #
    ##########################
    def listar_arquivos_json(self):
        arquivos = []
        for arquivo in os.listdir(self.pasta_editais):
            if arquivo.endswith(".json"):
                nome_formatado = arquivo.replace("_", " ").replace(".json", "")
                arquivos.append(nome_formatado)
        return arquivos

    #############################
    #  Carregar Disciplinas JSON #
    #############################
    def carregar_disciplinas_json(self, arquivo_json):
        caminho_arquivo = os.path.join(self.pasta_editais, f"{arquivo_json}.json")
        if os.path.exists(caminho_arquivo):
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                self.dados_json = json.load(f)



    # Função para resetar o edital
    def resetar_edital(self, arquivo_json):
        # Carregar o arquivo JSON
        arquivo_selecionado = arquivo_json.replace(" ", "_")
        self.carregar_disciplinas_json(arquivo_selecionado)

        # Marcar todas as ramificações como False
        if "disciplinas" in self.dados_json:
            for disciplina, detalhes in self.dados_json["disciplinas"].items():
                for ramificacao, topicos in detalhes.items():
                    for topico in topicos:
                        self.dados_json["disciplinas"][disciplina][ramificacao][topico] = False

        # Salvar as alterações
        self.salvar_dados_json()
        print(f"Edital '{arquivo_json}' foi resetado.")

    ##########################
    #  Calcular Progresso    #
    ##########################
    def calcular_cor_progresso(self, progresso):
        progresso = max(0, min(progresso, 100))
        if progresso == 0:
            return "#FF0000"
        else:
            r = 255 - int(255 * progresso / 100)
            g = int(255 * progresso / 100)
            return f'#{r:02X}{g:02X}00'


    #############################
    #  Carregar Disciplinas      #
    #############################
    def carregar_disciplinas(self, arquivo_json):
        arquivo_selecionado = arquivo_json.replace(" ", "_")
        self.carregar_disciplinas_json(arquivo_selecionado)

        disciplinas = self.dados_json.get("disciplinas", {})

        for widget in self.app.menus["menu_disciplinas"].winfo_children():
            if widget.winfo_exists():
                widget.destroy()

        for disciplina, detalhes in disciplinas.items():
            total_ramificacoes = sum(len(topicos) for ramificacao, topicos in detalhes.items())
            ramificacoes_concluidas = sum(1 for ramificacao, topicos in detalhes.items() for estado in topicos.values() if estado)
            progresso = int((ramificacoes_concluidas / total_ramificacoes) * 100) if total_ramificacoes > 0 else 0

            cor_borda = "#32CD32" if progresso == 100 else "#4A90E2"
            cor_texto_disciplina = cor_borda

            disciplina_frame = customtkinter.CTkFrame(self.app.menus["menu_disciplinas"], corner_radius=10, fg_color="transparent", border_width=2, border_color=cor_borda)
            disciplina_frame.pack(pady=5, padx=20, fill="x")

            label_disciplina = customtkinter.CTkLabel(disciplina_frame, text=disciplina, font=("Consolas", 31, "bold"), text_color=cor_texto_disciplina)
            label_disciplina.pack(pady=10, anchor="center")

            progresso_label = customtkinter.CTkLabel(disciplina_frame, text=f"{progresso}% concluído", font=("Consolas", 21, "italic"), text_color=self.calcular_cor_progresso(progresso))
            progresso_label.pack(pady=5, anchor="center")

            # Adicionando o evento de clique corretamente
            disciplina_frame.bind("<Button-1>", lambda event, nome=disciplina, det=detalhes: self.abrir_disciplina(nome, det))
            label_disciplina.bind("<Button-1>", lambda event, nome=disciplina, det=detalhes: self.abrir_disciplina(nome, det))


    def abrir_disciplina(self, nome, detalhes):
        """
        Abre a disciplina, renderiza os detalhes e ajusta o frame corretamente,
        atualizando o scroll para garantir que o conteúdo seja exibido sem problemas.
        """
        # Define o limite de caracteres para quebra de linha
        LIMITE_QUEBRA_LINHA = 85

        # Renderiza os elementos da disciplina
        self._carregar_detalhes_disciplina(nome, detalhes, LIMITE_QUEBRA_LINHA)

        # Adiciona um pequeno atraso para garantir que tudo seja renderizado antes de forçar o update
        self.app.menus["menu_disciplinas"].after(100, self._ajustar_scroll)

    def _ajustar_scroll(self):
        """
        Ajusta o scroll do CTkScrollableFrame para garantir que o frame esteja visível
        e que a área rolável seja atualizada corretamente.
        """
        # Atualiza o layout e o scrollregion do frame
        self.app.menus["menu_disciplinas"].update_idletasks()

        # Acessa o canvas interno do CTkScrollableFrame e rola para o topo
        self.app.menus["menu_disciplinas"]._parent_canvas.yview_moveto(0)

    def _carregar_detalhes_disciplina(self, nome, detalhes, LIMITE_QUEBRA_LINHA):
        """
        Carrega os detalhes da disciplina, limpando e reorganizando o conteúdo no frame.
        """
        # Limpa todos os widgets dentro do menu de disciplinas
        for widget in self.app.menus["menu_disciplinas"].winfo_children():
            widget.destroy()

        # Botão para voltar à lista de disciplinas
        botao_voltar = customtkinter.CTkButton(
            self.app.menus["menu_disciplinas"], text="Voltar",
            command=lambda: self.carregar_disciplinas(self.app.lista_editais.get()),
            corner_radius=5
        )
        botao_voltar.pack(pady=5, padx=10, anchor="w")

        # Exibe o nome da disciplina no topo
        nome_disciplina = customtkinter.CTkLabel(
            self.app.menus["menu_disciplinas"], text=nome, font=("Consolas", 30, "bold"), text_color="#FFFFFF"
        )
        nome_disciplina.pack(pady=5, anchor="center")

        # Carrega os detalhes das ramificações e tópicos
        for ramificacao, topicos in detalhes.items():
            # Calcula o progresso para colorir a borda
            total_topicos = len(topicos)
            topicos_concluidos = sum(1 for estado in topicos.values() if estado)
            progresso_ramificacao = int((topicos_concluidos / total_topicos) * 100) if total_topicos > 0 else 0

            cor_borda = "#32CD32" if progresso_ramificacao == 100 else "#4A90E2"
            cor_texto = cor_borda

            # Cria um frame para cada ramificação com borda colorida
            ramificacao_frame = customtkinter.CTkFrame(
                self.app.menus["menu_disciplinas"], corner_radius=8, fg_color="transparent", border_width=1, border_color=cor_borda
            )
            ramificacao_frame.pack(pady=5, padx=15, fill="x")

            # Nome da ramificação
            ramificacao_label = customtkinter.CTkLabel(
                ramificacao_frame, text=ramificacao, font=("Consolas", 25, "bold"), text_color=cor_texto
            )
            ramificacao_label.pack(pady=5, anchor="center")

            # Frame interno para os tópicos
            sub_frame = customtkinter.CTkFrame(ramificacao_frame, fg_color="transparent")
            sub_frame.pack(pady=2, padx=8, anchor="center")

            for idx, (topico, estado) in enumerate(topicos.items()):  # Adicionando índice
                cor_texto = "#90EE90" if estado else "#FFFFFF"

                # Adiciona linha divisória antes do primeiro subtópico
                if idx == 0:  # Se for o primeiro subtópico
                    linha_divisoria = customtkinter.CTkLabel(
                        sub_frame, text="─" * 100, font=("Consolas", 12), text_color="#4A90E2"  # Azul padrão
                    )
                    linha_divisoria.pack(fill="x", pady=1)

                # Formata o texto para múltiplas linhas
                texto_formatado = self.quebrar_texto(topico, LIMITE_QUEBRA_LINHA)

                # Define margem inferior maior apenas para o último subtópico
                margem_inferior = 15 if idx == len(topicos) - 1 else 1

                # Exibe o texto do tópico
                topico_label = customtkinter.CTkLabel(
                    sub_frame, text=texto_formatado, font=("Consolas", 21, "bold"), text_color=cor_texto
                )
                topico_label.pack(anchor="center", pady=(1, margem_inferior))  # Margem superior pequena, inferior variável

                # Menu contextual de clique direito
                topico_label.bind("<Button-3>", lambda event, t=topico, r=ramificacao, lbl=topico_label: self.criar_menu_contextual(event, t, r, lbl, nome))

                # Adiciona linha divisória apenas entre os tópicos (não no último)
                if idx < len(topicos) - 1:  # Se não for o último subtópico
                    linha_divisoria = customtkinter.CTkLabel(
                        sub_frame, text="─" * 100, font=("Consolas", 12), text_color="#4A90E2"  # Azul padrão
                    )
                    linha_divisoria.pack(fill="x", pady=1)





            # Aplica cor de progresso na ramificação
            self.verificar_e_aplicar_cor(ramificacao_frame, ramificacao_label, progresso_ramificacao)

        # Atualiza a interface após todos os widgets serem adicionados
        self.app.menus["menu_disciplinas"].update_idletasks()

    def quebrar_texto(self, texto, max_len):
        """
        Divide o texto em várias linhas para facilitar a leitura.
        """
        palavras = texto.split()
        linhas = []
        linha_atual = ""

        for palavra in palavras:
            if len(linha_atual) + len(palavra) + 1 <= max_len:
                linha_atual += " " + palavra if linha_atual else palavra
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)

        return "\n".join(linhas)



    #############################
    #  Verificar e Aplicar Cor   #
    #############################
    def verificar_e_aplicar_cor(self, ramificacao_frame, ramificacao_label, progresso):
        if progresso == 100:
            ramificacao_label.configure(text_color="#32CD32")
            ramificacao_frame.configure(border_color="#32CD32")
        else:
            ramificacao_label.configure(text_color="#4A90E2")
            ramificacao_frame.configure(border_color="#4A90E2")

    #############################
    #  Menu Contextual          #
    #############################
    def criar_menu_contextual(self, event, topico, ramificacao, label, disciplina):
        menu = Menu(self.app, tearoff=0)  # Usar tkinter.Menu aqui
        menu.add_command(label="Marcar como Concluído", command=lambda: self.marcar_como_concluido(disciplina, ramificacao, topico, label))
        menu.add_command(label="Desmarcar/Restaurar", command=lambda: self.desmarcar_como_concluido(disciplina, ramificacao, topico, label))
        menu.post(event.x_root, event.y_root)

        


    #############################
    #  Marcar e Desmarcar Conclusão #
    #############################
    def marcar_como_concluido(self, disciplina, ramificacao, topico, label):
        self.dados_json["disciplinas"][disciplina][ramificacao][topico] = True
        label.configure(text_color="#90EE90", font=("Consolas", 21, "bold"))
        self.salvar_dados_json()
        self.atualizar_cor_ramificacao(disciplina, ramificacao)

    def desmarcar_como_concluido(self, disciplina, ramificacao, topico, label):
        self.dados_json["disciplinas"][disciplina][ramificacao][topico] = False
        label.configure(text_color="#FFFFFF", font=("Consolas", 21, "normal"))
        self.salvar_dados_json()
        self.atualizar_cor_ramificacao(disciplina, ramificacao)

    #############################
    #  Atualizar Cor da Ramificação #
    #############################
    def atualizar_cor_ramificacao(self, disciplina, ramificacao):
        topicos = self.dados_json["disciplinas"][disciplina][ramificacao]
        total_topicos = len(topicos)
        topicos_concluidos = sum(1 for estado in topicos.values() if estado)
        progresso = int((topicos_concluidos / total_topicos) * 100) if total_topicos > 0 else 0

        for widget in self.app.menus["menu_disciplinas"].winfo_children():
            if isinstance(widget, customtkinter.CTkFrame):
                ramificacao_label = widget.winfo_children()[0]
                if ramificacao_label.cget("text") == ramificacao:
                    self.verificar_e_aplicar_cor(widget, ramificacao_label, progresso)

    #############################
    #  Salvar Dados JSON        #
    #############################
    def salvar_dados_json(self):
        arquivo_selecionado = self.app.lista_editais.get().replace(" ", "_")
        caminho_arquivo = os.path.join(self.pasta_editais, f"{arquivo_selecionado}.json")
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(self.dados_json, f, ensure_ascii=False, indent=4)

