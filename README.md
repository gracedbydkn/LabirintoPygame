# 🏚️ Lost in Maze

**Lost in Maze** é um jogo de exploração e furtividade em tema *dark fantasy*, desenvolvido em Python com Pygame. O jogador deve navegar por catacumbas sombrias, fugir de inimigos controlados por inteligência artificial, coletar itens e encontrar a saída sem ser capturado.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-008000?style=for-the-badge&logo=python&logoColor=white)

---

## 🎮 Sobre o Jogo

Perdido nas catacumbas de uma masmorra esquecida, o jogador enfrenta criaturas que patrulham os corredores usando inteligência artificial com pathfinding A\*. A névoa limita o campo de visão, exigindo cautela a cada passo. Use o ambiente a seu favor: esconda-se em barris, quebre vasos para distrair inimigos e colete runas para destravar barreiras mágicas. Encontre a chave e chegue à porta de saída antes que eles te encontrem.

![Início do Jogo](https://github.com/user-attachments/assets/e816331c-7c17-4d67-a447-d2f5b75494b8)

![Zumbi](https://github.com/user-attachments/assets/686372ef-52d8-468d-87c1-3a70eb9fd865)



---

## ✨ Funcionalidades

- **Névoa**: campo de visão dinâmico com iluminação suave ao redor do jogador e das tochas
- **IA dos Inimigos**: zumbi e troll com máquina de estados (patrulha, investigação, perseguição) e pathfinding A\*
- **Detecção por Som**: quebrar vasos alerta o inimigo mais próximo dentro de um raio configurável
- **Sistema de Stamina**: correr drena stamina; o jogador fica exausto se a esgota completamente
- **Esconderijos**: o jogador pode se esconder em barris para enganar os inimigos
- **Itens**: runas, chaves e barreiras mágicas compõem um mini sistema de puzzle
- **HUD**: exibe stamina, itens e dicas de teclas contextuais
- **Suporte a Controle**: compatível com gamepads (Xbox / PlayStation)
- **Áudio Ambiente**: trilha e efeitos sonoros (quebrar vasos, entrar em barris)
- **Mapa TMX**: cenário carregado a partir de arquivo Tiled (.tmx) com múltiplas camadas

---

## ⚙️ Requisitos

- Python 3.10+
- Pygame
- pytmx
- pathfinding

---

## 🚀 Como Executar

**1. Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/LabirintoPygame.git
cd LabirintoPygame
```

**2. Instale as dependências:**

```bash
pip install pygame pytmx pathfinding
```

**3. Execute o jogo:**

```bash
python main.py
```

---

## 🕹️ Controles

| Ação            | Teclado          | Controle (Xbox/PS)     |
|-----------------|------------------|------------------------|
| Mover           | `W A S D`        | Analógico esquerdo     |
| Correr          | `Shift`          | RB                     |
| Interagir       | `E`              | Botão A / Cruz         |
| Sair do jogo    | `Esc`            | —                      |
| Reiniciar       | `R` (game over)  | —                      |

---

## 🗂️ Estrutura do Projeto

```
LabirintoPygame/
├── main.py                  # Loop principal e inicialização do jogo
├── assets/
│   ├── maps/                # Mapas Tiled (.tmx)
│   ├── characters/          # Spritesheets do jogador, zumbi e troll
│   ├── itens/               # Sprites de vasos, runas, chaves, barreiras, etc.
│   └── audio/               # Trilha ambiente e efeitos sonoros
└── src/
    ├── core/
    │   ├── config.py        # Constantes globais (resolução, FPS, cores, FOV)
    │   └── audio_manager.py # Gerenciador de SFX e música ambiente
    ├── utils/
    │   ├── hud.py           # Desenho do HUD, stamina bar e inventário
    │   └── sprites.py       # Carregamento de spritesheets e frames
    └── world/
        ├── maze.py          # Carregamento e renderização do mapa TMX
        ├── fog.py           # Sistema de Fog of War com raycasting
        ├── env_object.py    # Objetos ambientais animados (tochas)
        ├── entities/
        │   ├── actor.py     # Classe base para entidades móveis
        │   ├── player.py    # Lógica do jogador (movimento, stamina, interação)
        │   ├── enemy.py     # IA do zumbi (A*, FSM, detecção por visão/som)
        │   ├── troll_enemy.py # IA do troll
        │   ├── inventory.py # Sistema de inventário
        │   └── item.py      # Itens coletáveis
        └── objects/
            ├── vaso.py      # Vaso quebrável com loot e notificação sonora
            ├── barreira.py  # Barreira mágica desbloqueável por runa
            ├── esconderijo.py # Barril esconderijo interativo
            └── porta_saida.py # Porta de saída (condição de vitória)
```

---

## 👥 Equipe

Este projeto foi desenvolvido por estudantes da **USJT**:

| Nome              | Papel                        |
|-------------------|------------------------------|
| Pedro da Costa    | Designer e Desenvolvedor     |
| Carlos Freire     | Desenvolvedor                |
| Gabi Danielly     | Desenvolvedora               |
| Márcio Barrocal   | Designer e Desenvolvedor     |
| Pedro Santos      | Desenvolvedor                |
| Gustavo Santana   | Desenvolvedor                |
| Allan Rocha       | Desenvolvedor                |
| Lucas de Claris   | Desenvolvedor                |
| Giovanna Fontes   | Desenvolvedora               |

---

## 📄 Licença

Assets de tileset utilizados sob licença pública — veja `assets/catacombs rogue fantasy/RF_Catacombs_v1.0/public-license.txt` para detalhes.

---

https://www.notion.so/DOCUMENTA-O-DO-PROJETO-A3-Pygame-33bae94f9d4680b08003e2c89e0d1a4a
