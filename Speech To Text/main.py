import speech_recognition as sr
from gtts import gTTS  # Google Text-to-Speech (better language support)
import os
import platform

# Cross-platform audio playback
try:
    from pygame import mixer
    USE_PYGAME = True
except ImportError:
    USE_PYGAME = False
    print("⚠  pygame not found. Install with: pip install pygame")
from deep_translator import GoogleTranslator  # More stable than googletrans

# Speech-to-Text: Recognize spoken language (English)
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Please speak now in English...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        print("🔄 Recognizing speech...")
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"✅ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand the audio.")
    except sr.RequestError as e:
        print(f"❌ API Error: {e}")
    return ""

# Translate text using deep-translator (more stable)
def translate_text(text, target_language="es"):
    try:
        translated = GoogleTranslator(source='en', target=target_language).translate(text)
        print(f"🌍 Translated text: {translated}")
        return translated
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return text

# Text-to-Speech using gTTS (supports many languages)
def speak(text, language="en"):
    try:
        # Create audio file
        tts = gTTS(text=text, lang=language, slow=False)
        audio_file = "output.mp3"
        tts.save(audio_file)
        
        # Play audio using available method
        print("🔊 Playing audio...")
        
        if USE_PYGAME:
            # Use pygame mixer (most reliable)
            mixer.init()
            mixer.music.load(audio_file)
            mixer.music.play()
            while mixer.music.get_busy():
                continue
            mixer.quit()
        else:
            # Fallback to system command
            system = platform.system()
            if system == "Windows":
                os.system(f'start {audio_file}')
            elif system == "Darwin":  # macOS
                os.system(f'afplay {audio_file}')
            else:  # Linux
                os.system(f'mpg123 {audio_file} || ffplay -nodisp -autoexit {audio_file}')
            
            # Wait for playback (approximate)
            import time
            time.sleep(3)
        
        # Clean up
        if os.path.exists(audio_file):
            os.remove(audio_file)
    except Exception as e:
        print(f"❌ Speech output error: {e}")

# Display language options to the user
def display_language_options():
    print("\n" + "="*50)
    print("🌐 Available translation languages:")
    print("="*50)
    languages = {
        # Indian Languages
        "1": ("hi", "Hindi"),
        "2": ("ta", "Tamil"),
        "3": ("te", "Telugu"),
        "4": ("bn", "Bengali"),
        "5": ("mr", "Marathi"),
        "6": ("gu", "Gujarati"),
        "7": ("ml", "Malayalam"),
        "8": ("pa", "Punjabi"),
        "9": ("kn", "Kannada"),
        "10": ("or", "Odia"),
        "11": ("as", "Assamese"),
        
        # European Languages
        "12": ("es", "Spanish"),
        "13": ("fr", "French"),
        "14": ("de", "German"),
        "15": ("it", "Italian"),
        "16": ("pt", "Portuguese"),
        "17": ("ru", "Russian"),
        "18": ("pl", "Polish"),
        "19": ("nl", "Dutch"),
        "20": ("sv", "Swedish"),
        "21": ("da", "Danish"),
        "22": ("fi", "Finnish"),
        "23": ("no", "Norwegian"),
        "24": ("el", "Greek"),
        "25": ("cs", "Czech"),
        "26": ("hu", "Hungarian"),
        "27": ("ro", "Romanian"),
        "28": ("sk", "Slovak"),
        "29": ("uk", "Ukrainian"),
        "30": ("bg", "Bulgarian"),
        
        # Asian Languages
        "31": ("ja", "Japanese"),
        "32": ("ko", "Korean"),
        "33": ("zh-cn", "Chinese Simplified"),
        "34": ("zh-tw", "Chinese Traditional"),
        "35": ("th", "Thai"),
        "36": ("vi", "Vietnamese"),
        "37": ("id", "Indonesian"),
        "38": ("ms", "Malay"),
        "39": ("tl", "Filipino"),
        "40": ("km", "Khmer"),
        
        # Middle Eastern Languages
        "41": ("ar", "Arabic"),
        "42": ("he", "Hebrew"),
        "43": ("tr", "Turkish"),
        "44": ("fa", "Persian"),
        "45": ("ur", "Urdu"),
        
        # African Languages
        "46": ("am", "Amharic"),
        "47": ("sw", "Swahili"),
        "48": ("zu", "Zulu"),
        "49": ("xh", "Xhosa"),
        "50": ("yo", "Yoruba"),
    }
    
    for key, (code, name) in languages.items():
        print(f"{key}. {name} ({code})")
    
    print("="*50)
    choice = input(f"Select target language (1-{len(languages)}): ").strip()
    
    if choice in languages:
        code, name = languages[choice]
        print(f"✅ Selected: {name}")
        return code
    else:
        print("⚠  Invalid selection. Defaulting to Spanish.")
        return "es"

# Main function
def main():
    print("\n" + "🎙 " * 15)
    print("  SPEECH-TO-TEXT TRANSLATOR WITH VOICE OUTPUT")
    print("🎙 " * 15 + "\n")
    
    # Step 1: Select target language
    target_language = display_language_options()
    
    # Step 2: Speech-to-Text
    original_text = speech_to_text()
    
    if original_text:
        # Step 3: Translate
        translated_text = translate_text(original_text, target_language=target_language)
        
        # Step 4: Speak translated text in target language
        if translated_text:
            speak(translated_text, language=target_language)
            print("✅ Translation completed successfully!")
    else:
        print("❌ No speech detected. Please try again.")

if __name__ == "__main__":
    main()