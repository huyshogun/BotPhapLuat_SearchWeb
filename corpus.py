import json

law_list = ["Thông tư 01/2024/TT-BGTVT", "Thông tư 12/2025/TT-BCA", "Thông tư 26/2024/TT-BCA", "Thông tư 32/2023/TT-BCA", "Thông tư 32/2024/TT-BGTVT", 
            "Thông tư 34/2024/TT-BGTVT", "Thông tư 35/2024/TT-BGTVT", "Thông tư 36/2023/TT-BCA", "Thông tư 40/2024/TT-BGTVT", "Thông tư 49/2024/TT-BGTVT",
            "Thông tư 62/2024/TT-BCA","Thông tư 63/2024/TT-BCA","Thông tư 64/2024/TT-BGTVT","Thông tư 67/2024/TT-BCA",
            "Thông tư 69/2024/TT-BCA","Thông tư 71/2024/TT-BQP","Thông tư 72/2024/TT-BCA","Thông tư 73/2024/TT-BCA","Thông tư 79/2024/TT-BCA"]
 
law_dict = {
    "Thông tư 01/2024/TT-BGTVT": "QUY ĐỊNH VỀ VIỆC KIỂM TRA CHẤT LƯỢNG AN TOÀN KỸ THUẬT VÀ BẢO VỆ MÔI TRƯỜNG PHƯƠNG TIỆN GIAO THÔNG ĐƯỜNG SẮT",
    "Thông tư 12/2025/TT-BCA": "QUY ĐỊNH VỀ SÁT HẠCH, CẤP GIẤY PHÉP LÁI XE; CẤP, SỬ DỤNG GIẤY PHÉP LÁI XE QUỐC TẾ",
    "Thông tư 26/2024/TT-BCA": "QUY ĐỊNH THỐNG KÊ, TỔNG HỢP, XÂY DỰNG, QUẢN LÝ, KHAI THÁC, SỬ DỤNG CƠ SỞ DỮ LIỆU VỀ TAI NẠN GIAO THÔNG ĐƯỜNG BỘ, TAI NẠN GIAO THÔNG ĐƯỜNG SẮT, TAI NẠN GIAO THÔNG ĐƯỜNG THỦY NỘI ĐỊA",
    "Thông tư 32/2023/TT-BCA": "QUY ĐỊNH NHIỆM VỤ, QUYỀN HẠN, HÌNH THỨC, NỘI DUNG VÀ QUY TRÌNH TUẦN TRA, KIỂM SOÁT, XỬ LÝ VI PHẠM HÀNH CHÍNH VỀ GIAO THÔNG ĐƯỜNG BỘ CỦA CẢNH SÁT GIAO THÔNG",
    "Thông tư 32/2024/TT-BGTVT": "QUY ĐỊNH VỀ QUẢN LÝ GIÁ DỊCH VỤ SỬ DỤNG ĐƯỜNG BỘ CỦA CÁC DỰ ÁN ĐẦU TƯ XÂY DỰNG ĐƯỜNG BỘ ĐỂ KINH DOANH, DO TRUNG ƯƠNG QUẢN LÝ ",
    "Thông tư 34/2024/TT-BGTVT": "QUY ĐỊNH VỀ HOẠT ĐỘNG TRẠM THU PHÍ ĐƯỜNG BỘ",
    "Thông tư 35/2024/TT-BGTVT": "QUY ĐỊNH VỀ ĐÀO TẠO, SÁT HẠCH, CẤP GIẤY PHÉP LÁI XE; CẤP, SỬ DỤNG GIẤY PHÉP LÁI XE QUỐC TẾ; ĐÀO TẠO, KIỂM TRA, CẤP CHỨNG CHỈ BỒI DƯỠNG KIẾN THỨC PHÁP LUẬT VỀ GIAO THÔNG ĐƯỜNG BỘ",
    "Thông tư 36/2023/TT-BCA": "QUY ĐỊNH QUY TRÌNH TUẦN TRA, KIỂM SOÁT VÀ XỬ LÝ VI PHẠM HÀNH CHÍNH CỦA CẢNH SÁT ĐƯỜNG THỦY",
    "Thông tư 40/2024/TT-BGTVT": "QUY ĐỊNH VỀ CÔNG TÁC PHÒNG, CHỐNG, KHẮC PHỤC HẬU QUẢ THIÊN TAI TRONG LĨNH VỰC ĐƯỜNG BỘ",
    "Thông tư 49/2024/TT-BGTVT": "BAN HÀNH QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ TRUNG TÂM SÁT HẠCH LÁI XE CƠ GIỚI ĐƯỜNG BỘ",
    "Thông tư 62/2024/TT-BCA": "BAN HÀNH QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ “HỆ THỐNG GIÁM SÁT BẢO ĐẢM AN NINH, TRẬT TỰ, AN TOÀN GIAO THÔNG ĐƯỜNG BỘ”, QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ “THIẾT BỊ GIÁM SÁT HÀNH TRÌNH VÀ THIẾT BỊ GHI NHẬN HÌNH ẢNH NGƯỜI LÁI XE” VÀ QUY CHUẨN KỸ THUẬT QUỐC GIA VỀ “TRUNG TÂM CHỈ HUY GIAO THÔNG",
    "Thông tư 63/2024/TT-BCA": "QUY ĐỊNH CÔNG TÁC KIỂM TRA, KIỂM SOÁT VÀ XỬ LÝ VI PHẠM PHÁP LUẬT TRONG LĨNH VỰC GIAO THÔNG ĐƯỜNG SẮT CỦA CẢNH SÁT GIAO THÔNG",
    "Thông tư 64/2024/TT-BGTVT": "QUY ĐỊNH NỘI DUNG, CHƯƠNG TRÌNH ĐÀO TẠO THUYỀN VIÊN, NGƯỜI LÁI PHƯƠNG TIỆN THỦY NỘI ĐỊA",
    "Thông tư 67/2024/TT-BCA": "QUY ĐỊNH QUY TRÌNH QUẢN LÝ, SỬ DỤNG PHƯƠNG TIỆN, THIẾT BỊ KỸ THUẬT NGHIỆP VỤ TRONG CÔNG AN NHÂN DÂN VÀ DỮ LIỆU THU ĐƯỢC TỪ PHƯƠNG TIỆN, THIẾT BỊ KỸ THUẬT DO CÁ NHÂN, TỔ CHỨC CUNG CẤP ĐỂ PHÁT HIỆN VI PHẠM HÀNH CHÍNH",
    "Thông tư 69/2024/TT-BCA": "QUY ĐỊNH VỀ CHỈ HUY, ĐIỀU KHIỂN GIAO THÔNG ĐƯỜNG BỘ CỦA CẢNH SÁT GIAO THÔNG",
    "Thông tư 71/2024/TT-BQP": "QUY ĐỊNH VỀ KIỂM SOÁT QUÂN SỰ, KIỂM TRA XE QUÂN SỰ THAM GIA GIAO THÔNG ĐƯỜNG BỘ",
    "Thông tư 72/2024/TT-BCA": "QUY ĐỊNH QUY TRÌNH ĐIỀU TRA, GIẢI QUYẾT TAI NẠN GIAO THÔNG ĐƯỜNG BỘ CỦA CẢNH SÁT GIAO THÔNG",
    "Thông tư 73/2024/TT-BCA": "QUY ĐỊNH CÔNG TÁC TUẦN TRA, KIỂM SOÁT, XỬ LÝ VI PHẠM PHÁP LUẬT VỀ TRẬT TỰ, AN TOÀN GIAO THÔNG ĐƯỜNG BỘ CỦA CẢNH SÁT GIAO THÔNG",
    "Thông tư 79/2024/TT-BCA": "QUY ĐỊNH VỀ CẤP, THU HỒI CHỨNG NHẬN ĐĂNG KÝ XE, BIỂN SỐ XE CƠ GIỚI, XE MÁY CHUYÊN DÙNG"
}

