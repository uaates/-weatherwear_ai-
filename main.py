import requests
import geocoder
import tkinter as tk
from PIL import Image, ImageTk
import speech_recognition as sr
import openai

# API Keys
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
openai.api_key = OPENAI_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_location():
    g = geocoder.ip('me')
    return g.city

def get_weather(city_name):
    params = {
        "q": city_name,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "tr"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if response.status_code == 200:
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        return temp, description
    else:
        print("Hata:", data.get("message", "Bilinmeyen hata"))
        return None, None

def recommend_outfit(temp):
    if temp < 5:
        return "Çok soğuk. Kalın mont, atkı ve eldiven giy.", "images/cold.png"
    elif 5 <= temp < 15:
        return "Hava serin. Ceket ve kazak tercih et.", "images/cool.png"
    elif 15 <= temp < 25:
        return "Hava ılık. Tişört veya ince bir üst giyebilirsin.", "images/warm.png"
    else:
        return "Hava sıcak. Şort ve tişört uygun olur.", "images/hot.png"

def show_weather(city=None):
    if not city:
        city = city_entry.get()
    if not city:
        city = get_location()
    temp, description = get_weather(city)
    if temp is not None:
        suggestion, img_path = recommend_outfit(temp)
        result_label.config(text=f"{city}:\n{description}, {temp}°C\n\n{suggestion}")

        # Görsel göster
        img = Image.open(img_path)
        img = img.resize((150, 150))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo
    else:
        result_label.config(text="Hava durumu alınamadı.")

def listen_city():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        result_label.config(text="Dinleniyor...")
        root.update()
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language="tr-TR")
            city_entry.delete(0, tk.END)
            city_entry.insert(0, text)
            show_weather(text)
        except sr.UnknownValueError:
            result_label.config(text="Ses anlaşılamadı.")
        except sr.RequestError:
            result_label.config(text="API hatası (internet?).")

def ask_ai():
    question = ai_entry.get()
    if not question:
        result_label.config(text="Bir soru giriniz.")
        return

    result_label.config(text="Yapay zeka düşünüyor...")
    root.update()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir yardımcı asistansın."},
            {"role": "user", "content": question}
        ]
    )
    answer = response['choices'][0]['message']['content']
    result_label.config(text=f"AI cevabı:\n{answer}")

# GUI
root = tk.Tk()
root.title("WeatherWear AI")

city_label = tk.Label(root, text="Şehir ismi gir (boş bırak otomatik algılar):")
city_label.pack()

city_entry = tk.Entry(root)
city_entry.pack()

check_button = tk.Button(root, text="Hava Durumu ve Öneri", command=show_weather)
check_button.pack()

listen_button = tk.Button(root, text="🎤 Sesli Şehir", command=listen_city)
listen_button.pack()

ai_label = tk.Label(root, text="Yapay zekaya soru sor:")
ai_label.pack()

ai_entry = tk.Entry(root)
ai_entry.pack()

ai_button = tk.Button(root, text="AI'ye Sor", command=ask_ai)
ai_button.pack()

result_label = tk.Label(root, text="", font=("Helvetica", 12), wraplength=300, justify="left")
result_label.pack()

image_label = tk.Label(root)
image_label.pack()

root.mainloop()
