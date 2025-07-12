@echo off
echo 正在启动前端服务...
cd frontend
streamlit run app.py --server.port 8501
pause 