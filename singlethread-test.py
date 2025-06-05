import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
import time
# ================================================
# 1) Cấu hình thư viện google.generativeai
# ================================================
# Đọc API key từ biến môi trường
API_KEY = "AIzaSyAYLp5HQXOAqeWCTOD8cgZJVZqTJipKHLI"
if not API_KEY:
    raise RuntimeError("Thiếu biến môi trường GOOGLE_API_KEY")

# Khởi tạo configuration
# (Nếu bạn dùng Service Account JSON, có thể config khác theo doc)
genai.configure(api_key=API_KEY)


# ================================================
# 2) Hàm gọi model gemini-2.0-flash
# ================================================
def call_gemini_flash(prompt_text: str, idx: int) -> dict:
    """
    Gửi request đến model gemini-2.0-flash qua google.generativeai
    Trả về dict: { index, status, output hoặc error }.
    """
    try:
        models = genai.GenerativeModel('gemini-2.0-flash')
        genai.configure(api_key=API_KEY)

        # Kết quả trả về thường ở field 'candidates'
        # Mỗi candidate có key 'output' chứa text
        # candidates = response.get("candidates", [])
        text_out = models.generate_content(prompt_text)

        return {
            "index": idx,
            "status": "success",
            "output": text_out
        }

    except Exception as e:
        return {
            "index": idx,
            "status": "error",
            "error": str(e)
        }



start = time.time()
resp = call_gemini_flash("Viết một đoạn thơ ngắn về mùa thu.", 0)
duration = time.time() - start
print(f"Thời gian chạy: {duration}s")
resp['output'].text
