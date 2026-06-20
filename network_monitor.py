import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import subprocess
import platform
import time
from datetime import datetime
import os
import threading

# ======================
# 1. إعداد ملف البيانات
# ======================
FILE_NAME = "network_log.xlsx"

if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["التاريخ", "الوقت", "الموقع", "زمن الاستجابة (ms)", "الحالة"])
    df.to_excel(FILE_NAME, index=False)

# ======================
# 2. دالة فحص الاتصال
# ======================
def ping_host(host="google.com"):
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", host]
        start_time = time.time()
        output = subprocess.run(command, capture_output=True, text=True, timeout=5)
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)

        if output.returncode == 0:
            return response_time, "متصل"
        else:
            return None, "منقطع"
    except:
        return None, "خطأ"

# ======================
# 3. دالة تسجيل النتيجة في Excel
# ======================
def log_result(host, response_time, status):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    new_row = pd.DataFrame([{
        "التاريخ": date,
        "الوقت": time_str,
        "الموقع": host,
        "زمن الاستجابة (ms)": response_time if response_time else "N/A",
        "الحالة": status
    }])

    df = pd.read_excel(FILE_NAME)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(FILE_NAME, index=False)

# ======================
# 4. دورة الفحص المتكرر (في الخلفية)
# ======================
monitoring_active = False

def start_monitoring():
    global monitoring_active
    host = host_entry.get().strip()
    if not host:
        messagebox.showerror("خطأ", "الرجاء إدخال عنوان الموقع")
        return

    monitoring_active = True
    status_label.config(text="🔄 جاري الفحص...", fg="orange")
    threading.Thread(target=monitor_loop, args=(host,), daemon=True).start()

def monitor_loop(host):
    while monitoring_active:
        response_time, status = ping_host(host)
        log_result(host, response_time, status)

        if status == "متصل":
            status_label.config(text=f"✅ متصل - {response_time} ms", fg="green")
        else:
            status_label.config(text="❌ منقطع أو بطيء", fg="red")

        time.sleep(5)  # انتظر 5 ثواني بين كل فحص

def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    status_label.config(text="⏹️ توقف الفحص", fg="gray")

# ======================
# 5. واجهة المستخدم (Tkinter)
# ======================
root = tk.Tk()
root.title("🌐 فاحص الاتصال بالإنترنت")
root.geometry("600x400")
root.configure(bg="#f0f4f8")

# العنوان
tk.Label(root, text="🌐 فاحص الاتصال بالإنترنت", font=("Arial", 20, "bold"), bg="#f0f4f8", fg="#1e3a5f").pack(pady=15)

# إطار الإدخال
frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
frame.pack(pady=10, padx=20, fill="x")

tk.Label(frame, text="عنوان الموقع (مثل google.com):", font=("Arial", 12), bg="#ffffff").grid(row=0, column=0, padx=5, pady=10)
host_entry = tk.Entry(frame, font=("Arial", 12), width=25)
host_entry.grid(row=0, column=1, padx=5, pady=10)
host_entry.insert(0, "google.com")

# أزرار التحكم
btn_frame = tk.Frame(root, bg="#f0f4f8")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="▶️ بدء الفحص", command=start_monitoring, bg="#27ae60", fg="white", font=("Arial", 12), width=15).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="⏹️ إيقاف", command=stop_monitoring, bg="#e74c3c", fg="white", font=("Arial", 12), width=15).grid(row=0, column=1, padx=10)

# حالة الاتصال
status_label = tk.Label(root, text="⏳ في انتظار بدء الفحص", font=("Arial", 14), bg="#f0f4f8", fg="gray")
status_label.pack(pady=10)

# زر عرض السجلات
def show_logs():
    try:
        df = pd.read_excel(FILE_NAME)
        if df.empty:
            messagebox.showinfo("📋", "لا توجد سجلات بعد")
            return
        win = tk.Toplevel(root)
        win.title("سجلات الفحص")
        win.geometry("700x400")
        text = tk.Text(win, font=("Arial", 10))
        text.pack(fill="both", expand=True)
        text.insert(tk.END, df.to_string(index=False))
    except Exception as e:
        messagebox.showerror("خطأ", str(e))

tk.Button(root, text="📋 عرض السجلات", command=show_logs, bg="#2980b9", fg="white", font=("Arial", 12), width=20).pack(pady=10)

# التوقيع
tk.Label(root, text="By Narjes Almari", font=("Arial", 10), bg="#f0f4f8", fg="gray").pack(side=tk.BOTTOM, pady=10)

# ======================
# 6. تشغيل التطبيق
# ======================
root.mainloop()
