# Igor KITT - Knight Rider App

App nativa Android/Windows con interfaz estilo KITT (Knight Rider).

## En Windows
Ejecuta `Iniciar KITT App.bat` o:
```
D:\OpenJarvis\.venv\Scripts\python.exe main.py
```

## Generar APK Android

### Opción 1: Google Colab (recomendado)
1. Abre: https://colab.research.google.com/
2. Crea un nuevo notebook
3. Ejecuta:
```python
!pip install buildozer cython
!git clone https://github.com/tuusuario/igorkitt.git
%cd igorkitt/app_kitt
!buildozer android debug
```
4. Descarga el APK de `bin/igorkitt-*.apk`

### Opción 2: GitHub Actions
1. Sube el código a GitHub
2. Ve a Actions → "Build Igor KITT APK" → Run workflow
3. Descarga el artifact generado

### Opción 3: WSL (Windows)
```bash
# Desde PowerShell como admin
wsl --install Ubuntu
wsl
# Dentro de Ubuntu:
sudo apt update && sudo apt install -y python3-pip git
pip install buildozer cython
cd /mnt/d/OpenJarvis/app_kitt
buildozer android debug
```
