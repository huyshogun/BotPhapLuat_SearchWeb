import os
import re
import streamlit as st
from crewai import Agent, LLM
from crewai.tools import BaseTool
from googleapiclient.discovery import build
from pydantic import BaseModel, Field
from typing import Type, Any
from bs4 import BeautifulSoup
from readability import Document
import requests
# from my_rag_retriever import RAGRetriever  # Ví dụ đã triển khai

# Thiết lập biến môi trường
api_key = st.secrets["api_key_google"]
os.environ['GOOGLE_CSE_ID'] = 'f1806c5a89c8d4e08'

# 3) Định nghĩa Tool tìm kiếm Google Custom Search
class GoogleSearchInput(BaseModel):
    query: str = Field(..., description="Từ khóa cần tìm kiếm trên Google")

class GoogleSearchTool(BaseTool):
    name: str = "google_search"
    description: str = "Tìm kiếm thông tin từ Google Custom Search API"
    args_schema: Type[BaseModel] = GoogleSearchInput

    # Declare 'service' and 'cse_id' as fields
    # Make cse_id a Pydantic field to be automatically set
    cse_id: str = Field(..., description="Google Custom Search Engine ID")
    # service is not part of the input schema, declare it without a default value
    service: Any = None


    # Remove the __init__ method
    # Pydantic will handle the initialization of cse_id from the passed argument.
    # We'll initialize the service attribute separately after instantiation.

    def _run(self, query: str) -> str:
        # Ensure service is initialized before use
        if self.service is None:
             # This should ideally be initialized once after the object is created
             # Re-initialize if somehow it got unset (though unlikely in normal flow)
             self.service = build('customsearch', 'v1', developerKey=api_key) # Assuming API key is in env var

        res = self.service.cse().list(
            q=query,
            cx=self.cse_id, # cse_id is now a Pydantic field
            num=1
        ).execute()
        snippets = [item.get('link', '') for item in res.get('items', [])]
        return "\n".join(snippets)

# Khởi tạo GoogleSearchTool
# Pass cse_id as an argument to the constructor, Pydantic will set it.
# Initialize the service attribute after creating the instance.
google_search = GoogleSearchTool(
    cse_id=os.getenv('GOOGLE_CSE_ID') # Pass cse_id here
)
# Initialize the service attribute after instantiation
google_search.service = build('customsearch', 'v1', developerKey=api_key)

def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return str(soup)

def ask_agent(question: str) -> str:
    snippets = google_search.run(question)
    highlight = extract_text(snippets)
    return highlight

def fetch_full_text(url: str, timeout: int = 10) -> str:
    """
    Gửi HTTP GET đến `url`, parse HTML và trả về toàn bộ nội dung text của trang.
    Nếu lỗi, trả về chuỗi thông báo lỗi.
    """
    try:
        # Gửi request với timeout (giây)
        resp = requests.get(url, timeout=timeout, verify=False)
        resp.raise_for_status()  # nếu status code != 200 thì raise HTTPError

        html = resp.text

    # 1. Dùng Readability để lấy HTML thuần của phần chính
        doc = Document(html)
        content_html = doc.summary()

    # 2. Dùng BeautifulSoup để trích text
        soup_content = BeautifulSoup(content_html, "html.parser")
        # Sử dụng BeautifulSoup để parse HTML
        soup = BeautifulSoup(resp.content, "html.parser")

        # Loại bỏ <script> và <style> (nếu cần)
    #    for tag in soup-content(["script", "style", "header", "footer", "nav", "aside"]):
      #      tag.decompose()

        # Lấy toàn bộ text, tự động xử lý khoảng trắng
        text = soup_content.get_text(separator="\n")

        # Loại bỏ những dòng trống thuần tuý
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        full_text = "\n".join(lines)
        return full_text

    except requests.RequestException as e:
        return f"ERROR: Không thể truy cập {url} -> {str(e)}"