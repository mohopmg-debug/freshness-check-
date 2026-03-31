import streamlit as st
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Smart Freshness Scanner", page_icon="🥩")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    .stMetric {background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Smart Freshness Scanner")
st.write("วิเคราะห์ความสดตามเกณฑ์ Danger Zone Guide")

# 2. ฟังก์ชันวิเคราะห์สีตามใบงาน (ม่วง=สด / แดง=เน่า)
def analyze_danger_zone(rgb_color):
    color_uint8 = np.uint8([[rgb_color]])
    hsv_color = cv2.cvtColor(color_uint8, cv2.COLOR_RGB2HSV)[0][0]
    hue = hsv_color[0]
    
    # คำนวณตามแผนภาพที่ส่งมา
    if 125 <= hue <= 155: 
        return "สด (Fresh)", "pH 6-7", 100, "success", "✅ ปลอดภัย บริโภคได้ปกติ"
    
    elif 100 <= hue < 125:
        return "เริ่มเสีย (Base)", "pH 8-9", 40, "warning", "⚠️ เริ่มเสี่ยง: มีสภาวะเป็นด่าง"
    
    elif 30 <= hue < 100:
        return "เน่าเสีย (Base)", "pH 10+", 0, "error", "🚫 อันตรายสูงสุด: ห้ามบริโภค"
    
    elif 156 <= hue <= 175:
        return "เริ่มเสีย (Acid)", "pH 5", 40, "warning", "⚠️ เริ่มเสี่ยง: มีสภาวะเป็นกรด"
    
    elif hue > 175 or hue < 30:
        return "เน่าเสีย (Acid)", "pH 4-", 0, "error", "🚫 อันตรายสูงสุด: ห้ามบริโภค"
    
    else:
        return "ตรวจสอบไม่ได้", "-", 0, "info", "กรุณาถ่ายรูปใหม่ในที่สว่าง"

# 3. ส่วนแสดงผล
uploaded_file = st.file_uploader("ถ่ายรูปหรืออัปโหลดแถบวัด", type=["jpg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    st.image(img, caption="รูปที่อัปโหลด", use_container_width=True)
    
    # ใช้ K-Means หาเฉดสีเด่น
    pixels = cv2.resize(img_array, (100, 100)).reshape((-1, 3))
    kmeans = KMeans(n_clusters=3, n_init=10).fit(pixels)
    dom_color = kmeans.cluster_centers_[np.argmax(np.bincount(kmeans.labels_))]
    
    status, ph, score, alert, msg = analyze_danger_zone(dom_color)
    
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("สถานะ", status)
    col2.metric("ค่า pH ประมาณการ", ph)
    
    if alert == "success": st.success(msg)
    elif alert == "warning": st.warning(msg)
    else: st.error(msg)
    
    # โชว์สีที่ตรวจได้
    hex_c = '#%02x%02x%02x' % (int(dom_color[0]), int(dom_color[1]), int(dom_color[2]))
    st.markdown(f"**สีที่ตรวจพบ:** <div style='display:inline-block; width:30px; height:30px; background-color:{hex_c}; border-radius:50%; vertical-align:middle;'></div> {hex_c}", unsafe_allow_html=True)
