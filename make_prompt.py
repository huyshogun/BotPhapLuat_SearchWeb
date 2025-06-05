import re
import textwrap
import numpy as np
import pandas as pd
import google.generativeai as genai
import os
import pickle
import streamlit as st
# from dotenv import load_dotenv
# load_dotenv()  # Tải các biến môi trường từ tệp .env
# api_key = os.getenv("api_key_google")
# api_key = os.environ.get("api_key_google")
api_key = st.secrets["api_key_google"]
genai.configure(api_key=api_key)

def make_first_prompt_gt_tt(query, relevant_passage, law_name):
  escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = textwrap.dedent("""Bạn là một bot hữu ích và giàu thông tin, trả lời các câu hỏi bằng cách sử dụng văn bản pháp luật từ đoạn văn tham khảo bên dưới.\
  Đảm bảo trả lời bằng một câu hoàn chỉnh, toàn diện, bao gồm tất cả thông tin cơ bản có liên quan.\
  Biết đoạn văn bạn tham khảo thuộc {law_name}, hãy nêu rõ bạn tham khảo điều này, khoản nào, điểm nào trong đoạn văn đó\
  Tuy nhiên, bạn đang nói chuyện với người dùng không biết nhiều về pháp luật, vì vậy hãy nhớ chia nhỏ các khái niệm phức tạp và\
  tạo ra một giọng điệu thân thiện và mang tính đối thoại.\
  Nếu đoạn văn không liên quan đến câu trả lời,hãy trả lời bằng những kiến thức bạn có.
  QUESTION: '{query}'
  PASSAGE: '{relevant_passage}'

    ANSWER:
  """).format(query=query, relevant_passage=escaped, law_name=law_name)
  return prompt
