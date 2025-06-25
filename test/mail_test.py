import smtplib, os

try:
    with smtplib.SMTP('smtp.qq.com', 587) as server:
        server.starttls()  # 启用 TLS
        server.login('1941227494@qq.com', '')
        print("SMTP login successful!")
except Exception as e:
    print(f"SMTP login failed: {e}")
