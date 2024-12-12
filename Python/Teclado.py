import tkinter as tk
import pygame
import pygame.midi
import json
import time
import threading
import serial

# Inicializando o mixer do pygame
pygame.midi.init()
print(f"Dispositivos MIDI disponíveis: {pygame.midi.get_count()}")
player = pygame.midi.Output(2)
player.set_instrument(0)


# Inicializando comunicação com Arduino
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=1)


# |||| Variáveis globais ||||
gravando = False    # Indica o estado da gravação
gravando_faixa = "notas"  # Indica a faixa de gravação atual, como sendo "nota" ou "batida"
eventos_notas = [] # Lista das notas gravadas
eventos_batidas = [] # Lista das batidas gravadas
inicio_gravacao = None
loop_reproducao = False
reproduzindo_loop = False 
instrumento_atual = "escova"
bpm_atual = 120  # Valor padrão

midi_to_note = {
    60: "C", 61: "C#", 62: "D", 63: "D#", 64: "E", 
    65: "F", 66: "F#", 67: "G", 68: "G#", 69: "A", 
    70: "A#", 71: "B", 72: "C", 73: "C#", 74: "D",
    75: "D#", 76: "E", 77: "F", 78: "F#", 79: "G",
    80: "G#", 81: "A", 82: "A#", 83: "B", 84: "C"
}


# |||| FUNÇÕES ||||

def enviar_comando(comando):
    print(f"Comando enviado para Arduino: {comando}")
    arduino.write((comando + '\n').encode())

# Função para salvar eventos em json
def salvar_eventos():
    dados = {"notas": eventos_notas, "batidas": eventos_batidas}
    print(f"Salvando eventos: {dados}")
    with open("eventos.json", "w") as arquivo:
        json.dump(dados, arquivo)
    print("Gravação salva em 'eventos.json'")

# Função para alternar gravação
def alternar_gravacao(botao, faixa, cor_original):
    global gravando, eventos_notas, eventos_batidas, inicio_gravacao, gravando_faixa, loop_reproducao

    canvas.itemconfig(botao, fill="white")
    canvas.after(100, lambda: canvas.itemconfig(botao, fill=cor_original))

    if gravando and gravando_faixa == faixa:
        print(f"Gravação de {faixa} finalizada.")
        gravando = False
        loop_reproducao = False  # Para a reprodução em loop
        salvar_eventos()
    else:
        print(f"Gravando {faixa}...")

        gravando = True
        gravando_faixa = faixa
        if faixa == "notas":
            eventos_notas.clear()
        elif faixa == "batidas":
            eventos_batidas.clear()
        inicio_gravacao = time.time()

        # Inicia a reprodução da outra faixa em loop
        outra_faixa = "batidas" if faixa == "notas" else "teclas"
        thread_reproducao = threading.Thread(target=reproduzir_eventos_em_loop, args=(outra_faixa,))
        thread_reproducao.start()
        

# Função para registrar eventos
def registrar_evento(nota, acao, tipo="nota"):
    if gravando:
        tempo = time.time() - inicio_gravacao
        evento = {"nota": nota, "acao": acao, "tempo": tempo, "tipo": tipo, "instrumento": instrumento_atual}
        if gravando_faixa == "notas":
            eventos_notas.append(evento)
        elif gravando_faixa == "batidas":
            eventos_batidas.append(evento)

# Função para tocar uma nota
def tocar_nota(nota):
    player.note_on(nota, 127)

# Função para parar uma nota
def parar_nota(nota):
    player.note_off(nota, 127)

# Função para tocar uma batida
def tocar_batida(nota):
    player.write_short(0x99, nota, 127)
    player.write_short(0x89, nota, 0)

# Função para ajustar o BPM
def ajustar_bpm():
    global bpm_atual
    try:
        novo_bpm = int(entry_bpm.get())
        if 0 <= novo_bpm <= 300:  # Intervalo de BPM razoável
            bpm_atual = novo_bpm
            print(f"BPM ajustado para: {bpm_atual}")
        else:
            print("Erro: O BPM deve estar entre 40 e 300.")
    except ValueError:
        print("Erro: Digite um número válido para o BPM.")

