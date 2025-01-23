import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

# Variáveis globais para armazenar os descritores da imagem registrada e o nível de autenticação
imagem_registrada_descritores = None
nivel_autenticacao_registrado = None

# Dicionário para mensagens personalizadas por nível de autenticação
mensagens_nivel = {
    1: "Bem-vindo! Você tem acesso ao Nível 1. Aproveite!",
    2: "Acesso ao Nível 2 concedido. Bem-vindo diretor de divisão.",
    3: "Acesso ao Nível 3 concedido. Bem-vindo ministro."
}


def carregar_imagem():
    caminho_imagem = filedialog.askopenfilename(
        title="Selecione a imagem de impressão digital para autenticação")
    if caminho_imagem:
        imagem = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
        cv2.imshow("Imagem Original (Aquisição)", imagem)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        imagem_processada = pre_processamento(imagem)
        verificar_autenticacao(imagem_processada)


def pre_processamento(imagem):
    """Etapas de pré-processamento: suavização, binarização e segmentação."""
    # Suavização para reduzir ruído
    imagem_suavizada = cv2.GaussianBlur(imagem, (5, 5), 0)
    cv2.imshow("Imagem Suavizada", imagem_suavizada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Binarização
    _, imagem_binarizada = cv2.threshold(
        imagem_suavizada, 127, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("Imagem Binarizada", imagem_binarizada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Segmentação: Detectar contornos
    contornos, _ = cv2.findContours(
        imagem_binarizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    imagem_segmentada = np.zeros_like(imagem_binarizada)
    cv2.drawContours(imagem_segmentada, contornos, -
                     1, (255), thickness=cv2.FILLED)
    cv2.imshow("Imagem Segmentada", imagem_segmentada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return imagem_segmentada


def extrair_caracteristicas(imagem):
    """Extrai características da imagem usando ORB."""
    orb = cv2.ORB_create()
    keypoints, descritores = orb.detectAndCompute(imagem, None)
    if descritores is None:
        messagebox.showerror(
            "Erro", "Falha ao extrair características da imagem.")
        return None, None
    imagem_com_pontos = cv2.drawKeypoints(imagem, keypoints, None, color=(
        0, 255, 0), flags=cv2.DrawMatchesFlags_DRAW_RICH_KEYPOINTS)
    cv2.imshow(
        "Imagem com Pontos-Chave (Extração de Características)", imagem_com_pontos)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return keypoints, descritores


def registrar_imagem():
    global imagem_registrada_descritores, nivel_autenticacao_registrado
    caminho_imagem = filedialog.askopenfilename(
        title="Selecione a imagem de impressão digital para registro")
    if caminho_imagem:
        imagem = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
        imagem_processada = pre_processamento(imagem)
        _, imagem_registrada_descritores = extrair_caracteristicas(
            imagem_processada)

        if imagem_registrada_descritores is not None:
            nivel_autenticacao_registrado = int(nivel_var.get())
            resultado_label.config(text=f"Imagem registrada com sucesso no nível {
                                   nivel_autenticacao_registrado}!", fg="green", font=("Helvetica", 13, "italic"))
        else:
            resultado_label.config(
                text="Erro ao registrar a imagem.", fg="red", font=("Helvetica", 13, "italic"))


def verificar_autenticacao(imagem):
    global imagem_registrada_descritores, nivel_autenticacao_registrado
    resultado_label.config(text="", fg="white",
                           font=("Helvetica", 13, "italic"))

    if imagem_registrada_descritores is None:
        resultado_label.config(text="Acesso negado", fg="red")
        return

    _, descritores = extrair_caracteristicas(imagem)
    if descritores is None:
        resultado_label.config(text="Acesso negado", fg="red")
        return

    # Verificação de correspondência de características
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descritores, imagem_registrada_descritores)
    num_matches = len(matches)
    distancia_media = np.mean(
        [match.distance for match in matches]) if matches else float('inf')

    # Limites de correspondência para os níveis
    requisitos_nivel = {1: (30, 40), 2: (50, 30), 3: (70, 20)}
    num_min, dist_max = requisitos_nivel.get(
        nivel_autenticacao_registrado, (30, 40))

    # Verificação do nível solicitado pelo usuário
    nivel_solicitado = int(nivel_var.get())
    if nivel_solicitado != nivel_autenticacao_registrado:
        resultado_label.config(text="Acesso negado", fg="red")
        return

    # Verificação da correspondência com os limites do nível registrado
    if num_matches > num_min and distancia_media < dist_max:
        mensagem_personalizada = mensagens_nivel.get(
            nivel_solicitado, "Acesso permitido.")
        resultado_label.config(text=mensagem_personalizada, fg="green")
    else:
        resultado_label.config(text="Acesso negado", fg="red")


# Interface principal
janela = tk.Tk()
janela.title("Autenticação Biométrica")
janela.geometry("960x540")
janela.configure(bg="white")

# Frame e imagem de fundo
frame_imagem = tk.Frame(janela, bg="white", width=450, height=540)
frame_imagem.grid(row=0, column=0, sticky="nsew")

try:
    imagem = Image.open("C:/Users/helos/Downloads/padraoimg.jpeg")
    imagem = imagem.resize((450, 540),  Image.Resampling.LANCZOS)
    imagem_tk = ImageTk.PhotoImage(imagem)
    label_imagem = tk.Label(frame_imagem, image=imagem_tk, bg="white")
    label_imagem.image = imagem_tk
    label_imagem.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    messagebox.showerror("Erro", f"Não foi possível carregar a imagem: {e}")

# Frame de autenticação
frame_direito = tk.Frame(janela, bg="white", width=510, height=540)
frame_direito.grid(row=0, column=1, sticky="nsew", padx=20)
label_titulo = tk.Label(frame_direito, text="Bem-Vindo!",
                        font=("Arial", 50, "bold"), bg="white", fg="#1f6a30")
label_titulo.pack(pady=(80, 10), anchor="center")
label_subtitulo = tk.Label(frame_direito, text="Autenticação Biométrica", font=(
    "Arial", 14), bg="white", fg="#A3D9A5")
label_subtitulo.pack(anchor="center")

# Botão de registro e opção de nível
nivel_var = tk.IntVar(value=1)
nivel_label = tk.Label(frame_direito, text="Escolha o Nível de Autenticação:", font=(
    "Arial", 12), bg="white", fg="#1f6a30")
nivel_label.pack(pady=(5, 5))
for nivel in [1, 2, 3]:
    tk.Radiobutton(frame_direito, text=f"Nível {nivel}", variable=nivel_var, value=nivel, font=(
        "Arial", 12), bg="white", fg="#1f6a30").pack(anchor="w")

btn_registrar = tk.Button(frame_direito, text="Registrar Impressão Digital", font=(
    "Arial", 14), bg="#A3D9A5", fg="#1f6a30", command=registrar_imagem)
btn_registrar.pack(pady=(10, 10))

# Botão de autenticação
btn_autenticar = tk.Button(frame_direito, text="Autenticar Impressão Digital", font=(
    "Arial", 14), bg="#A3D9A5", fg="#1f6a30", command=carregar_imagem)
btn_autenticar.pack(pady=(10, 10))

resultado_label = tk.Label(frame_direito, text="", font=(
    "Helvetica", 13, "italic"), bg="white")
resultado_label.pack(pady=(10, 10))

janela.mainloop()
