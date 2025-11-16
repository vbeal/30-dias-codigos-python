# ################################################
# 🎯 Projeto: Fogos de Artifício com Turtle
# ################################################
# 📁 Caminho: dia-5/dia05_fogos_artificio_turtle.py
# Desafio 30 dias com Python por Victor Beal
# ################################################
import turtle
import random

# Configurações da tela
tela = turtle.Screen()
tela.bgcolor("black")
tela.title("🎆 Fogos de Artifício com Python")
tela.setup(width=800, height=600)

# Tartaruga única
t = turtle.Turtle()
t.hideturtle()
t.speed(0)

# Cores válidas
cores = ["red", "yellow", "orange", "blue", "magenta", "white", "green"]

# Função para desenhar um fogo
def fogo():
    t.clear()
    x = random.randint(-300, 300)
    y = random.randint(-200, 200)
    t.penup()
    t.goto(x, y)
    t.pendown()
    for _ in range(36):
        t.color(random.choice(cores))
        t.forward(100)
        t.backward(100)
        t.left(10)

# Disparar fogos em sequência
def sequencia_fogos(n):
    if n > 0:
        fogo()
        tela.ontimer(lambda: sequencia_fogos(n - 1), 1000)
    else:
        tela.exitonclick()

# Iniciar sequência
sequencia_fogos(5)
tela.mainloop()