def make_first_prompt_gt1(query, relevant_passage):
    """
    Tạo prompt cho chatbot dựa trên câu hỏi, đoạn văn tham khảo và ngữ cảnh hội thoại trước đó.

    Args:
        query (str): Câu hỏi của người dùng.
        relevant_passage (str): Đoạn văn tham khảo cần sử dụng.
        context (str): Ngữ cảnh hội thoại trước đó (mặc định là rỗng).

    Returns:
        str: Prompt đã được định dạng để gửi cho mô hình.
    """
    # Loại bỏ các ký tự không cần thiết từ đoạn văn tham khảo
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")

    # Xây dựng prompt dựa trên template
    prompt_template = textwrap.dedent("""
        Bạn là một bot hữu ích và giàu thông tin, trả lời các câu hỏi bằng cách sử dụng văn bản pháp luật từ văn bản tham khảo bên dưới. \
        Đảm bảo trả lời bằng một cách hoàn chỉnh, toàn diện, bao gồm tất cả thông tin cơ bản. \
        Hãy trả lời một cách ngắn gọn, chủ yếu nêu ra số tiền phạt. \
        Lưu ý trong câu trả lời không viết lại câu hỏi. \
        Ví dụ: 4.000.000 đồng rút gọn thành 4tr, hoặc 400.000 đồng rút gọn thành 400k.\
        Và ghi nhớ hãy bôi đậm mức tiền phạt. \
        Biết văn bản pháp luật bạn tham khảo thuộc Nghị định 168/2024/NĐ-CP, và nêu rõ bạn tham khảo những điều nào, khoản nào, điểm nào trong đoạn văn đó. \
        Nếu câu hỏi không nêu cụ thể phương tiện nào thì hãy cho ra thông tin đối với mọi phương tiện như ô tô, xe máy, xe đạp,... \
        Nếu người vi phạm trong câu hỏi mắc nhiều lỗi thì cộng mức phạt trung bình của từng lỗi lại để cho ra mức phạt tổng.. \
        Có một ví dụ sau để hiểu hơn về các yêu cầu: \
        QUESTION: Anh A điều khiển xe trên đường mà trong máu hoặc hơi thở có nồng độ cồn \
        0,3 miligam/1 lít khí thở, chạy quá tốc độ 15km/h. Anh A gây ra tai nạn nhưng không dừng lại, không giữ nguyên hiện trường, bỏ trốn không đến trình báo với cơ quan có thẩm quyền. \
        Hỏi: Anh A bị xử phạt hành chính và trử điểm giấy phép lái xe như nào ? \
        Các bước giải: \
        Nếu áp dụng luật cũ (không phải luật trong văn bản tham khảo )ta có: \
        1, Lỗi nồng độ cồn 0,2 miligam/1 lít khí thở. Trong luật có: "Phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng đối với người điều khiển xe thực hiện hành vi điều khiển xe trên đường mà trong máu hoặc hơi thở có nồng độ cồn \
        nhưng chưa vượt quá 50 miligam/100 mililít máu hoặc chưa vượt quá 0,25 miligam/1 lít khí thở." => Lấy trung bình là (6+8)/2 = 7 triệu đồng \
        2, Lỗi chạy quá tốc độ 15km/h. Trong luật có: "Phạt tiền từ 3.000.000 đồng đến 5.000.000 đồng đối với người điều khiển xe thực hiện hành vi điều khiển xe chạy quá tốc độ quy định từ 10 km/h đến 20 km/h." \
        Luật này có rõ khoảng cho trước nên có thể lấy số tiền là: 3 + ((5-3)/(20-10))*(15-10) = 4 triệu đồng \
        3, Lỗi gây ra tai nạn nhưng không dừng lại, không giữ nguyên hiện trường, bỏ trốn không đến trình báo với cơ quan có thẩm quyền.\
        Trong luật có: " Phạt tiền từ 3.000.000 đồng đến 5.000.000 đồng đối với người điều khiển xe thực hiện một trong các hành vi vi phạm sau: không chấp hành hiệu lệnh của đèn tín hiệu giao thông; \
        không chấp hành hiệu lệnh, hướng dẫn của người điều khiển giao thông hoặc người kiểm soát giao thông."\
        => Không có khoảng cho trước nên lấy trung bình (3+5)/2 = 4 triệu đồng \
        4, Để tìm ra mức trừ điểm lái xe và các hình phạt bổ sung, hãy tìm những điều khoản có đề cập đến các điều khoản ở trên. VD: Lỗi ở bước 3 thuộc điều 5 khoản 6 điểm c.\
        Thì trong luật có đề cập điều 5 khoản 16 điểm d là: "Vi phạm lỗi ở điều 5 khoản 6 điểm c thì bị tước bằng lái xe 2 đến 4 tháng" -> Hình phạt bổ sung cho lỗi gây tai nạn là bị tước bằng 2 đến 4 tháng \
        ANSWER: Số tiền bị phạt: 7 + 4 + 4 = 15 triệu đồng \
                Bị tước quyền sử dụng giấy phép lái xe từ 2 đến 4 tháng \
        Nếu mỗi lỗi có một mức trừ điểm giấy phép lái xe khác nhau chỉ lấy mức trử điểm lớn nhất.
        Nếu câu hỏi không đề cập đến ai là chủ phương tiện thì mặc định người vi phạm là chủ phương tiện\
        Nếu đoạn văn không liên quan đến câu trả lời, hãy trả lời bằng những kiến thức bạn có.

        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'


        ANSWER:
    """)
    prompt = prompt_template.format(query=query, relevant_passage=escaped)
    return prompt

import textwrap

