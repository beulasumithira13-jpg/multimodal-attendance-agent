import streamlit as st
import pandas as pd
import numpy as np
import cv2, tempfile, os
import plotly.express as px
from datetime import date

st.set_page_config(page_title="ClassPulse", page_icon="🎓", layout="wide")
st.markdown("""<div style="padding:22px;border-radius:16px;background:linear-gradient(120deg,#182b72,#3978e8);color:white"><h1>🎓 ClassPulse</h1><p>Multimodal Attendance & Engagement Agent</p></div>""", unsafe_allow_html=True)

with st.sidebar:
    page=st.radio("Modules",["Overview","Attendance Register","Vision Analysis","Audio Analysis","Reports & Privacy"])
    st.caption("Educational prototype. Uploaded media is processed during this session; no identity recognition.")

def attendance():
    if "att" not in st.session_state:
        st.session_state.att=pd.DataFrame([
            {"Student ID":"STU001","Student Name":"Student 1","Date":str(date.today()),"Status":"Present"},
            {"Student ID":"STU002","Student Name":"Student 2","Date":str(date.today()),"Status":"Present"},
            {"Student ID":"STU003","Student Name":"Student 3","Date":str(date.today()),"Status":"Absent"},
            {"Student ID":"STU004","Student Name":"Student 4","Date":str(date.today()),"Status":"Late"},
        ])
    return st.session_state.att

if page=="Overview":
    df=attendance()
    a,b,c=st.columns(3)
    a.metric("Register entries",len(df))
    b.metric("Present / Late",int(df.Status.isin(["Present","Late"]).sum()))
    c.metric("Attendance rate",f"{100*df.Status.isin(['Present','Late']).sum()/len(df):.1f}%" if len(df) else "0%")
    st.subheader("Attendance snapshot")
    st.plotly_chart(px.pie(df,names="Status",hole=.4),use_container_width=True)
    st.info("Edit sample records in Attendance Register. Use Vision and Audio modules to analyse consented sample media.")

elif page=="Attendance Register":
    st.subheader("🧾 Attendance Register")
    upload=st.file_uploader("Import CSV",type=["csv"])
    if upload:
        imported=pd.read_csv(upload)
        if {"Student ID","Student Name","Date","Status"}.issubset(imported.columns):
            st.session_state.att=imported
        else: st.error("CSV needs Student ID, Student Name, Date, Status columns.")
    edited=st.data_editor(attendance(),num_rows="dynamic",use_container_width=True,
        column_config={"Status":st.column_config.SelectboxColumn(options=["Present","Absent","Late"])})
    if st.button("Save attendance",type="primary"):
        st.session_state.att=edited
        st.success("Saved for this session.")
    st.download_button("Download attendance CSV",edited.to_csv(index=False).encode(),f"attendance_{date.today()}.csv","text/csv")

elif page=="Vision Analysis":
    st.subheader("👁️ Vision Module — Face-region estimate")
    st.write("Upload a photo. OpenCV detects face-like regions only; it does not identify people or automatically mark attendance.")
    photo=st.file_uploader("Upload image",type=["png","jpg","jpeg"])
    if photo:
        image=cv2.imdecode(np.frombuffer(photo.getvalue(),np.uint8),cv2.IMREAD_COLOR)
        if image is None: st.error("Could not read image.")
        else:
            gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            detector=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
            faces=detector.detectMultiScale(gray,1.1,5,minSize=(30,30))
            out=image.copy()
            for x,y,w,h in faces: cv2.rectangle(out,(x,y),(x+w,y+h),(40,200,80),2)
            l,r=st.columns([2,1])
            l.image(cv2.cvtColor(out,cv2.COLOR_BGR2RGB),use_container_width=True)
            r.metric("Estimated face regions",len(faces))
            r.caption("May miss faces or detect false positives. Do not treat as proof of identity or attendance.")
            st.download_button("Download annotated image",cv2.imencode(".png",out)[1].tobytes(),"vision_result.png","image/png")

elif page=="Audio Analysis":
    st.subheader("🔊 Audio Module — Sound activity")
    st.write("Upload a short audio clip. This measures acoustic features only, not speech meaning or student engagement.")
    audio=st.file_uploader("Upload audio",type=["wav","mp3","ogg","flac"])
    if audio:
        st.audio(audio)
        try:
            import librosa
            with tempfile.NamedTemporaryFile(delete=False,suffix=os.path.splitext(audio.name)[1]) as tmp:
                tmp.write(audio.getvalue()); path=tmp.name
            y,sr=librosa.load(path,sr=None,mono=True); os.unlink(path)
            rms=librosa.feature.rms(y=y)[0]
            zcr=librosa.feature.zero_crossing_rate(y)[0]
            x,yc,z=st.columns(3)
            x.metric("Duration",f"{len(y)/sr:.1f} sec")
            yc.metric("Mean RMS energy",f"{float(np.mean(rms)):.4f}")
            z.metric("Mean zero-crossing rate",f"{float(np.mean(zcr)):.4f}")
            st.plotly_chart(px.line(x=librosa.frames_to_time(np.arange(len(rms)),sr=sr),y=rms,labels={"x":"Time (sec)","y":"RMS energy"},title="Sound energy over time"),use_container_width=True)
        except Exception as e:
            st.error("Audio analysis failed. Check dependencies and file format.")
            st.code(str(e))

else:
    st.subheader("📊 Reports & Privacy")
    df=attendance()
    st.plotly_chart(px.bar(df,x="Status",title="Attendance records"),use_container_width=True)
    st.download_button("Export report CSV",df.to_csv(index=False).encode(),"classpulse_report.csv","text/csv")
    st.markdown("""### Responsible use
- Obtain permission before uploading classroom images or recordings.
- Use fictional IDs for demos and protect student information.
- Face detection does not identify people.
- Audio energy is not a reliable engagement score.
- Verify attendance manually before making academic decisions.
- This prototype does not permanently store uploaded media.""")
