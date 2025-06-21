# pyTranslateOCR
OCR program with translator and overlay - supports various translators and two OCRs. 

The TTS will read the translation to you in your language. Useful for video games like stories with subtitles or whatever you want.

This program is the evolution of my [pyLibOCR]( https://github.com/MoonDragon-MD/pyLibOCR) project

**Right now it is in Beta there are still a few things to fix but overall it works.**

**Still the interface and notes are mainly in Italian, I am working on it.**

First of all the interface is in pyQt5 and is much more convenient and scalable. 

It is compatible with the following translators:

- Google
- [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate)
- [translateLocally]( https://github.com/XapaJIaMnu/translateLocally)  if you want the Italian language look at this: [ITA-models-translateLocally]( https://github.com/MoonDragon-MD/ITA-models-translateLocally-)
- [nllb-serve]( https://github.com/thammegowda/nllb-serve) or [nllb-serve-slim]( https://github.com/MoonDragon-MD/nllb-serve-slim) (only CPU)
  
It supports the following OCRs:

- [tesseract]( https://github.com/tesseract-ocr/tesseract)
- [Umi-OCR]( https://github.com/hiroi-sora/Umi-OCR)
- Umi-OCR server
  
Can read the translation result via integrated/pre-installed TTS (windows/linux)

Can be operated by keyboard shortcuts on both operating systems.

There is an overlay option that allows you to see the translation directly in overlay instead of the original text.

If you have strange text/background there is the enhance image option (with various setups)

The single text option allows you to send the full text (not line by line) to the translator so that you have better comprehension.

### Requirements:
- Python (I used 3.8 on Linux / 3.10 on Windows)
Linux/Debian:

- At startup you might have problems if you don't create the ini file correctly, so close, set the ini by hand and then reopen.

- Sometimes it automantically switches to translate with LibreTranslate
-      pip install PyQt5 pyttsx3 pytesseract pillow requests pynput python-xlib googletrans==3.1.0a0 httpx httpcore
- sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-*LANG [espeak]
Windows:
-      pip install PyQt5 pyttsx3 pytesseract pillow requests keyboard pynput googletrans==3.1.0a0 httpx httpcore


### Installation:
For Linux, I have created a simple installer (it also checks for necessary dependencies) so that you will find it in the menu (with icon).

### Usage:
For Linux if you used the installer you will find it in the menu otherwise use ``` python3 main.py ```
For Windows there is the "pyTranslateOCR.bat" file (two clicks and it starts), otherwise use ``` python main.py ```

### Here are some screenshots:
![alt text](https://github.com/MoonDragon-MD/pyTranslateOCR/blob/main/img/ITA-BETA.jpg?raw=true)

### Known problems:
- At startup you might have problems if you don't create the ini file correctly, so close, set the ini by hand and then reopen.
- Sometimes it automantically switches to translate with LibreTranslate