def make_first_prompt_gt2(query, relevant_passage, context=""):
    """
    Tạo prompt cho chatbot dựa trên câu hỏi, đoạn văn tham khảo và ngữ cảnh hội thoại trước đó.

    Args:
        query (str): Câu hỏi của người dùng.
        relevant_passage (str): Đoạn văn tham khảo cần sử dụng.
        context (str): Ngữ cảnh hội thoại trước đó (mặc định là rỗng).

    Returns:
        str: Prompt đã được định dạng để gửi cho mô hình.
    """
    # Loại bỏ các ký tự không cần thiết từ đoạn văn tham khảo
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    
    # Xây dựng prompt dựa trên template
    prompt_template = textwrap.dedent("""
        Bạn là một bot hữu ích và giàu thông tin, trả lời các câu hỏi bằng cách sử dụng văn bản pháp luật từ văn bản tham khảo bên dưới. \
        Đảm bảo trả lời bằng một cách hoàn chỉnh, toàn diện, bao gồm tất cả thông tin cơ bản liên quan đến mọi phương tiện giao thông như ô tô, xe máy, xe mô tô, xe đạp,....\
        Hãy trả lời một cách ngắn gọn, chủ yếu nêu ra số tiền phạt. \
        Lưu ý trong câu trả lời không viết lại câu hỏi. \
        Ví dụ: 4.000.000 đồng rút gọn thành 4tr, hoặc 400.000 đồng rút gọn thành 400k.\
        Và ghi nhớ hãy bôi đậm mức tiền phạt. \
        Biết văn bản pháp luật bạn tham khảo thuộc Nghị định 168/2024/NĐ-CP, và nêu rõ bạn tham khảo những điều nào, khoản nào, điểm nào trong đoạn văn đó. \
        Nếu người dùng yêu cầu trả lời câu hỏi liên quan đến các câu hỏi trước đó trong phần CONTEXT bên dưới thì hãy trả lời bằng kiến thức bạn có. \
        Nếu đoạn văn không liên quan đến câu trả lời, hãy trả lời bằng những kiến thức bạn có.

        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'
        CONTEXT: '{context}'

        ANSWER:
    """)
    prompt = prompt_template.format(query=query, relevant_passage=escaped, context=context)
    return prompt
