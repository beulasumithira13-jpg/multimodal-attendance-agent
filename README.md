# ClassPulse — Multimodal Attendance & Engagement Agent

Beginner-friendly Streamlit prototype with:
- Editable attendance register and CSV import/export
- OpenCV face-region detection from a still image (no identity recognition)
- Audio duration, RMS energy and zero-crossing analysis
- Attendance charts and privacy guidance

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. (Recommended) create a virtual environment.
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `streamlit run app.py`
6. Open the local URL Streamlit shows, usually `http://localhost:8501`.

## Important limitations
This is an educational prototype, not a validated production attendance system. It does not identify people, automatically mark attendance from faces, transcribe speech, or produce a scientifically valid engagement score. Use consented media and verify attendance manually. Sample attendance records are fictional.