# ||||| FUNÇÕES DE REPRODUÇÃO |||||
# Função para reproduzir eventos
def reproduzir_eventos(tipo):
    try:
        # Carregando o arquivo JSON
        with open("eventos.json", "r") as arquivo:
            dados = json.load(arquivo)

        # Validar formato dos dados
        if not isinstance(dados, dict):
            print("Erro: O arquivo JSON não contém um dicionário válido.")
            return

        # Seleciona eventos com base no tipo
        eventos = []
        if tipo == "teclas":
            eventos = dados.get("notas", [])  # Usar .get evita KeyError
        elif tipo == "batidas":
            eventos = dados.get("batidas", [])
        elif tipo == "ambos":
            eventos = dados.get("notas", []) + dados.get("batidas", [])
            eventos.sort(key=lambda e: e["tempo"])  # Ordena eventos pelo tempo

        # Verificar se há eventos carregados
        if not eventos:
            print(f"Nenhum evento encontrado para o tipo '{tipo}'.")
            return

        print(f"Reproduzindo {tipo}...")

        # Função para tocar os eventos de forma assíncrona
        def tocar_evento(indice):
            if indice < len(eventos):
                evento = eventos[indice]
                executar_evento(evento)

                # Agendar o próximo evento com base no tempo
                if indice + 1 < len(eventos):
                    proximo_tempo = eventos[indice + 1]["tempo"]
                    delay = int((proximo_tempo - evento["tempo"]) * 1000)  # Tempo em milissegundos
                    canvas.after(delay, lambda: tocar_evento(indice + 1))

        # Inicia a reprodução do primeiro evento
        tocar_evento(0)

    except FileNotFoundError:
        print("Erro: Nenhuma gravação encontrada.")
    except json.JSONDecodeError:
        print("Erro: O arquivo JSON está corrompido ou contém dados inválidos.")

# Função para reproduzir eventos (em loop)
def reproduzir_eventos_em_loop(tipo):
    global loop_reproducao

    try:
        with open("eventos.json", "r") as arquivo:
            dados = json.load(arquivo)

        # Selecionar eventos com base no tipo
        eventos = []
        if tipo == "teclas":
            eventos = dados.get("notas", [])
        elif tipo == "batidas":
            eventos = dados.get("batidas", [])
        elif tipo == "ambos":
            eventos = dados.get("notas", []) + dados.get("batidas", [])
            eventos.sort(key=lambda e: e["tempo"])  # Ordenar por tempo

        if not eventos:
            print(f"Nenhuma gravação encontrada para o tipo '{tipo}'.")
            return

        print(f"Iniciando reprodução em loop da faixa '{tipo}'...")

        # Função de loop para reproduzir os eventos
        def tocar_loop(indice):
            global loop_reproducao
            if not loop_reproducao:
                return

            if indice < len(eventos):
                evento = eventos[indice]
                executar_evento(evento)

                # Calcular o tempo até o próximo evento
                if indice + 1 < len(eventos):
                    proximo_tempo = eventos[indice + 1]["tempo"]
                else:
                    proximo_tempo = eventos[0]["tempo"] + eventos[-1]["tempo"]

                delay = int((proximo_tempo - evento["tempo"]) * 1000)
                canvas.after(delay, lambda: tocar_loop((indice + 1) % len(eventos)))  # Reinicia no índice 0
            else:
                # Reiniciar o loop
                canvas.after(1, lambda: tocar_loop(0))

        # Começar a reprodução do loop
        loop_reproducao = True
        tocar_loop(0)

    except FileNotFoundError:
        print(f"Erro: Nenhuma gravação encontrada para o tipo '{tipo}'.")

