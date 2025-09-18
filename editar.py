import customtkinter
import json
import tkinter.messagebox as MessageBox  # Usar o tkinter.messagebox para exibir alertas de erro

def abrir_edital_interface(caminho_arquivo, app):
    """Função para abrir a interface de edição do edital e carregar o conteúdo do JSON."""
    # Criar a nova janela para edição do edital
    editar_janela = customtkinter.CTkToplevel()  # Nova janela
    editar_janela.title("Editar Edital")
    
    # Ajuste da geometria para centralizar a janela
    screen_width = editar_janela.winfo_screenwidth()
    screen_height = editar_janela.winfo_screenheight()
    width, height = 800, 600
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    editar_janela.geometry(f"{width}x{height}+{x}+{y}")
    
    # Garantir que a janela de edição fique na frente da janela principal
    editar_janela.grab_set()  # Impede a interação com a janela principal enquanto a janela de edição está aberta
    editar_janela.lift()  # Traz a janela para frente
    editar_janela.focus_force()  # Garante que a janela de edição receba o foco

    # Tentar carregar o arquivo JSON
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados_json = json.load(f)
        
        disciplinas = dados_json.get("disciplinas", {})  # Carregar as disciplinas
        progresso_anterior = disciplinas.copy()  # Preservar o estado atual
    except Exception as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        MessageBox.showerror("Erro", f"Erro ao carregar o arquivo JSON: {e}")
        return

    # Criar o conteúdo do edital em texto
    conteudo_editado = ""

    for nome_disciplina, dados_disciplina in disciplinas.items():
        conteudo_editado += "____________________________________\n"
        conteudo_editado += f"#{nome_disciplina}\n"
        conteudo_editado += "____________________________________\n\n"
        
        # Iterar sobre os tópicos
        for nome_topico, dados_topico in dados_disciplina.items():
            conteudo_editado += f"- {nome_topico}\n"
            
            # Adicionar os subtópicos, um por linha
            for subtitulo in dados_topico:
                conteudo_editado += f"{subtitulo}\n"

            conteudo_editado += "\n"  # Espaço entre tópicos para melhor visualização

    # Criar uma caixa de texto para exibir o conteúdo do edital
    texto_edital = customtkinter.CTkTextbox(editar_janela, width=700, height=400)
    texto_edital.insert("1.0", conteudo_editado)  # Preencher a caixa de texto com o conteúdo do edital
    texto_edital.pack(padx=10, pady=10, fill="both", expand=True)

    def salvar_edital():
        try:
            print("Iniciando o processo de salvamento...")

            # Obter o conteúdo editado
            conteudo_salvo = texto_edital.get("1.0", "end-1c").strip()

            # Se o conteúdo estiver vazio, mostrar mensagem de erro
            if not conteudo_salvo:
                print("Erro: O conteúdo está vazio!")
                MessageBox.showerror("Erro", "O conteúdo do edital está vazio. Não é possível salvar.")
                return

            # Atualizar o conteúdo no JSON
            novo_conteudo = {}
            linhas = conteudo_salvo.split("\n")
            disciplina_atual = ""
            topico_atual = ""
            erro_detectado = False
            erro_mensagem = ""

            # Estrutura para armazenar os dados antes e depois da edição
            dados_modificados = {
                "disciplinas": {}
            }

            # Iterar sobre as linhas para identificar e organizar as disciplinas, tópicos e subtópicos
            for linha in linhas:
                linha = linha.strip()

                # Ignorar linhas vazias ou com apenas travessões
                if not linha or linha == "____________________________________":
                    continue

                if linha.startswith("#"):  # Disciplina
                    disciplina_atual = linha[1:].strip()
                    if disciplina_atual not in dados_modificados["disciplinas"]:
                        dados_modificados["disciplinas"][disciplina_atual] = {}
                elif linha.startswith("-"):  # Tópico
                    topico_atual = linha[1:].strip()
                    if topico_atual not in dados_modificados["disciplinas"][disciplina_atual]:
                        dados_modificados["disciplinas"][disciplina_atual][topico_atual] = {}
                else:  # Subtópico
                    subtitulo = linha.strip()
                    if subtitulo:
                        # Preservar o progresso anterior
                        estado = (
                            progresso_anterior.get(disciplina_atual, {})
                            .get(topico_atual, {})
                            .get(subtitulo, False)
                        )
                        dados_modificados["disciplinas"][disciplina_atual][topico_atual][subtitulo] = estado

            # Validação: Checando se a disciplina tem pelo menos um tópico e se o tópico tem pelo menos um subtópico
            for disciplina, dados_topicos in dados_modificados["disciplinas"].items():
                if not dados_topicos:  # Disciplina sem tópicos
                    erro_mensagem = f"A disciplina '{disciplina}' não pode ser salva sem tópicos."
                    erro_detectado = True
                    break
                for topico, dados_subtopicos in dados_topicos.items():
                    if not dados_subtopicos:  # Tópico sem subtópicos
                        erro_mensagem = f"O tópico '{topico}' na disciplina '{disciplina}' não pode ser salvo sem subtópicos."
                        erro_detectado = True
                        break

            if erro_detectado:
                MessageBox.showerror("Erro de Validação", erro_mensagem)
                return

            # Atualizar os dados no JSON com as alterações feitas
            dados_json["disciplinas"] = dados_modificados["disciplinas"]
            
            # Salvar no arquivo JSON
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_json, f, ensure_ascii=False, indent=4)

            print("Alterações salvas com sucesso!")

            # Atualizar a interface principal após salvar
            editar_janela.destroy()  # Fecha a janela após salvar
            app.carregar_disciplinas()  # Chama o método da aplicação principal para atualizar a interface

        except Exception as e:
            print(f"Erro ao salvar as alterações: {e}")
            MessageBox.showerror("Erro", f"Erro ao salvar as alterações: {e}")  # Exibe o erro usando tkinter.messagebox

    # Botões lado a lado
    frame_botoes = customtkinter.CTkFrame(editar_janela)
    frame_botoes.pack(pady=10)

    # Botão para salvar as alterações
    botao_salvar = customtkinter.CTkButton(frame_botoes, text="Salvar Alterações", command=salvar_edital)
    botao_salvar.pack(side="left", padx=10)

    # Botão para fechar sem salvar
    botao_fechar = customtkinter.CTkButton(frame_botoes, text="Fechar", command=editar_janela.destroy)
    botao_fechar.pack(side="left", padx=10)
