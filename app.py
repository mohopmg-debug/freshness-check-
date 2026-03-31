import streamlit as st
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# --- การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Ultra-Precision Freshness Scanner", page_icon="🔬", layout="centered")

st.markdown("""
    <style>
    .main {background-color: #f0f2f6;}
    .reportview-container .main .block-container {padding-top: 2rem;}
    .stAlert {border-radius: 12px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 Smart Freshness Scanner (Pro)")
st.caption("ระบบวิเคราะห์ความสดระดับนวัตกรรม ด้วยการคำนวณค่า HSV และ K-Means Clustering")

# --- ฟังก์ชันวิเคราะห์ระดับเทพ ---
def analyze_danger_zone_pro(rgb_color):
    # แปลงจาก RGB เป็น HSV (Hue, Saturation, Value)
    color_uint8 = np.uint8([[rgb_color]])
    hsv_color = cv2.cvtColor(color_uint8, cv2.COLOR_RGB2HSV)[0][0]
    
    h = hsv_color[0]  # เฉดสี (0-180)
    s = hsv_color[1]  # ความสด/อิ่มตัวของสี (0-255)
    v = hsv_color[2]  # ความสว่าง (0-255)

    # 1. แก้ปัญหาสีขาว/เทา/ซีด (#fafafa): 
    # ถ้า Saturation ต่ำมาก (S < 30) แสดงว่าสียังไม่เปลี่ยนไปทางอันตราย ให้ถือว่าเป็นช่วง Baseline (สด)
    if s < 30:
        return "สด (Fresh)", "pH 6-7", 100, "success", "✅ ปลอดภัย: แถบวัดยังไม่ทำปฏิกิริยากับก๊าซอันตราย", h, s, v

    # 2. วิเคราะห์ตาม Hue (เฉดสี) ตาม Danger Zone Guide
    # ช่วงสีม่วง (Baseline)
    if 125 <= h <= 155:
        return "สด (Fresh)", "pH 6-7", 100, "success", "✅ ปลอดภัย: เนื้อสัตว์ยังมีความสดอยู่", h, s, v
    
    # ช่วงสีน้ำเงินม่วง (เริ่มเสียจากเบส)
    elif 100 <= h < 125:
        return "เริ่มเสีย (Base)", "pH 8-9", 40, "warning", "⚠️ เริ่มเสี่ยง: ตรวจพบสภาวะเป็นด่าง (ก๊าซแอมโมเนียเริ่มก่อตัว)", h, s, v
    
    # ช่วงสีเขียว/เหลือง (เน่าจากเบส)
    elif 30 <= h < 100:
        return "เน่าเสีย (Base)", "pH 10+", 0, "error", "🚫 อันตรายสูงสุด: ห้ามบริโภค! ตรวจพบสภาวะด่างรุนแรง", h, s, v
    
    # ช่วงสีชมพู (เริ่มเสียจากกรด)
    elif 156 <= h <= 175:
        return "เริ่มเสีย (Acid)", "pH 5", 40, "warning", "⚠️ เริ่มเสี่ยง: ตรวจพบสภาวะกรดเกินมาตรฐาน", h, s, v
    
    # ช่วงสีแดง (เน่าจากกรด) - Hue 0-30 หรือ 176-180
    elif h > 175 or h < 30:
        return "เน่าเสีย (Acid)", "pH 4-", 0, "error", "🚫 อันตรายสูงสุด: ห้ามบริโภค! ตรวจพบสภาวะกรดรุนแรง", h, s, v
    
    else:
        return "ตรวจสอบไม่ได้", "-", 0, "info", "กรุณาตรวจสอบแสงไฟหรือถ่ายรูปใหม่อีกครั้ง", h, s, v

# --- ส่วนหน้าจอการทำงาน ---
uploaded_file = st.file_uploader("📷 อัปโหลดรูปภาพแถบวัดสารสกัดกะหล่ำปลีม่วง", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    st.image(img, caption="ภาพที่กำลังวิเคราะห์", use_container_width=True)
    
    with st.spinner('🧪 AI กำลังสแกนหาเฉดสีในระดับโมเลกุล...'):
        # ใช้ K-Means เพื่อหา "สีที่แท้จริง" โดยไม่โดนแสงเงารบกวน
        pixels = cv2.resize(img_array, (100, 100)).reshape((-1, 3))
        kmeans = KMeans(n_clusters=3, n_init=10).fit(pixels)
        
        # เลือกสีกลุ่มที่ใหญ่ที่สุด (Dominant Color)
        counts = np.bincount(kmeans.labels_)
        dom_color = kmeans.cluster_centers_[np.argmax(counts)]
        
        # ประมวลผลด้วยฟังก์ชันตัวใหม่
        status, ph, score, alert, msg, h_val, s_val, v_val = analyze_danger_zone_pro(dom_color)
        
        st.divider()
        
        # แสดงผลลัพธ์แบบ Dashboard
        c1, c2 = st.columns(2)
        with c1:
            st.metric("สถานะความสด", status)
            st.metric("ค่า pH (ประมาณการ)", ph)
        with c2:
            st.write("**ข้อมูลทางเทคนิคของสี:**")
            st.text(f"Hue (เฉดสี): {h_val}°")
            st.text(f"Saturation: {s_val}")
            st.text(f"Value (ความสว่าง): {v_val}")

        if alert == "success": st.success(msg)
        elif alert == "warning": st.warning(msg)
        else: st.error(msg)
        
        # แสดงแถบสีที่ AI ตรวจพบจริง
        hex_c = '#%02x%02x%02x' % (int(dom_color[0]), int(dom_color[1]), int(dom_color[2]))
        st.markdown(f"**สีเด่นที่ตรวจพบ:** <div style='display:inline-block; width:60px; height:25px; background-color:{hex_c}; border:1px solid #000; vertical-align:middle; border-radius:4px;'></div> `{hex_c}`", unsafe_allow_html=True)
