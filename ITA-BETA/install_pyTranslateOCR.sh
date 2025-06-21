#!/bin/bash

# Mostra la finestra principale dell'installatore
(
    while true; do
        sleep 1
    done
) | zenity --progress --width=600 --height=500 --title="Installatore per pyTranslateOCR by MoonDragon" \
    --text="<b>Installatore per pyTranslateOCR by MoonDragon</b>\n\nVersione: 1.0.0\n\nhttps://github.com/MoonDragon-MD/pyTranslateOCR\n\nSeguirà l'installazione guidata comprese le dipendenze e scorciatoia sul menù" \
    --no-cancel --auto-close --pulsate &

INSTALLER_PID=$!

# Funzione per mostrare un popup con il comando da eseguire
show_command_popup() {
    zenity --error --width=400 --text="Errore: $1 non trovato.\nEsegui il seguente comando:\n\n<b>$2</b>"
}

# Verifica le dipendenze
if ! zenity --question --width=400 --text="Vuoi verificare e installare le dipendenze?"; then
    INSTALL_DEPENDENCIES=false
else
    INSTALL_DEPENDENCIES=true
fi

if [ "$INSTALL_DEPENDENCIES" = true ]; then
    # Verifica Python3
    if ! command -v python3 &> /dev/null; then
        show_command_popup "Python3" "sudo apt-get install python3"
        kill $INSTALLER_PID
        exit 1
    fi

    # Verifica pip
    if ! command -v pip3 &> /dev/null; then
        show_command_popup "pip3" "sudo apt-get install python3-pip"
        kill $INSTALLER_PID
        exit 1
    fi

    # Installa le dipendenze Python
    zenity --info --width=400 --text="Installando le dipendenze Python..."
     pip3 install PyQt5 pyttsx3 pytesseract pillow requests pynput python-xlib googletrans==3.1.0a0 httpx httpcore
fi

# Chiede all'utente dove installare pyTranslateOCR
INSTALL_DIR=$(zenity --file-selection --directory --title="Seleziona la directory di installazione per pyTranslateOCR" --width=400)
if [ -z "$INSTALL_DIR" ]; then
    zenity --error --width=400 --text="Nessuna directory selezionata.\nInstallazione annullata."
    kill $INSTALLER_PID
    exit 1
fi

# Crea il desktop entry
zenity --info --width=400 --text="Creando il collegamento nel menu applicazioni..."
cat > ~/.local/share/applications/pyTranslateOCR.desktop << EOL
[Desktop Entry]
Name=pyTranslateOCR
Comment=Traduttore OCR con sovrimpressione e TTS
Exec=$INSTALL_DIR/pyTranslateOCR/pyTranslateOCR.sh
Icon=$INSTALL_DIR/pyTranslateOCR/icon.png
Terminal=false
Type=Application
Categories=Utility;AudioVideo;
EOL

# Crea la directory di installazione se non esiste
mkdir -p "$INSTALL_DIR"

# Copia i file necessari
zenity --info --width=400 --text="Installando l'applicazione..."
cp -r pyTranslateOCR "$INSTALL_DIR/"

# Genera lo script pyTranslateOCR.sh
cat > "$INSTALL_DIR/pyTranslateOCR/pyTranslateOCR.sh" << EOL
#!/bin/bash
cd $INSTALL_DIR/pyTranslateOCR/
python3 main.py
EOL

# Rende eseguibile lo script pyTranslateOCR.sh
chmod +x "$INSTALL_DIR/pyTranslateOCR/pyTranslateOCR.sh"

# Chiude la finestra principale dell'installatore
kill $INSTALLER_PID

zenity --info --width=400 --text="Installazione completata!"
zenity --info --width=400 --text="Puoi avviare pyTranslateOCR dal menu delle applicazioni"
