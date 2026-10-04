# Reto Opcional: CI/CD para Regenerar Diagramas con Mermaid CLI (+2 Puntos)

> **Lab 04 · Construcción de Software · EPIS-UNSA · Grupo 04**  
> **Consigna:** *"configure una GitHub Action que, en cada push, regenere automáticamente las imágenes PNG de los archivos .mmd usando mermaid-cli."*

Este documento contiene la especificación y el código listo para la GitHub Action que automatiza la regeneración de los diagramas Mermaid al detectar cambios en el repositorio.

---

## 1. Código del Workflow (`.github/workflows/render-diagrams.yml`)

Para activar esta acción en GitHub:
1. En el repositorio de GitHub, navegar a **Add file > Create new file**.
2. Escribir como ruta: `.github/workflows/render-diagrams.yml`.
3. Pegar el siguiente contenido y hacer commit:

```yaml
name: Regenerar Diagramas Mermaid (Reto Opcional)

on:
  push:
    paths:
      - "docs/architecture/diagramas/*.mmd"
      - ".github/workflows/render-diagrams.yml"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  render-mermaid:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout del repositorio
        uses: actions/checkout@v4

      - name: Configurar Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Instalar mermaid-cli
        run: npm install -g @mermaid-js/mermaid-cli

      - name: Renderizar arquitectura.mmd a PNG
        run: |
          mkdir -p docs/architecture/diagramas/img
          mmdc -i docs/architecture/diagramas/arquitectura.mmd -o docs/architecture/diagramas/img/arquitectura.png -t neutral -b white -s 2

      - name: Guardar y subir imagen regenerada
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/architecture/diagramas/img/arquitectura.png
          if ! git diff --cached --quiet; then
            git commit -m "ci: regenerar automaticamente arquitectura.png via mermaid-cli [skip ci]"
            git push
          else
            echo "Sin cambios en el diagrama renderizado."
          fi
```

---

## 2. Explicación del funcionamiento

1. **Disparador selectivo (`paths`):** El workflow solo se ejecuta cuando se modifica el archivo `docs/architecture/diagramas/arquitectura.mmd` o la configuración del workflow, ahorrando minutos de cómputo en GitHub Actions.
2. **Entorno reproducible:** Utiliza un contenedor Ubuntu con Node.js 20 e instala `@mermaid-js/mermaid-cli` de manera global.
3. **Escala idéntica a la guía:** Ejecuta `mmdc` con los parámetros exactos especificados en el README (`-s 2` con escala de Puppeteer y tema neutral), garantizando legibilidad en alta resolución.
4. **Protección contra bucles infinitos:** El commit automático incluye la directiva `[skip ci]`, evitando que el commit generado por el bot vuelva a disparar la acción.
