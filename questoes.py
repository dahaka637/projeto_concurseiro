import customtkinter
import json
import os

class QuestoesManager:
    def __init__(self, app, frame_principal, disciplinas):
        self.app = app
        self.frame_principal = frame_principal
        self.disciplinas = disciplinas  # Dicionário com disciplinas e ramificações
        self.questoes = {}  # Estrutura para armazenar questões
        self.popup_frame = None  # Para manter referência ao frame popup

        # Carregar o arquivo JSON após a inicialização completa
        self.app.after(100, self.carregar_json_edital)

    def carregar_json_edital(self):
        """Carregar o arquivo JSON completo do edital e mostrar as disciplinas."""
        try:
            if hasattr(self.app, 'lista_editais'):
                arquivo_edital = self.app.lista_editais.get().replace(" ", "_") + ".json"
                caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editais", arquivo_edital)
                
                if os.path.exists(caminho_arquivo):
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados_json = json.load(f)
                        self.disciplinas = dados_json.get("disciplinas", {})
                        self.questoes = dados_json.get("questoes", {})
                else:
                    self.disciplinas = {}
                    self.questoes = {}

            else:
                self.disciplinas = {}
                self.questoes = {}

        except Exception as e:
            pass
            self.disciplinas = {}
            self.questoes = {}

    def create_menu(self):
        """Criar o menu de Questões dentro do frame principal."""
        menu_questoes = customtkinter.CTkFrame(self.frame_principal, border_width=2)
        menu_questoes.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.6)

        # Botão centralizado no topo para adicionar questões
        self.botao_adicionar_questao = customtkinter.CTkButton(menu_questoes, text="Adicionar Questões",
                                                            command=self.abrir_popup_adicionar_questao, width=200)
        self.botao_adicionar_questao.place(relx=0.5, rely=0.05, anchor="center")

        # Frame rolável abaixo do botão, ocupando o restante do espaço
        self.frame_rolavel = customtkinter.CTkScrollableFrame(menu_questoes, fg_color="transparent", border_width=2)
        self.frame_rolavel.place(relx=0.0, rely=0.1, relwidth=1.0, relheight=0.9)

        # Certifique-se de que os dados do JSON estão carregados antes de exibir as estatísticas
        self.app.after(100, self.exibir_estatisticas_questoes)

        return menu_questoes

    def exibir_estatisticas_questoes(self):
        """Exibir estatísticas gerais e por matéria no frame rolável."""
        # Primeiro, remover todos os widgets existentes no frame rolável para evitar duplicação
        for widget in self.frame_rolavel.winfo_children():
            widget.destroy()

        # Verificar se há questões registradas
        if not self.questoes:
            pass
            return

        # Função para calcular a cor dinamicamente com base no percentual
        def calcular_cor_dinamica(percentual):
            """Retorna uma cor RGB em formato hexadecimal com base no percentual de acertos."""
            if percentual <= 50:
                r = 255
                g = int((percentual / 50) * 255)
                b = 0
            else:
                r = int(255 - ((percentual - 50) / 50) * 255)
                g = 255
                b = 0
            return f"#{r:02x}{g:02x}{b:02x}"

        # Calcular totais gerais
        total_acertos_geral, total_erros_geral, total_nao_faz_ideia_geral = 0, 0, 0

        # Somar os dados para o cálculo da média geral
        for materia, ramificacoes in self.questoes.items():
            for dados in ramificacoes.values():
                total_acertos_geral += dados.get("acertos", 0)
                total_erros_geral += dados.get("erros", 0)
                total_nao_faz_ideia_geral += dados.get("nao_faz_ideia", 0)

        total_questoes_geral = total_acertos_geral + total_erros_geral + total_nao_faz_ideia_geral
        if total_questoes_geral > 0:
            media_acertos_geral = (total_acertos_geral / total_questoes_geral) * 100
        else:
            media_acertos_geral = 0

        # Calcular a cor dinâmica para a média geral
        cor_media_geral = calcular_cor_dinamica(media_acertos_geral)

        # Exibir o "Total Geral de Questões" e "Média Geral" com cor dinâmica
        label_total_questoes = customtkinter.CTkLabel(self.frame_rolavel, text=f"Total Geral de Questões: {total_questoes_geral}",
                                                    font=("Arial", 20, "bold"))
        label_total_questoes.pack(pady=10)

        label_media_geral = customtkinter.CTkLabel(self.frame_rolavel, text=f"Média Geral: {media_acertos_geral:.2f}%",
                                                font=("Arial", 20, "bold"), text_color=cor_media_geral)
        label_media_geral.pack(pady=10)

        # Percorrer cada matéria
        for materia, ramificacoes in self.questoes.items():
            # Calcular totais da matéria
            total_materia_acertos, total_materia_erros, total_materia_nao_faz_ideia = 0, 0, 0

            for dados in ramificacoes.values():
                total_materia_acertos += dados.get("acertos", 0)
                total_materia_erros += dados.get("erros", 0)
                total_materia_nao_faz_ideia += dados.get("nao_faz_ideia", 0)

            total_materia_questoes = total_materia_acertos + total_materia_erros + total_materia_nao_faz_ideia

            if total_materia_questoes > 0:
                porcent_acertos_materia = (total_materia_acertos / total_materia_questoes) * 100
            else:
                porcent_acertos_materia = 0

            # Calcular a cor do título da matéria e a borda com base na média de acertos
            cor_titulo_materia = calcular_cor_dinamica(porcent_acertos_materia)
            cor_borda_materia = cor_titulo_materia

            # Criar o frame para a matéria com a borda colorida
            frame_materia = customtkinter.CTkFrame(self.frame_rolavel, border_width=3, corner_radius=10)
            frame_materia.configure(border_color=cor_borda_materia)
            frame_materia.pack(pady=10, padx=20, fill="x", expand=True)

            # Exibir o nome da matéria com cor dinâmica
            label_materia = customtkinter.CTkLabel(frame_materia, text=f"{materia}", font=("Arial", 21, "bold"),
                                                text_color=cor_titulo_materia)
            label_materia.pack(pady=5)

            # Exibir o total de questões da matéria
            label_total_questoes_materia = customtkinter.CTkLabel(frame_materia,
                                                                text=f"Total de Questões: {total_materia_questoes}",
                                                                font=("Arial", 16))
            label_total_questoes_materia.pack(pady=5)

            # Exibir a ramificação "GERAL" se ela existir
            if "GERAL" in ramificacoes:
                dados_geral = ramificacoes["GERAL"]
                total_geral_questoes = dados_geral["acertos"] + dados_geral["erros"] + dados_geral["nao_faz_ideia"]
                porcent_acertos_geral = (dados_geral["acertos"] / total_geral_questoes) * 100 if total_geral_questoes > 0 else 0
                cor_titulo_geral = calcular_cor_dinamica(porcent_acertos_geral)

                label_geral = customtkinter.CTkLabel(frame_materia,
                                                    text=f"GERAL - Total: {total_geral_questoes}",
                                                    font=("Arial", 18, "italic"),
                                                    text_color=cor_titulo_geral)
                label_geral.pack(pady=2)

                label_acertos_geral = customtkinter.CTkLabel(frame_materia,
                                                            text=f"  Acertos: {dados_geral.get('acertos', 0)} ({porcent_acertos_geral:.2f}%)",
                                                            font=("Arial", 12))
                label_acertos_geral.pack(pady=2)

                porcent_erros_geral = (dados_geral.get("erros", 0) / total_geral_questoes) * 100 if total_geral_questoes > 0 else 0
                label_erros_geral = customtkinter.CTkLabel(frame_materia,
                                                        text=f"  Erros: {dados_geral.get('erros', 0)} ({porcent_erros_geral:.2f}%)",
                                                        font=("Arial", 12))
                label_erros_geral.pack(pady=2)

                porcent_nao_faz_ideia_geral = (dados_geral.get("nao_faz_ideia", 0) / total_geral_questoes) * 100 if total_geral_questoes > 0 else 0
                label_nao_faz_ideia_geral = customtkinter.CTkLabel(frame_materia,
                                                                text=f"  Não faz ideia: {dados_geral.get('nao_faz_ideia', 0)} ({porcent_nao_faz_ideia_geral:.2f}%)",
                                                                font=("Arial", 12))
                label_nao_faz_ideia_geral.pack(pady=3)

            # Exibir as ramificações da matéria
            for ramificacao, dados in ramificacoes.items():
                if ramificacao == "GERAL":
                    continue  # Já exibimos "GERAL", então pulamos

                total_ramificacao_questoes = dados.get("acertos", 0) + dados.get("erros", 0) + dados.get("nao_faz_ideia", 0)

                if total_ramificacao_questoes > 0:
                    porcent_acertos = (dados.get("acertos", 0) / total_ramificacao_questoes) * 100
                else:
                    porcent_acertos = 0

                # Calcular a cor do título da ramificação com base no percentual de acertos
                cor_titulo_ramificacao = calcular_cor_dinamica(porcent_acertos)

                # Exibir o nome da ramificação com cor dinâmica
                label_ramificacao = customtkinter.CTkLabel(frame_materia,
                                                        text=f"{ramificacao} - Total: {total_ramificacao_questoes}",
                                                        font=("Arial", 18, "italic"),
                                                        text_color=cor_titulo_ramificacao)
                label_ramificacao.pack(pady=2)

                # Exibir os acertos, erros e "não faz ideia" sem cor
                label_acertos = customtkinter.CTkLabel(frame_materia,
                                                    text=f"  Acertos: {dados.get('acertos', 0)} ({porcent_acertos:.2f}%)",
                                                    font=("Arial", 12))
                label_acertos.pack(pady=2)

                porcent_erros = (dados.get("erros", 0) / total_ramificacao_questoes) * 100 if total_ramificacao_questoes > 0 else 0
                label_erros = customtkinter.CTkLabel(frame_materia,
                                                    text=f"  Erros: {dados.get('erros', 0)} ({porcent_erros:.2f}%)",
                                                    font=("Arial", 12))
                label_erros.pack(pady=2)

                porcent_nao_faz_ideia = (dados.get("nao_faz_ideia", 0) / total_ramificacao_questoes) * 100 if total_ramificacao_questoes > 0 else 0
                label_nao_faz_ideia = customtkinter.CTkLabel(frame_materia,
                                                            text=f"  Não faz ideia: {dados.get('nao_faz_ideia', 0)} ({porcent_nao_faz_ideia:.2f}%)",
                                                            font=("Arial", 12))
                label_nao_faz_ideia.pack(pady=3)

        # Certifique-se de que os widgets foram processados e exibidos
        self.frame_rolavel.update_idletasks()



    
    def abrir_popup_adicionar_questao(self):
        """Abrir um frame para adicionar uma nova questão."""
        if self.popup_frame:
            self.popup_frame.place_forget()  # Remover o popup se já estiver aberto

        # Criar o popup centralizado dentro do frame principal
        self.popup_frame = customtkinter.CTkFrame(self.frame_principal, border_width=2)
        self.popup_frame.place(relx=0.325, rely=0.25, relwidth=0.35, relheight=0.5)

        # Seletor de Matéria
        self.seletor_materia = customtkinter.CTkOptionMenu(self.popup_frame, values=list(self.disciplinas.keys()),
                                                           command=self.atualizar_ramificacoes, width=250)
        self.seletor_materia.pack(pady=(20, 5))  # Maior margem para cima
        self.seletor_materia.set("Selecione a matéria")

        # Seletor de Ramificação
        self.seletor_ramificacao = customtkinter.CTkOptionMenu(self.popup_frame, values=["Selecione uma matéria"], width=250)
        self.seletor_ramificacao.pack(pady=5)
        self.seletor_ramificacao.set("Selecione a ramificação")

        # Entradas de acertos, erros e não faz ideia
        entry_frame = customtkinter.CTkFrame(self.popup_frame, fg_color="transparent")
        entry_frame.pack(pady=10)

        # "Acertos" entry
        self.entry_acertos = customtkinter.CTkEntry(entry_frame, width=50, justify="center")
        self.entry_acertos.grid(row=0, column=0, padx=10, pady=5)
        label_acertos = customtkinter.CTkLabel(entry_frame, text="Acertos", text_color="green")
        label_acertos.grid(row=0, column=1)

        # "Erros" entry
        self.entry_erros = customtkinter.CTkEntry(entry_frame, width=50, justify="center")
        self.entry_erros.grid(row=1, column=0, padx=10, pady=5)
        label_erros = customtkinter.CTkLabel(entry_frame, text="Erros", text_color="yellow")
        label_erros.grid(row=1, column=1)

        # "Não faz ideia" entry
        self.entry_nao_faz_ideia = customtkinter.CTkEntry(entry_frame, width=50, justify="center")
        self.entry_nao_faz_ideia.grid(row=2, column=0, padx=10, pady=5)
        label_nao_faz_ideia = customtkinter.CTkLabel(entry_frame, text="Não faz ideia", text_color="red")
        label_nao_faz_ideia.grid(row=2, column=1)

        # Botões de Cancelar e Salvar
        botoes_frame = customtkinter.CTkFrame(self.popup_frame, fg_color="transparent")
        botoes_frame.pack(pady=10)

        botao_cancelar = customtkinter.CTkButton(botoes_frame, text="Cancelar", width=120, command=self.fechar_popup)
        botao_cancelar.grid(row=0, column=0, padx=20)

        botao_salvar = customtkinter.CTkButton(botoes_frame, text="Salvar", width=120, command=self.salvar_questao)
        botao_salvar.grid(row=0, column=1, padx=20)

        # Adicionar o label para mensagens de erro (inicialmente invisível)
        self.label_erro = customtkinter.CTkLabel(self.popup_frame, text="", text_color="red")
        self.label_erro.pack(pady=5)


    def validate_numeric(self, value, max_digits):
        """Validar se o valor é numérico e tem no máximo max_digits dígitos."""
        if value.isdigit() and len(value) <= int(max_digits):
            return True
        elif value == "":  # Permitir string vazia
            return True
        else:
            return False

    def salvar_questao(self):
        """Salvar a questão no JSON e exibir mensagem de erro caso falte informação."""
        materia = self.seletor_materia.get()
        ramificacao = self.seletor_ramificacao.get()

        if materia == "Selecione a matéria" or ramificacao == "Selecione a ramificação":
            self.label_erro.configure(text="Selecione uma matéria e uma ramificação.")
            return

        # Permitir salvar com campos vazios, interpretando-os como zero
        try:
            acertos = int(self.entry_acertos.get() or 0)
            erros = int(self.entry_erros.get() or 0)
            nao_faz_ideia = int(self.entry_nao_faz_ideia.get() or 0)
        except ValueError:
            self.label_erro.configure(text="Todos os campos devem ser números ou deixados em branco.")
            return

        # Atualizar ou adicionar questões na estrutura
        if materia not in self.questoes:
            self.questoes[materia] = {}

        # Verificar se a ramificação é "GERAL" e salvar diretamente na matéria
        if ramificacao == "GERAL":
            if "GERAL" not in self.questoes[materia]:
                self.questoes[materia]["GERAL"] = {"acertos": 0, "erros": 0, "nao_faz_ideia": 0}
            
            self.questoes[materia]["GERAL"]["acertos"] += acertos
            self.questoes[materia]["GERAL"]["erros"] += erros
            self.questoes[materia]["GERAL"]["nao_faz_ideia"] += nao_faz_ideia
        else:
            if ramificacao not in self.questoes[materia]:
                self.questoes[materia][ramificacao] = {"acertos": 0, "erros": 0, "nao_faz_ideia": 0}

            # Atualizar os valores existentes
            self.questoes[materia][ramificacao]["acertos"] += acertos
            self.questoes[materia][ramificacao]["erros"] += erros
            self.questoes[materia][ramificacao]["nao_faz_ideia"] += nao_faz_ideia

        # Fechar o popup
        self.fechar_popup()

        # Salvar no JSON
        self.salvar_json()

        # Atualizar a exibição das estatísticas
        self.exibir_estatisticas_questoes()

        # Feedback visual no botão
        self.feedback_visual()



    def feedback_visual(self):
        """Mudar o texto e cor do botão após o cadastro e restaurar depois."""
        original_text = "Adicionar Questões"
        original_color = "#4A90E2"

        # Alterar o texto e a cor para "Cadastrado com Sucesso"
        self.botao_adicionar_questao.configure(text="Cadastrado com Sucesso", fg_color="green")

        # Após 3 segundos, voltar ao estado original
        self.app.after(3000, lambda: self.botao_adicionar_questao.configure(text=original_text, fg_color=original_color))

    def salvar_json(self):
        """Salvar a estrutura de questões no arquivo JSON."""
        try:
            arquivo_edital = self.app.lista_editais.get().replace(" ", "_") + ".json"
            caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editais", arquivo_edital)
            
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados_json = json.load(f)
                
            # Adicionar a estrutura de questões ao JSON
            dados_json["questoes"] = self.questoes

            # Salvar novamente o JSON atualizado
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_json, f, ensure_ascii=False, indent=4)


        except Exception as e:
            pass

    def fechar_popup(self):
        """Fechar o frame popup."""
        self.popup_frame.place_forget()  # Esconde o popup ao cancelar

    def atualizar_ramificacoes(self, materia_selecionada):
        """Atualizar as ramificações com base na matéria selecionada."""
        ramificacoes = list(self.disciplinas.get(materia_selecionada, {}).keys())  # Pegar as ramificações da disciplina
        ramificacoes.insert(0, "GERAL")  # Inserir "GERAL" no início da lista
        
        if ramificacoes:
            self.seletor_ramificacao.configure(values=ramificacoes)
            self.seletor_ramificacao.set("Selecione a ramificação")
        else:
            self.seletor_ramificacao.configure(values=["Nenhuma ramificação disponível"])
            self.seletor_ramificacao.set("Nenhuma ramificação disponível")




    def atualizar_disciplinas(self):
        """Atualiza a lista de disciplinas no menu ao carregar novo edital."""
        # Aqui você deve atualizar a lista de disciplinas com base no novo edital
        novas_disciplinas = list(self.disciplinas.keys())

        # Por exemplo, atualizar o seletor de disciplinas se houver um menu de seleção
        if hasattr(self, 'seletor_materia'):
            self.seletor_materia.configure(values=novas_disciplinas)
            if novas_disciplinas:
                self.seletor_materia.set(novas_disciplinas[0])
            else:
                self.seletor_materia.set("Nenhuma disciplina disponível")


    def atualizar_questoes_com_edital(self, novo_edital):
        """Carregar as questões e disciplinas do novo edital e atualizar a exibição."""
        try:
            arquivo_edital = novo_edital.replace(" ", "_") + ".json"
            caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editais", arquivo_edital)

            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    self.questoes = dados_json.get("questoes", {})
                    self.disciplinas = dados_json.get("disciplinas", {})
            else:
                self.questoes = {}
                self.disciplinas = {}

            # Atualizar a exibição das estatísticas e disciplinas com as novas questões e disciplinas
            self.exibir_estatisticas_questoes()
            self.atualizar_disciplinas()

        except Exception as e:
            pass
            self.questoes = {}
            self.disciplinas = {}
            self.exibir_estatisticas_questoes()  # Limpa a exibição caso haja erro
