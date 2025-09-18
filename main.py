###################
#.......MAIN.PY....
###################

import os
import customtkinter
from PIL import Image
from disciplinas import DisciplinaManager
from notas import NotasManager
from materiais import MateriaisManager
import json
from questoes import QuestoesManager
from editar import *
import time
from datetime import datetime

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme(os.path.join(os.path.dirname(__file__), "visual.json"))

def iniciar_software():
    class App(customtkinter.CTk):
        def __init__(self):
            super().__init__()

            self.protocol("WM_DELETE_WINDOW", self.close_app)
            self.title("Projeto Concurseiro")
            self.attributes("-alpha", 0.99)
            self.resizable(True, True)  
            width, height = 1200, 750
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.geometry(f"{width}x{height}+{x}+{y}")

            raiz = os.path.dirname(os.path.abspath(__file__))
            self.diretorio_img = os.path.join(raiz, "img")
            nome_icone = "LOGO.ico"
            caminho_icone = os.path.join(self.diretorio_img, nome_icone)
            if os.path.exists(caminho_icone):
                self.iconbitmap(caminho_icone)

            # Frame principal que mantém a estrutura da interface
            frame = customtkinter.CTkFrame(self)
            frame.place(relx=0.02, rely=0.00, relwidth=0.96, relheight=0.96)

            # Frame exclusivo para o título (agora com imagem)
            frame_titulo = customtkinter.CTkFrame(self, fg_color="transparent")
            frame_titulo.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=0.17)
            frame_titulo.pack_propagate(False)
            caminho_titulo_img = os.path.join(self.diretorio_img, "titulo.png")  

            # Carregar a imagem do título
            titulo_img = customtkinter.CTkImage(Image.open(caminho_titulo_img), size=(400, 85))  # Ajuste o tamanho conforme necessário

            # Exibir a imagem no lugar do título
            label_titulo = customtkinter.CTkLabel(frame_titulo, image=titulo_img, text="", anchor="center")
            label_titulo.place(relx=0.2, rely=0.5, anchor="center")

            self.icones = {
                "Disciplinas": {"image": "Disciplinas.png", "text": "Disciplinas", "menu": "menu_disciplinas"},
                "Notas": {"image": "Notas.png", "text": "Notas", "menu": "menu_notas"},
                "Materiais": {"image": "Materiais.png", "text": "Materiais", "menu": "menu_materiais"},
                "Questões": {"image": "questoes.png", "text": "Questões", "menu": "menu_questoes"},
                "Editais": {"image": "Editais.png", "text": "Editais", "menu": "menu_editais"}
            }


            # Instância do gerenciador de disciplinas
            self.disciplina_manager = DisciplinaManager(self, frame)

            self.materiais_manager = MateriaisManager(self, frame)

            # Instância do gerenciador de notas
            self.notas_manager = NotasManager(self, frame, self.disciplina_manager.dados_json)

            # Instância do gerenciador de questões
            self.questoes_manager = QuestoesManager(self, frame, self.disciplina_manager.dados_json)



            # Variáveis de controle do tempo
            self.tempo_inicio = time.time()
            self.ultima_atualizacao = time.time()
            self.tempo_total = 0
            self.tempo_dia = 0
            self.data_hoje = datetime.now().strftime('%Y-%m-%d')

            self.menus = {}
            self.init_menus(frame)

            # Carregar ícones antes de manipular labels
            self.load_icons(frame_titulo, self.diretorio_img)

            # Inicializa o menu de editais após criar disciplina_manager
            self.init_menu_editais()

            self.carregar_disciplinas()

            # Chamar on_icon_click após os ícones serem carregados
            self.on_icon_click("Disciplinas")


            self.verificar_ou_criar_estrutura_temporizador()

            self.iniciar_temporizador()
            

        def reset_icon_styles(self):
            for icone in self.icones:
                self.icones[icone]["label"].configure(text_color="white", font=customtkinter.CTkFont(size=20, weight="bold"))

        def on_icon_click(self, icon_name):
            self.reset_icon_styles()
            self.icones[icon_name]["label"].configure(text_color="#4A90E2", font=customtkinter.CTkFont(size=18, weight="bold"))
            self.ocultar_todos_os_menus()
            self.menus[self.icones[icon_name]["menu"]].place(relx=0.0, rely=0.18, relwidth=1.0, relheight=0.82)

        def load_icons(self, barra_de_tarefas, diretorio_img):
            # Lista de posições relx, uma para cada ícone
            posicoes_relx = [0.41, 0.54, 0.63, 0.74, 0.86]


            icon_size = (50, 50)

            for idx, icon_name in enumerate(self.icones):
                icon_data = self.icones[icon_name]
                icon_image_path = os.path.join(diretorio_img, icon_data["image"])
                icon_image = customtkinter.CTkImage(Image.open(icon_image_path), size=icon_size)

                # Criar o ícone com o texto associado
                icon_label = customtkinter.CTkLabel(barra_de_tarefas, text=icon_data["text"], image=icon_image, compound="top", font=("Consolas", 20, "bold"))
                
                # Usar a posição relx correspondente da lista
                icon_label.place(relx=posicoes_relx[idx], rely=0.5, anchor="w")
                icon_label.bind("<Button-1>", lambda event, name=icon_name: self.on_icon_click(name))
                self.icones[icon_name]["label"] = icon_label




        def init_menus(self, frame):
            self.menus["menu_disciplinas"] = customtkinter.CTkScrollableFrame(frame, width=900, height=400, fg_color="transparent", border_width=2)
            self.menus["menu_notas"] = self.notas_manager.create_menu()
            self.menus["menu_materiais"] = self.materiais_manager.create_menu()
            self.menus["menu_editais"] = customtkinter.CTkFrame(frame, border_width=2)
            self.menus["menu_questoes"] = self.questoes_manager.create_menu()

        def init_menu_editais(self):
            arquivos_json = self.disciplina_manager.listar_arquivos_json()
            
            # Movendo os itens para cima
            label_instrucoes = customtkinter.CTkLabel(self.menus["menu_editais"], text="Selecione o edital", font=("Consolas", 20, "bold"))
            label_instrucoes.place(relx=0.5, rely=0.1, anchor="center")
            
            lista_editais = customtkinter.CTkOptionMenu(self.menus["menu_editais"], values=arquivos_json, font=("Consolas", 21), command=lambda valor: self.carregar_disciplinas(valor))
            lista_editais.place(relx=0.5, rely=0.2, anchor="center", relwidth=0.35, relheight=0.06)
            lista_editais.set(arquivos_json[0] if arquivos_json else "Nenhum arquivo")
            self.lista_editais = lista_editais

            # Adicionando o botão "Resetar Edital"
            botao_resetar = customtkinter.CTkButton(self.menus["menu_editais"], text="Resetar Edital", command=self.resetar_edital)
            botao_resetar.place(relx=0.5, rely=0.3, anchor="center", relwidth=0.3, relheight=0.06)

            # Adicionando o botão "Zerar Questões"
            botao_zerar_questoes = customtkinter.CTkButton(self.menus["menu_editais"], text="Zerar Questões", command=self.zerar_questoes)
            botao_zerar_questoes.place(relx=0.5, rely=0.4, anchor="center", relwidth=0.3, relheight=0.06)

            # Adicionando o botão "Zerar Temporizador"
            botao_zerar_temporizador = customtkinter.CTkButton(self.menus["menu_editais"], text="Zerar Temporizador", command=self.zerar_temporizador)
            botao_zerar_temporizador.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.3, relheight=0.06)


            # Adicionando o botão "Editar Edital"
            botao_editar_edital = customtkinter.CTkButton(self.menus["menu_editais"], text="Editar Edital", command=self.abrir_editar_edital)
            botao_editar_edital.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.3, relheight=0.06)


            # Adicionando a linha divisória
            linha_divisoria = customtkinter.CTkFrame(self.menus["menu_editais"], height=2, fg_color="grey")
            linha_divisoria.place(relx=0.05, rely=0.65, relwidth=0.9)

            # Adicionar rótulo para mostrar a mensagem de reset ou zerar questões
            self.label_mensagem_reset = customtkinter.CTkLabel(self.menus["menu_editais"], text="", font=("Consolas", 18), text_color="#68ff5c")
            self.label_mensagem_reset.place(relx=0.5, rely=0.88, anchor="center")

            # Adicionar o texto "Desenvolvido por Henrique Wegher"
            label_desenvolvedor = customtkinter.CTkLabel(self.menus["menu_editais"], text="Desenvolvido por Henrique Wegher", font=("Consolas", 12), text_color="grey")
            label_desenvolvedor.place(relx=0.5, rely=0.95, anchor="center")

            label_total_horas = customtkinter.CTkLabel(self.menus["menu_editais"], text="Total de Horas de Estudo: 00:00:00", font=("Consolas", 18))
            label_total_horas.place(relx=0.5, rely=0.7, anchor="center")  # Próximo à linha divisória
            self.label_total_horas = label_total_horas  # Salva a referência

            label_horas_hoje = customtkinter.CTkLabel(self.menus["menu_editais"], text="Total de Horas Hoje: 00:00:00", font=("Consolas", 16))
            label_horas_hoje.place(relx=0.5, rely=0.75, anchor="center")  # Um pouco abaixo do total de horas
            self.label_horas_hoje = label_horas_hoje  # Salva a referência


            # Ajuste do botão "Pausar"
            self.botao_pausar = customtkinter.CTkButton(self.menus["menu_editais"], text="Iniciar Cronômetro", width=135, height=30, command=self.pausar_ou_retornar_temporizador)
            self.botao_pausar.place(relx=0.5, rely=0.82 , anchor="center")





        def carregar_disciplinas(self, valor_selecionado=None):
            """Carregar disciplinas e atualizar questões, notas e materiais com base no edital selecionado."""
            arquivo_json = self.lista_editais.get() if valor_selecionado is None else valor_selecionado
            # Carregar disciplinas
            self.disciplina_manager.carregar_disciplinas(arquivo_json)
            # Atualizar as notas com o novo JSON
            self.notas_manager.carregar_json_edital()
            # Atualizar os materiais com o novo JSON
            self.materiais_manager.carregar_json_edital()
            # Atualizar as questões com o novo JSON
            self.disciplina_manager.carregar_disciplinas(arquivo_json)
            self.questoes_manager.atualizar_questoes_com_edital(arquivo_json)
            self.verificar_ou_criar_estrutura_temporizador()
            self.tempo_inicio = 0  # Reinicia o tempo de início para contabilizar o novo tempo
            self.pausado = True
            self.botao_pausar.configure(text="Iniciar Cronômetro")
            self.iniciar_temporizador()
            
            





        def zerar_questoes(self):
            """Apagar todas as questões do edital selecionado."""
            try:
                arquivo_edital = self.lista_editais.get().replace(" ", "_") + ".json"
                caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editais", arquivo_edital)

                if os.path.exists(caminho_arquivo):
                    # Carregar o JSON atual
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados_json = json.load(f)
                    
                    # Zerar a parte das questões
                    dados_json["questoes"] = {}

                    # Salvar novamente o JSON atualizado
                    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                        json.dump(dados_json, f, ensure_ascii=False, indent=4)

                    # Atualizar a interface
                    self.questoes_manager.questoes = {}  # Limpar as questões carregadas
                    self.questoes_manager.exibir_estatisticas_questoes()  # Atualizar a exibição
                    self.label_mensagem_reset.configure(text="Questões zeradas com sucesso!", text_color="green")
                else:
                    self.label_mensagem_reset.configure(text="Arquivo de edital não encontrado.", text_color="red")

            except Exception as e:
                pass
                self.label_mensagem_reset.configure(text="Erro ao zerar questões.", text_color="red")



        def resetar_edital(self):
            self.disciplina_manager.resetar_edital(self.lista_editais.get())
            self.label_mensagem_reset.configure(text="Edital resetado com sucesso!")  # Exibir a mensagem
            self.carregar_disciplinas()  # Recarregar disciplinas após o reset

        def ocultar_todos_os_menus(self):
            for menu in self.menus.values():
                menu.place_forget()

        def close_app(self):
            os._exit(0)
    
