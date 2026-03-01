# MLX Installation Guide

MLX est nécessaire uniquement pour la représentation graphique (jbarthel). L'installation se fait manuellement car les wheels fournis peuvent être incompatibles avec certaines versions de Python.

## Méthode 1: Wheel pré-compilé (si compatible)

```bash
# Dans votre venv activé
pip install ./mlx-2.2-py3-ubuntu-any.whl
```

Si erreur "not a supported wheel", passez à la méthode 2.

## Méthode 2: Compilation depuis sources

```bash
# Extraire l'archive
tar -xzf mlx_CLXV-2.2.tgz
cd mlx_CLXV/python

# Installer depuis le dossier Python
pip install .
```

## Vérification

```bash
python3 -c "import mlx; print('MLX importé avec succès')"
```

## Notes

- MLX est optionnel en phase de développement initial
- Nécessaire uniquement pour la partie graphique (semaine 2)
- L'ASCII rendering (oguizol) ne nécessite pas MLX
