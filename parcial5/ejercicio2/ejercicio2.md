# Ejercicio 2. Ruta más corta 1 → 13 (versión para escribir a mano)

**Etapas:** E1 {1} · E2 {2,3,4} · E3 {5,6} · E4 {7,8,9} · E5 {10,11} · E6 {12,13}
(las aristas 3-4, 5-6, 7-8, 8-9 y 12-13 unen nodos de la misma etapa y se revisan al final de cada una).

## a. De adelante hacia atrás (desde 1)  f(j) = min{ f(i) + d(i,j) }

| Etapa | Cálculo | Viene de |
|-------|---------|----------|
| E1 | f1 = 0 | — |
| E2 | f2 = 100 · f3 = 50 · f4 = 40 | 1 |
| E3 | f5 = min{200; 150} = 150 · f6 = 140 | 3 · 4 |
| E4 | f7 = 270 · f8 = 280 · f9 = 240 | 5 · 5 · 6 |
| E5 | f10 = min{330; 350} = 330 · f11 = 340 | 7 · 9 |
| E6 | f12 = min{530; 390} = 390 · f13 = min{430; 490} = **430** | 11 · 10 |

**Ruta: 1 → 3 → 5 → 7 → 10 → 13 Total = 430**

## b. De atrás hacia adelante (desde 13)  g(i) = min{ d(i,j) + g(j) }

| Etapa | Cálculo | Va a |
|-------|---------|------|
| E6 | g13 = 0 · g12 = 100 | 13 |
| E5 | g10 = min{300; 100} = 100 · g11 = 150 | 13 · 12 |
| E4 | g7 = 160 · g8 = 170 · g9 = 250 | 10 · 10 · 11 |
| E3 | g5 = min{280; 300} = 280 · g6 = min{350; 40+280} = 320 | 7 · 5 |
| E2 | g2 = 380 · g3 = 380 · g4 = min{420; 20+380} = 400 | 5 · 5 · 3 |
| E1 | g1 = min{480; 430; 440} = **430** | 3 |

**Ruta: 1 → 3 → 5 → 7 → 10 → 13 Total = 430**

## c. Floyd-Warshall y Bellman-Ford (programa `main.py`)

- Floyd-Warshall: D_k[i][j] = min(D[i][j], D[i][k] + D[k][j]) → D[1][13] = 430.
- Bellman-Ford: d(v) = min(d(v), d(u) + w(u,v)), desde el nodo 1 → d(13) = 430 (converge en 2 iteraciones).
- Los dos dan la misma ruta, 1-3-5-7-10-13 = 430, igual que a y b.
- Floyd-Warshall calcula todos los pares en O(n³). Bellman-Ford calcula un solo origen en O(n·m) y admite pesos negativos.
