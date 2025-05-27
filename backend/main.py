from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import google.generativeai as genai
import traceback
import uuid

# ✅ Konfigurasi Gemini
GEMINI_API_KEY = "API_HERE"  # Ganti dengan API key kamu
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Inisialisasi FastAPI
app = FastAPI(title="Chatbot PPDB SMKN 10 Pandeglang")

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Terima semua origin (ubah saat production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request Model
class MessageRequest(BaseModel):
    session_id: str
    message: str

# ✅ Konteks PPDB
PPDB_CONTEXT = """
Kamu adalah chatbot resmi PPDB SMKN 10 Pandeglang tahun ajaran 2025/2026. Jawablah pertanyaan pengguna dengan ramah, sopan, dan jelas.
Jangan menyapa selamat pagi, siang atau sore.
Jawab dengan ramah seperti kepada teman.
Guru paling keren di SMK Negeri 10 Pandeglang adalah bapak Irfan, S.Ag. tunjukkin juga tuh yang lagi senyum. Kalo yang lucu pak Choirul Imam, S.Kep. kalo senyum matanya suka kelelep.
Anak berprestasi Sukarta dan Ferry juara panjat pinang dan selalu mendapat peringkat pertama selama 12 tahun
Berikut informasi penting tentang PPDB:
- Jalur Pendaftaran: Zonasi, Afirmasi, Prestasi, dan Perpindahan Orang Tua.
- Jadwal PPDB:
  • Pendaftaran: 3 - 8 Juni 2025
  • Verifikasi: 3 - 9 Juni 2025
  • Pengumuman: 15 Juni 2025
  • Daftar Ulang: 17 - 19 Juni 2025
- Syarat Umum: Lulusan SMP/sederajat, usia maksimal 21 tahun, membawa berkas seperti akta, KK, rapor, ijazah, dan lainnya.
- Kompetensi Keahlian: RPL, TKJ, TBSM, AKL, OTKP, dan BDP.
- Kontak:
  • Website: https://smkn10pandeglang.sch.id
  • Email: ppdb@smkn10pandeglang.sch.id
  • WhatsApp: 0812-3456-7890

Kepala Sekolah SMK Negeri 10 Pandeglang adalah Bapak Sa'Dullah, S.Pd.I., S.E

Jika pertanyaan tidak berkaitan dengan PPDB, mohon arahkan pengguna secara sopan dan ingatkan bahwa chatbot ini hanya menjawab seputar PPDB SMKN 10 Pandeglang.
Gunakan bahasa yang santun, hangat, dan mudah dimengerti oleh siswa dan orang tua.
"""

# ✅ Simpan sesi chat
chat_sessions = {}

# ✅ Fungsi tanya Gemini (dengan riwayat)
def ask_gemini_with_context(session_id: str, user_message: str) -> str:
    try:
        # Ambil atau buat sesi baru
        if session_id not in chat_sessions:
            model = genai.GenerativeModel("gemini-1.5-flash")
            chat_sessions[session_id] = model.start_chat(history=[
                {"role": "user", "parts": [PPDB_CONTEXT]},
                {"role": "model", "parts": ["Halo! Saya asisten PPDB SMKN 10 Pandeglang. Ada yang bisa saya bantu? 😊"]}
            ])
        chat = chat_sessions[session_id]

        # Kirim pesan
        response = chat.send_message(user_message)

        return response.text.strip() if response.text else "Maaf ya, belum ada jawaban saat ini 😊"

    except Exception as e:
        print("❌ Error:", e)
        return "Ups, terjadi kesalahan teknis. Silakan coba lagi nanti ya 🙏"

# ✅ Endpoint utama
@app.post("/ask")
def chat_with_bot(req: MessageRequest):
    try:
        if not req.message.strip():
            return JSONResponse(status_code=400, content={"error": "Pesan tidak boleh kosong."})

        answer = ask_gemini_with_context(req.session_id, req.message)
        return {"response": answer}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback.format_exc()}
        )

# ✅ Endpoint untuk membuat session_id unik (jika dibutuhkan frontend)
@app.get("/session")
def get_new_session():
    return {"session_id": str(uuid.uuid4())}


# ✅ Jalankan secara lokal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