# ... Eventos porém no serial do arduíno
def reproduzir_eventos_serial():
    try:
        with open("eventos.json", "r") as arquivo:
            dados = json.load(arquivo)

        # Validar formato dos dados
        if not isinstance(dados, dict):
            print("Erro: O arquivo JSON não contém um dicionário válido.")
            return

        eventos = dados.get("notas", []) + dados.get("batidas", [])
        eventos.sort(key=lambda e: e["tempo"])  # Ordena eventos pelo tempo

        if not eventos:
            print("Nenhum evento encontrado para reprodução.")
            return

        print(f"Reproduzindo todas as faixas...")
        print(f"Reproduzindo todas as faixas com BPM {bpm_atual}...")

        # Envia o BPM primeiro
        enviar_comando(f"bpm:{bpm_atual}")

        # Função para reproduzir eventos
        def tocar_evento(indice):
            if indice < len(eventos):
                evento = eventos[indice]
                executar_evento_ard(evento)  # Envia comando pro Arduino

                # Verifica se este é o último evento
                if indice + 1 == len(eventos):
                    # Agendar o comando "desliga" após o último evento
                    canvas.after(1000, lambda: enviar_comando("desliga"))  # Aguarda 1 segundo
                else:
                    # Agendar o próximo evento com base no tempo
                    proximo_tempo = eventos[indice + 1]["tempo"]
                    delay = int((proximo_tempo - evento["tempo"]) * 1000)  # Tempo em milissegundos
                    canvas.after(delay, lambda: tocar_evento(indice + 1))

        # Inicia a reprodução do primeiro evento
        tocar_evento(0)

    except FileNotFoundError:
        print("Erro: Nenhuma gravação encontrada.")
    except json.JSONDecodeError:
        print("Erro: O arquivo JSON está corrompido ou contém dados inválidos.")

# Função para executar eventos no Arduino
def executar_evento_ard(evento):
    nota_nome = midi_to_note.get(evento["nota"], "unknown")  # Obtem o nome da nota
    if evento["tipo"] == "batida":
        enviar_comando(f"batida_{nota_nome}")  # Ex: batida_C
    elif evento["tipo"] == "nota":
        if evento["acao"] == "on":
            enviar_comando(f"nota_on_{evento['instrumento']}_{nota_nome}")  # Ex: escova_on_C
        elif evento["acao"] == "off":
            enviar_comando(f"nota_off_{evento['instrumento']}_{nota_nome}")  # Ex: escova_off_C


# Função para executar eventos (nota ou batida)
def executar_evento(evento):
    if evento["tipo"] == "batida":
        if evento["acao"] == "on":
            tocar_batida(evento["nota"])
    elif evento["tipo"] == "nota":
        if evento["acao"] == "on":
            tocar_nota(evento["nota"])
        elif evento["acao"] == "off":
            parar_nota(evento["nota"])

# Função para criar uma tecla e associar o som
def criar_tecla(canvas, x, y, largura, altura, cor, nota=None):
    tecla = canvas.create_rectangle(x, y, x + largura, y + altura, fill=cor, outline="black", width=2)
    if nota is not None:
        # Associando eventos para tocar e parar a nota
        canvas.tag_bind(tecla, "<ButtonPress-1>", lambda event: pressionar_tecla(canvas, tecla, cor, nota))
        canvas.tag_bind(tecla, "<ButtonRelease-1>", lambda event: soltar_tecla(canvas, tecla, cor, nota))
    return tecla

# Funções de evento ao pressionar uma tecla ou botão de batida
def pressionar_tecla(canvas, tecla, cor_original, nota):
    registrar_evento(nota, "on", tipo="nota")
    tocar_nota(nota)
    canvas.itemconfig(tecla, fill="gray")
    

def soltar_tecla(canvas, tecla, cor_original, nota):
    registrar_evento(nota, "off", tipo="nota")
    parar_nota(nota)
    canvas.itemconfig(tecla, fill=cor_original)  # Restaura a cor original da tecla
    

def pressionar_batida(nota, botao, cor_original):
    registrar_evento(nota, "on", tipo="batida")
    canvas.itemconfig(botao, fill="white")
    canvas.after(100, lambda: canvas.itemconfig(botao, fill=cor_original))  # Restaura a cor original do botão depois de 100ms
    tocar_batida(nota)

# Função para criar botões de batida
def criar_botao_som(canvas, x, y, raio, cor, nota):
    botao = canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=cor, outline="black")
    canvas.tag_bind(botao, "<Button-1>", lambda event: pressionar_batida(nota, botao, cor))

