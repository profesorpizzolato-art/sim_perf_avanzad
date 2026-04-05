cd menfa-well-sim
git init
git add .
git commit -m "feat: IPCL MENFA Well Simulator V7.0"
git branch -M main
git remote add origin https://github.com/profesorpizzolato-art/sim_perf_avanzad.git
git push -u origin main
streamlit --version
streamlit hello
streamlit run app.py
