#!/bin/bash
echo "Starting Gridseek Frontend..."
echo

# 检查是否安装了依赖
echo "Checking dependencies..."
if ! python -c "import streamlit" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo
fi

echo "Starting application..."
echo "Open your browser and go to the URL shown below:"
echo

# 启动应用
streamlit run app.py