def alterar_instrumento(instrumento, botao, cor_original):
    global instrumento_atual
    instrumento_atual = instrumento
    print(f"Instrumento alterado para: {instrumento}")
    canvas.itemconfig(botao, fill="white")
    canvas.after(100, lambda: canvas.itemconfig(botao, fill=cor_original))

# |||| INTERFACE ||||

# Configuração da janela principal
janela = tk.Tk()
janela.title("Tecladinho")

# Configuração do Canvas
canvas = tk.Canvas(janela, width=800, height=200, bg="#555555")
canvas.pack()

# Corpo do teclado
corpo_teclado = canvas.create_rectangle(20, 20, 750, 180, fill="black", outline="black", width=2)

# Botões de batida
criar_botao_som(canvas, 40, 50, 15, "blue", 64) # IMPRESSORA
criar_botao_som(canvas, 80, 50, 15, "green", 62) # DVD
# criar_botao_som(canvas, 120, 50, 15, "purple", 66)

# BOTÕES 
# Botão Desliga
botao_desliga = canvas.create_oval(365, 25, 415, 60, fill="red", outline="red")  # Coordenadas ajustadas para centralizar
canvas.tag_bind(
    botao_desliga,
    "<Button-1>",
    lambda _: enviar_comando("desliga")
)
canvas.tag_bind(
    canvas.create_text(390, 43, text="DESLIGA", fill="white"),
    "<Button-1>",
    lambda _: enviar_comando("desliga")
)

# Botão REC Notas - faixa 2
botao_rec_notas = canvas.create_oval(600, 30, 630, 60, fill="red", outline="red")
canvas.tag_bind(
    canvas.create_text(615, 45, text="REC N", fill="white"),
    "<Button-1>",
    lambda _: alternar_gravacao(botao_rec_notas, "notas", "red")
)
canvas.tag_bind(
    botao_rec_notas,
    "<Button-1>",
    lambda _: alternar_gravacao(botao_rec_notas, "notas", "red")
)

# Botão REC Batidas - faixa 2
botao_rec_batidas = canvas.create_oval(640, 30, 670, 60, fill="orange", outline="orange")
canvas.tag_bind(
    canvas.create_text(655, 45, text="REC B", fill="white"),
    "<Button-1>",
    lambda _: alternar_gravacao(botao_rec_batidas, "batidas", "orange")
)
canvas.tag_bind(
    botao_rec_batidas,
    "<Button-1>",
    lambda _: alternar_gravacao(botao_rec_batidas, "batidas", "orange")
)

# Botão PLAY Notas - faixa 1
botao_play_notas = canvas.create_rectangle(590, 70, 630, 100, fill="green", outline="green")
canvas.tag_bind(
    canvas.create_text(610, 85, text="NOTAS", fill="white"),
    "<Button-1>",
    lambda _: reproduzir_eventos("teclas")
)
canvas.tag_bind(
    botao_play_notas,
    "<Button-1>",
    lambda _: reproduzir_eventos("teclas")
)

# Botão PLAY Batidas - faixa 2
botao_play_batidas = canvas.create_rectangle(640, 70, 680, 100, fill="blue", outline="blue")
canvas.tag_bind(
    canvas.create_text(660, 85, text="BATIDAS", fill="white"),
    "<Button-1>",
    lambda _: reproduzir_eventos("batidas")
)
canvas.tag_bind(
    botao_play_batidas,
    "<Button-1>",
    lambda _: reproduzir_eventos("batidas")
)

# Botão PLAY Ambos - faixa 1 e 2
botao_play_ambos = canvas.create_rectangle(690, 70, 730, 100, fill="purple", outline="purple")
canvas.tag_bind(
    canvas.create_text(710, 85, text="AMBAS", fill="white"),
    "<Button-1>",
    lambda _: reproduzir_eventos("ambos")
)
canvas.tag_bind(
    botao_play_ambos,
    "<Button-1>",
    lambda _: reproduzir_eventos("ambos")
)