#################
# TEMPORIZADOR
#################


        def verificar_ou_criar_estrutura_temporizador(self):
            """Verifica se a estrutura de temporizador existe no JSON, caso contrário, cria uma nova e atualiza a interface."""
            arquivo_json = self.lista_editais.get().replace(" ", "_") + ".json"
            caminho_arquivo = os.path.join(self.disciplina_manager.pasta_editais, arquivo_json)
            
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                # Verifica se a estrutura de temporizador já existe
                if 'temporizador' not in dados:
                    dados['temporizador'] = {
                        'tempo_total': 0,
                        'tempo_dia': 0,
                        'data': self.data_hoje
                    }
                    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                        json.dump(dados, f, ensure_ascii=False, indent=4)
                else:
                    # Recupera o tempo salvo anteriormente
                    self.tempo_total = dados['temporizador']['tempo_total']
                    self.tempo_dia = dados['temporizador']['tempo_dia']
                    self.data_hoje = dados['temporizador']['data']
                    
                    # Verifica se o dia mudou
                    data_atual = datetime.now().strftime('%Y-%m-%d')
                    if self.data_hoje != data_atual:
                        # Se o dia mudou, adiciona o tempo do dia ao total e reseta o tempo do dia
                        self.tempo_total += self.tempo_dia
                        self.tempo_dia = 0
                        self.data_hoje = data_atual
                        
                        # Atualiza o JSON com os novos valores
                        dados['temporizador']['tempo_total'] = self.tempo_total
                        dados['temporizador']['tempo_dia'] = self.tempo_dia
                        dados['temporizador']['data'] = self.data_hoje
                        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                            json.dump(dados, f, ensure_ascii=False, indent=4)

                    # Atualiza a interface com os valores já carregados
                    total_horas_estudo = self.tempo_total + self.tempo_dia
                    self.label_horas_hoje.configure(text=f"Total de Horas Hoje: {self.formatar_tempo(self.tempo_dia)}")
                    self.label_total_horas.configure(text=f"Total de Horas de Estudo: {self.formatar_tempo(total_horas_estudo)}")
                    
            else:
                # Se o arquivo não existe, cria uma nova estrutura de dados
                dados = {
                    'temporizador': {
                        'tempo_total': 0,
                        'tempo_dia': 0,
                        'data': self.data_hoje
                    }
                }
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=4)
                
                # Atualiza a interface com os valores iniciais
                self.label_horas_hoje.configure(text="Total de Horas Hoje: 00:00:00")
                self.label_total_horas.configure(text="Total de Horas de Estudo: 00:00:00")



        def iniciar_temporizador(self):
            """Inicia o temporizador para atualizar o tempo na interface e salvar no JSON a cada 30 segundos."""
            self.verificar_ou_criar_estrutura_temporizador()  # Carrega os tempos salvos e atualiza a interface
            self.tempo_inicio = time.time()  # Marca o tempo inicial
            self.tempo_pausado = 0  # Variável para armazenar o tempo decorrido durante a pausa
            self.pausado = True  # Começa pausado, até o usuário iniciar
            self.atualizar_tempo_interface()  # Atualiza a interface com o tempo
            self.salvar_dados_periodicamente()  # Salva os dados periodicamente


        def atualizar_tempo_interface(self):
            """Atualiza o tempo na interface a cada segundo."""
            if not self.pausado:
                tempo_atual = time.time()
                tempo_decorrido = (tempo_atual - self.tempo_inicio) + self.tempo_pausado  # Considera o tempo antes da pausa

                # Atualiza a interface com o tempo formatado
                self.label_horas_hoje.configure(text=f"Total de Horas Hoje: {self.formatar_tempo(self.tempo_dia + tempo_decorrido)}")
                self.label_total_horas.configure(text=f"Total de Horas de Estudo: {self.formatar_tempo(self.tempo_total + self.tempo_dia + tempo_decorrido)}")

            # Reexecuta a função após 1 segundo
            self.after(1000, self.atualizar_tempo_interface)

        def salvar_dados_periodicamente(self):
            """Salva os dados no JSON a cada 30 segundos."""
            if not self.pausado:
                self.salvar_tempo_estudo()
            self.after(15000, self.salvar_dados_periodicamente)  # Reexecuta a cada 15 segundos

        def salvar_tempo_estudo(self):
            """Salva o tempo total e o tempo do dia no arquivo JSON."""
            arquivo_json = self.lista_editais.get().replace(" ", "_") + ".json"
            caminho_arquivo = os.path.join(self.disciplina_manager.pasta_editais, arquivo_json)

            tempo_atual = time.time()
            tempo_decorrido = (tempo_atual - self.tempo_inicio) + self.tempo_pausado  # Considera o tempo antes da pausa
            self.tempo_dia += tempo_decorrido  # Atualiza o tempo do dia

            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                # Verifica se a data mudou
                data_atual = datetime.now().strftime('%Y-%m-%d')
                if self.data_hoje != data_atual:
                    # Se a data mudou, adiciona o tempo do dia ao total e reseta o tempo do dia
                    dados['temporizador']['tempo_total'] += self.tempo_dia
                    dados['temporizador']['tempo_dia'] = 0
                    dados['temporizador']['data'] = data_atual
                    self.tempo_total += self.tempo_dia
                    self.tempo_dia = 0
                    self.data_hoje = data_atual
                else:
                    # Caso contrário, apenas atualiza o tempo do dia
                    dados['temporizador']['tempo_dia'] = self.tempo_dia

                # Atualiza os dados no arquivo JSON
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=4)

            # Reseta o tempo de início para o próximo ciclo
            self.tempo_inicio = time.time()
            self.tempo_pausado = 0  # Reseta o tempo pausado após o salvamento

        def formatar_tempo(self, segundos):
            """Formata o tempo em horas, minutos e segundos."""
            horas = int(segundos // 3600)
            minutos = int((segundos % 3600) // 60)
            segundos = int(segundos % 60)
            return f"{horas:02}:{minutos:02}:{segundos:02}"

        def pausar_ou_retornar_temporizador(self):
            """Alterna o estado de pausa do temporizador com feedback visual no botão."""
            if self.pausado:
                # Se o temporizador não está pausado, volta ao estado normal
                self.pausado = False
                self.botao_pausar.configure(text="Pausar", fg_color="#4A90E2", hover_color="#3B7CC4")
                self.tempo_inicio = time.time()  # Reinicia o tempo de início para contabilizar o novo tempo
            else:
                # Se o temporizador está pausado, altera o feedback visual
                self.pausado = True
                self.botao_pausar.configure(text="PAUSADO", fg_color="darkred", hover_color="#B22222")
                # Armazena o tempo decorrido até o momento da pausa
                self.tempo_pausado += time.time() - self.tempo_inicio

        def zerar_temporizador(self):
            """Zera o temporizador e atualiza o JSON."""
            self.tempo_dia = 0
            self.tempo_total = 0
            self.tempo_pausado = 0
            self.tempo_inicio = time.time()  # Reinicia o tempo de início

            # Atualiza a interface
            self.label_horas_hoje.configure(text="Total de Horas Hoje: 00:00:00")
            self.label_total_horas.configure(text="Total de Horas de Estudo: 00:00:00")
            self.label_mensagem_reset.configure(text="Temporizador resetado com sucesso!") 

            # Atualiza o JSON para refletir o temporizador zerado
            arquivo_json = self.lista_editais.get().replace(" ", "_") + ".json"
            caminho_arquivo = os.path.join(self.disciplina_manager.pasta_editais, arquivo_json)
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                # Zera o temporizador no JSON
                dados['temporizador']['tempo_total'] = 0
                dados['temporizador']['tempo_dia'] = 0
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=4)


#################
# TEMPORIZADOR 
#################



################
# ABRIR EDITAL
################
        # Alterar a função abrir_editar_edital para passar o caminho do arquivo JSON
        def abrir_editar_edital(self):
            """Abre uma nova interface para edição do edital, passando o caminho do arquivo JSON."""
            arquivo_edital = self.lista_editais.get().replace(" ", "_") + ".json"
            caminho_arquivo = os.path.join(self.disciplina_manager.pasta_editais, arquivo_edital)
            
            # Chamar a função do arquivo editar.py, passando o caminho do arquivo e o objeto self
            abrir_edital_interface(caminho_arquivo, self)




    if __name__ == "__main__":
        app = App()
        app.mainloop()

iniciar_software()
