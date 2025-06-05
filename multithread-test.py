import os
from multiprocessing import Pool
import google.generativeai as genai
import time
# ================================
# 1. Thiết lập API Key
# ================================
API_KEY = "AIzaSyAYLp5HQXOAqeWCTOD8cgZJVZqTJipKHLI"
if not API_KEY:
    raise RuntimeError("Thiếu biến môi trường GOOGLE_API_KEY")


# ================================
# 2. Hàm worker: gọi API Gemini an toàn
# ================================
def call_gemini(prompt: str) -> dict:
    """
    Trong mỗi process, ta sẽ:
      1) Khởi tạo client và model riêng (tránh chia sẻ lock).
      2) Bắt mọi exception, trả về dict {'success': False, 'error': ...} nếu có lỗi,
         hoặc {'success': True, 'text': ...} nếu thành công.
    """
    try:
        # Khởi riêng genai.Client và GenerativeModel trong tiến trình con
        models = genai.GenerativeModel("gemini-2.0-flash")
        genai.configure(api_key=API_KEY)
        # Gọi API
        response = models.generate_content(prompt)
        return {"success": True, "text": response.text}

    except Exception as e:
        # Nếu có lỗi, chỉ trả về thông tin lỗi dưới dạng string
        return {"success": False, "error": str(e)}


# ================================
# 3. Hàm chính: khởi Pool và thu kết quả
# ================================
def main():
    # Danh sách các prompt cần gửi
    prompts = [
        "Viết một đoạn thơ ngắn về mùa thu.",
        "Viết một đoạn thơ ngắn về mùa hạ.",
        "Viết một đoạn thơ ngắn về mùa đông.",
        "Viết một đoạn thơ ngắn về mùa xuân.",
        # … bạn có thể thêm nhiều prompt hơn
    ]

    # Lấy số lượng nhân CPU khả dụng
    num_cpus = os.cpu_count() or 1
    print(f"Số nhân CPU được phát hiện: {num_cpus}")
    start = time.time()
    # Khởi Pool với số process = num_cpus
    with Pool(processes=4) as pool:
        # Gọi song song: mỗi nhân chạy call_gemini với một prompt
        results = pool.map(call_gemini, prompts)
    duration = time.time() - start
    print(f"Thời gian chạy: {duration}")
    # Duyệt và in kết quả
    for idx, res in enumerate(results):
        if res["success"]:
            print(f"[Prompt {idx+1}] Kết quả:\n{res['text']}\n")
        else:
            print(f"[Prompt {idx+1}] LỖI: {res['error']}\n")


#if __name__ == "__main__":
 #   main()
start = time.time()
resp = call_gemini("Viết một đoạn thơ ngắn về mùa xuân.")
if resp["success"]:
    print(f"Kết quả:\n{resp['text']}\n")
else:
    print(f"LỖI: {resp['error']}\n")
resp = call_gemini("Viết một đoạn thơ ngắn về mùa hạ.")
if resp["success"]:
    print(f"Kết quả:\n{resp['text']}\n")
else:
    print(f"LỖI: {resp['error']}\n")
resp = call_gemini("Viết một đoạn thơ ngắn về mùa thu.")
if resp["success"]:
    print(f"Kết quả:\n{resp['text']}\n")
else:
    print(f"LỖI: {resp['error']}\n")
resp = call_gemini("Viết một đoạn thơ ngắn về mùa đông.")
duration = time.time() - start
print(f"Thời gian chạy: {duration}s")
if resp["success"]:
    print(f"Kết quả:\n{resp['text']}\n")
else:
    print(f"LỖI: {resp['error']}\n")