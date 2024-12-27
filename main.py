import tkinter as tk
from tkinter import ttk, messagebox, StringVar, DoubleVar, filedialog
import math
import scipy.stats as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Fonctions de pricing d'options (placées avant l'interface Tkinter)
def binomial_option_price(S, K, T, r, sigma, N, option_type="call"):
    dt = T / N
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    p = (math.exp(r * dt) - d) / (u - d)

    option_values = [[0.0 for j in range(i + 1)] for i in range(N + 1)]

    for j in range(N + 1):
        if option_type == "call":
            option_values[N][j] = max(0, S * (u ** (N - j)) * (d ** j) - K)
        elif option_type == "put":
            option_values[N][j] = max(0, K - S * (u ** (N - j)) * (d ** j))
        else:
            raise ValueError("Type d'option non valide. Utilisez 'call' ou 'put'.")

    for i in range(N - 1, -1, -1):
        for j in range(i + 1):
            option_values[i][j] = math.exp(-r * dt) * (p * option_values[i + 1][j] + (1 - p) * option_values[i + 1][j + 1])

    return option_values[0][0]

def black_scholes_option_price(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type == "call":
        price = S * st.norm.cdf(d1) - K * math.exp(-r * T) * st.norm.cdf(d2)
    elif option_type == "put":
        price = K * math.exp(-r * T) * st.norm.cdf(-d2) - S * st.norm.cdf(-d1)
    else:
        raise ValueError("Type d'option non valide. Utilisez 'call' ou 'put'.")

    return price

# Interface Tkinter
fenetre = tk.Tk()
fenetre.title("Calculateur de prix d'options")

# Variables Tkinter
entry_S = DoubleVar()
entry_K = DoubleVar()
entry_T = DoubleVar()
entry_r = DoubleVar()
entry_sigma = DoubleVar()
entry_N = StringVar()
resultat_binomial = StringVar()
resultat_black_scholes = StringVar()
option_var = StringVar(value="Call")

# Fonctions d'interaction
def calculer():
    try:
        S = float(entry_S.get())
        K = float(entry_K.get())
        T = float(entry_T.get())
        r = float(entry_r.get())
        sigma = float(entry_sigma.get())
        N = int(entry_N.get())
        option_type = option_var.get().lower()

        if S <= 0 or K <= 0 or T <= 0 or sigma <= 0 or N <= 0:
            raise ValueError("Les valeurs doivent être positives.")
        if r < 0:
            raise ValueError("Le taux d'intérêt doit être positif ou nul.")

        binomial_price = binomial_option_price(S, K, T, r, sigma, N, option_type)
        black_scholes_price = black_scholes_option_price(S, K, T, r, sigma, option_type)

        resultat_binomial.set(f"{binomial_price:.2f}")
        resultat_black_scholes.set(f"{black_scholes_price:.2f}")

    except ValueError as e:
        messagebox.showerror("Erreur", str(e))

def charger_donnees():
    try:
        filepath = filedialog.askopenfilename(title="Charger un fichier CSV", filetypes=[("Fichiers CSV", "*.csv")])
        if filepath:
            df = pd.read_csv(filepath)

            volatility = df['Close'].pct_change().std() * math.sqrt(252)
            entry_sigma.set(volatility)

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(df["Close"])
            ax.set_title("Cours de l'actif")
            ax.set_xlabel("Temps")
            ax.set_ylabel("Prix")

            canvas = FigureCanvasTkAgg(fig, master=fenetre)
            canvas.draw()
            canvas.get_tk_widget().grid(row=9, column=0, columnspan=2)

    except FileNotFoundError:
        messagebox.showerror("Erreur", "Fichier non trouvé.")
    except KeyError:
        messagebox.showerror("Erreur", "Le fichier CSV doit contenir une colonne 'Close'.")
    except Exception as e:
        messagebox.showerror("Erreur lors du chargement des données", str(e))

# Création des éléments Tkinter
ttk.Label(fenetre, text="Prix de l'actif (S):").grid(row=0, column=0, sticky="w")
ttk.Entry(fenetre, textvariable=entry_S).grid(row=0, column=1)
ttk.Label(fenetre, text="Prix d'exercice (K):").grid(row=1, column=0, sticky="w")
ttk.Entry(fenetre, textvariable=entry_K).grid(row=1, column=1)
ttk.Label(fenetre, text="Temps jusqu'à l'échéance (T):").grid(row=2, column=0, sticky="w")
ttk.Entry(fenetre, textvariable=entry_T).grid(row=2, column=1)
ttk.Label(fenetre, text="Taux sans risque (r):").grid(row=3, column=0, sticky="w")
ttk.Entry(fenetre, textvariable=entry_r).grid(row=3, column=1)
ttk.Label(fenetre, text="Volatilité (sigma):").grid(row=4, column=0, sticky="w")
ttk.Entry(fenetre, textvariable=entry_sigma).grid(row=4, column=1)
ttk.Label(fenetre, text="Nombre de périodes (N):").grid(row=5, column=0, sticky="w")
ttk.Entry(fenetre, textvariable=entry_N).grid(row=5, column=1)

ttk.Label(fenetre, text="Type d'option:").grid(row=6, column=0, sticky="w")
ttk.Radiobutton(fenetre, text="Call", variable=option_var, value="Call").grid(row=6, column=1, sticky="w")
ttk.Radiobutton(fenetre, text="Put", variable=option_var, value="Put").grid(row=7, column=1, sticky="w")

ttk.Button(fenetre, text="Calculer", command=calculer).grid(row=8, column=0, columnspan=2)
ttk.Button(fenetre, text="Charger données (CSV)", command=charger_donnees).grid(row=10, column=0, columnspan=2)

ttk.Label(fenetre, text="Prix binomial:").grid(row=11, column=0, sticky="w")
ttk.Label(fenetre, textvariable=resultat_binomial).grid(row=11, column=1)
ttk.Label(fenetre, text="Prix Black-Scholes:").grid(row=12, column=0, sticky="w")
ttk.Label(fenetre, textvariable=resultat_black_scholes).grid(row=12, column=1)

fenetre.mainloop()