def make_first_prompt_gt3(query, relevant_passage, context=""):
    """
    Tạo prompt cho chatbot dựa trên câu hỏi, đoạn văn tham khảo và ngữ cảnh hội thoại trước đó.

    Args:
        query (str): Câu hỏi của người dùng.
        relevant_passage (str): Đoạn văn tham khảo cần sử dụng.
        context (str): Ngữ cảnh hội thoại trước đó (mặc định là rỗng).

    Returns:
        str: Prompt đã được định dạng để gửi cho mô hình.
    """
    # Loại bỏ các ký tự không cần thiết từ đoạn văn tham khảo
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    
    # Xây dựng prompt dựa trên template
    prompt_template = textwrap.dedent("""
        Bạn là một bot hữu ích và giàu thông tin, trả lời các câu hỏi bằng cách sử dụng văn bản pháp luật từ văn bản tham khảo bên dưới. \
        Đảm bảo trả lời bằng một cách hoàn chỉnh, toàn diện, bao gồm tất cả thông tin cơ bản. \
        Hãy trả lời một cách ngắn gọn, chủ yếu nêu ra số tiền phạt. \
        Lưu ý trong câu trả lời không viết lại câu hỏi. \
        Ví dụ: 4.000.000 đồng rút gọn thành 4tr, hoặc 400.000 đồng rút gọn thành 400k.\
        Và ghi nhớ hãy bôi đậm mức tiền phạt. \
        Biết văn bản pháp luật bạn tham khảo thuộc Nghị định 168/2024/NĐ-CP, và nêu rõ bạn tham khảo những điều nào, khoản nào, điểm nào trong đoạn văn đó. \
        Nếu câu hỏi không nêu cụ thể phương tiện nào thì hãy cho ra thông tin đối với mọi phương tiện như ô tô, xe máy, xe đạp,... \
        Nếu người vi phạm trong câu hỏi mắc nhiều lỗi thì cộng mức phạt trung bình của từng lỗi lại để cho ra mức phạt tổng.. \
        Có một ví dụ sau để hiểu hơn về các yêu cầu: \
        QUESTION: Anh A điều khiển xe trên đường mà trong máu hoặc hơi thở có nồng độ cồn \
        0,3 miligam/1 lít khí thở, chạy quá tốc độ 15km/h. Anh A gây ra tai nạn nhưng không dừng lại, không giữ nguyên hiện trường, bỏ trốn không đến trình báo với cơ quan có thẩm quyền. \
        Hỏi: Anh A bị xử phạt hành chính và trử điểm giấy phép lái xe như nào ? \
        Các bước giải: \
        Nếu áp dụng luật cũ (không phải luật trong văn bản tham khảo )ta có: \
        1, Lỗi nồng độ cồn 0,2 miligam/1 lít khí thở. Trong luật có: "Phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng đối với người điều khiển xe thực hiện hành vi điều khiển xe trên đường mà trong máu hoặc hơi thở có nồng độ cồn \
        nhưng chưa vượt quá 50 miligam/100 mililít máu hoặc chưa vượt quá 0,25 miligam/1 lít khí thở." => Lấy trung bình là (6+8)/2 = 7 triệu đồng \
        2, Lỗi chạy quá tốc độ 15km/h. Trong luật có: "Phạt tiền từ 3.000.000 đồng đến 5.000.000 đồng đối với người điều khiển xe thực hiện hành vi điều khiển xe chạy quá tốc độ quy định từ 10 km/h đến 20 km/h." \
        Luật này có rõ khoảng cho trước nên có thể lấy số tiền là: 3 + ((5-3)/(20-10))*(15-10) = 4 triệu đồng \
        3, Lỗi gây ra tai nạn nhưng không dừng lại, không giữ nguyên hiện trường, bỏ trốn không đến trình báo với cơ quan có thẩm quyền.\
        Trong luật có: " Phạt tiền từ 3.000.000 đồng đến 5.000.000 đồng đối với người điều khiển xe thực hiện một trong các hành vi vi phạm sau: không chấp hành hiệu lệnh của đèn tín hiệu giao thông; \
        không chấp hành hiệu lệnh, hướng dẫn của người điều khiển giao thông hoặc người kiểm soát giao thông."\
        => Không có khoảng cho trước nên lấy trung bình (3+5)/2 = 4 triệu đồng \
        4, Để tìm ra mức trừ điểm lái xe và các hình phạt bổ sung, hãy tìm những điều khoản có đề cập đến các điều khoản ở trên. VD: Lỗi ở bước 3 thuộc điều 5 khoản 6 điểm c.\
        Thì trong luật có đề cập điều 5 khoản 16 điểm d là: "Vi phạm lỗi ở điều 5 khoản 6 điểm c thì bị tước bằng lái xe 2 đến 4 tháng" -> Hình phạt bổ sung cho lỗi gây tai nạn là bị tước bằng 2 đến 4 tháng \
        ANSWER: Số tiền bị phạt: 7 + 4 + 4 = 15 triệu đồng \
                Bị tước quyền sử dụng giấy phép lái xe từ 2 đến 4 tháng \
        Trong ví dụ trên chưa nêu rõ phương tiện gì nên lấy tạm xe máy làm ví dụ, trong câu hỏi thực tế nếu câu hỏi không đề cập cụ thể phương tiện gì thì \
        cho ra tất cả các loại phương tiện giao thông có thể nếu phương tiện đó có thể gây ra lỗi trong câu hỏi \
        Nếu câu hỏi đã cho biết loại phương tiện cụ thể (VD: Xe taxi cũng là xe ô tô) thì chỉ cho ra mức xử phạt liên quan đến phương tiện đó thôi. \
        Nếu mỗi lỗi có một mức trừ điểm giấy phép lái xe khác nhau chỉ lấy mức trử điểm lớn nhất. \
        Nếu đoạn văn không liên quan đến câu trả lời, hãy trả lời bằng những kiến thức bạn có.

        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'
        CONTEXT: '{context}'

        ANSWER:
    """)
    prompt = prompt_template.format(query=query, relevant_passage=escaped, context=context)
    return prompt