# Botão PLAY no serial do arduino
botao_play_serial = canvas.create_rectangle(690, 30, 730, 60, fill="blue", outline="blue")
canvas.tag_bind(
    canvas.create_text(710, 45, text="SERIAL", fill="white"),
    "<Button-1>",
    lambda _: reproduzir_eventos_serial()
)

canvas.tag_bind(
    botao_play_serial,
    "<Button-1>",
    lambda _: reproduzir_eventos_serial()
)

# Botões de instrumentos

# I1
botao_instrumento_1 = canvas.create_rectangle(20, 70, 100, 95, fill="yellow")
canvas.tag_bind(
    botao_instrumento_1,
    "<Button-1>",
    lambda _: alterar_instrumento("escova", botao_instrumento_1, "yellow")
)
canvas.tag_bind(
    canvas.create_text(60, 83, text="Instrumento 1", fill="black"),
    "<Button-1>",
    lambda _: alterar_instrumento("escova", botao_instrumento_1, "yellow")
)

# I2
botao_instrumento_2 = canvas.create_rectangle(120, 70, 200, 95, fill="orange")
canvas.tag_bind(
    botao_instrumento_2,
    "<Button-1>",
    lambda _: alterar_instrumento("liqui", botao_instrumento_2, "orange")
)
canvas.tag_bind(
    canvas.create_text(160, 83, text="Instrumento 2", fill="black"),
    "<Button-1>",
    lambda _: alterar_instrumento("liqui", botao_instrumento_2, "orange")
)

# AJUSTE DE BPM
label_bpm = tk.Label(janela, text="BPM:", bg="#555555", fg="white", font=("Arial", 10))
label_bpm.place(x=20, y=10)  # Posição no topo da interface

entry_bpm = tk.Entry(janela, width=5)
entry_bpm.place(x=60, y=10)
entry_bpm.insert(0, "120")  # Valor inicial

botao_ajustar_bpm = tk.Button(janela, text="Ajustar BPM", command=ajustar_bpm)
botao_ajustar_bpm.place(x=100, y=5)

# Botões BPM

botao_bpm_120 = canvas.create_rectangle(100, 35, 150, 65, fill="white", outline="black")
canvas.tag_bind(
    botao_bpm_120,
    "<Button-1>",
    lambda _: enviar_comando("bpm:180")
)
canvas.tag_bind(
    canvas.create_text(125, 50, text="BPM 180", fill="black"),
    "<Button-1>",
    lambda _: enviar_comando("bpm:180")
)

botao_bpm_150 = canvas.create_rectangle(160, 35, 210, 65, fill="white", outline="black")
canvas.tag_bind(
    botao_bpm_150,
    "<Button-1>",
    lambda _: enviar_comando("bpm:150")
)
canvas.tag_bind(
    canvas.create_text(185, 50, text="BPM 150", fill="black"),
    "<Button-1>",
    lambda _: enviar_comando("bpm:150")
)

botao_bpm_180 = canvas.create_rectangle(220, 35, 270, 65, fill="white", outline="black")
canvas.tag_bind(
    botao_bpm_180,
    "<Button-1>",
    lambda _: enviar_comando("bpm:120")
)
canvas.tag_bind(
    canvas.create_text(245, 50, text="BPM 120", fill="black"),
    "<Button-1>",
    lambda _: enviar_comando("bpm:120")
)

# |||| TECLAS ||||

# Notas das teclas brancas
notas_brancas = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]
tecla_largura = 40
tecla_altura = 80
for i, nota in enumerate(notas_brancas):
    criar_tecla(canvas, 30 + i * tecla_largura, 100, tecla_largura, tecla_altura, "white", nota=nota)

# Notas das teclas pretas
notas_pretas = [61, 63, None, 66, 68, 70, None, 73, 75, None, 78, 80, 82]
tecla_preta_largura = 20
tecla_preta_altura = 50
offset = 30 + tecla_largura - (tecla_preta_largura / 2)
for i, nota in enumerate(notas_pretas):
    if nota:  # Pula o espaço entre mi e fá
        criar_tecla(canvas, offset + i * tecla_largura, 100, tecla_preta_largura, tecla_preta_altura, "black", nota=nota)

# Iniciando a interface
janela.mainloop()
