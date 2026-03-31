import streamlit as st
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# ==========================================
# 1. ตั้งค่าหน้าเว็บ (UI/UX Design)
# ==========================================
st.set_page_config(page_title="Bio-Freshness Scanner", page_icon="🥩", layout="centered")

# ตกแต่งด้วย Custom CSS ให้ดูทันสมัย
st.markdown("""
    <style>
    .main {background-color: #F0F2F6;}
    h1 {color: #4B0082; text-align: center; font-family: 'Helvetica';}
    .stProgress > div > div > div > div {background-image: linear-gradient(to right, #ff9999 , #99ccff);}
    </style>
    """, unsafe_allow_html=True)

st.title("🥩 Bio-Freshness Scanner")
st.markdown("<p style='text-align: center; color: #666;'>ระบบ AI วิเคราะห์ความสดจากแถบวัดสารสกัดกะหล่ำปลีม่วง</p>", unsafe_allow_html=True)
st.divider()

# ==========================================
# 2. ฟังก์ชันวิเคราะห์สี (AI Core)
# ==========================================
def get_dominant_color(image, k=3):
    img = cv2.resize(image, (100, 100))
    pixels = img.reshape((-1, 3))
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    counts = np.bincount(kmeans.labels_)
    dominant_color = kmeans.cluster_centers_[np.argmax(counts)]
    return dominant_color

def analyze_freshness(rgb_color):
    color_uint8 = np.uint8([[rgb_color]])
    hsv_color = cv2.cvtColor(color_uint8, cv2.COLOR_RGB2HSV)[0][0]
    hue = hsv_color[0]
    
    # เกณฑ์การวัดสี Anthocyanin (ปรับจูนตามผลการทดลองจริงของคุณ)
    if hue > 145 or hue < 15:  
        return "สดมาก (Fresh)", "pH 2-4", 100, "success"
    elif 115 < hue <= 145:     
        return "ปกติ (Normal)", "pH 5-6", 75, "info"
    elif 75 < hue <= 115:      
        return "เริ่มไม่สด (Deteriorating)", "pH 7-8", 45, "warning"
    else:                      
        return "เน่าเสีย (Spoiled)", "pH 9+", 15, "error"

# ==========================================
# 3. ส่วนการแสดงผล (Frontend)
# ==========================================
st.subheader("📸 อัปโหลดรูปภาพแถบวัด")
uploaded_file = st.file_uploader("เลือกไฟล์ภาพ JPG หรือ PNG", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    with st.spinner('กำลังวิเคราะห์ค่าสี...'):
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        st.image(image, caption="ภาพที่อัปโหลด", use_container_width=True)
        
        # ประมวลผล
        dom_color = get_dominant_color(img_array)
        status, ph_level, score, alert_type = analyze_freshness(dom_color)
        
        st.divider()
        st.subheader("📊 ผลการวิเคราะห์")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("สถานะ", status)
        c2.metric("ค่า pH", ph_level)
        c3.metric("ความสด", f"{score}%")
        
        st.progress(score / 100.0)
        
        if alert_type == "success": st.success("✅ วัตถุดิบสดใหม่ ปลอดภัย")
        elif alert_type == "info": st.info("ℹ️ วัตถุดิบปกติ")
        elif alert_type == "warning": st.warning("⚠️ เริ่มไม่สด ควรระวัง")
        else: st.error("❌ เน่าเสีย ห้ามรับประทาน")

        # แสดงแถบสีที่ AI ตรวจพบ
        color_hex = '#%02x%02x%02x' % (int(dom_color[0]), int(dom_color[1]), int(dom_color[2]))
        st.markdown(f"**สีที่ตรวจพบ:** <div style='display:inline-block; width:50px; height:20px; background-color:{color_hex}; vertical-align:middle; border-radius:4px;'></div> {color_hex}", unsafe_allow_html=True)
