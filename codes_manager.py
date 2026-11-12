#!/usr/bin/env python3
import json
import hashlib
import getpass
import pathlib
import requests

BASE_URL = "https://albasem-tv.duckdns.org"
ADMIN_API = f"{BASE_URL}/api/codes/admin"
LOGIN_API = f"{BASE_URL}/api/codes/admin_login"
PASS_API = f"{BASE_URL}/api/codes/change_password"
ADULT_API = f"{BASE_URL}/api/codes/adult_pin"

TOKEN_FILE = pathlib.Path.home() / ".albasem_admin_auth.json"
DEFAULT_TOKEN = hashlib.sha256("satalet@gmail.com:Basem@2026:ALBASEM_SALT_2026".encode()).hexdigest()

def get_saved_token():
    if TOKEN_FILE.exists():
        try:
            data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
            if data.get("token"):
                return data["token"]
        except Exception:
            pass
    return DEFAULT_TOKEN

def save_token(token, email="satalet@gmail.com"):
    TOKEN_FILE.write_text(json.dumps({"email": email, "token": token}, indent=2), encoding="utf-8")

def ensure_login():
    print("\n🔐 جلسة الإدارة غير مفعلة أو تم تغيير كلمة المرور، يرجى تسجيل الدخول:")
    email = input("📧 البريد الإلكتروني [satalet@gmail.com]: ").strip() or "satalet@gmail.com"
    password = getpass.getpass("🔑 كلمة المرور السرية (أو اكتبها واضغط Enter): ").strip()
    if not password:
        password = input("🔑 كلمة المرور: ").strip()
    try:
        r = requests.post(LOGIN_API, json={"email": email, "password": password}, timeout=15)
        d = r.json()
        if d.get("success") and d.get("token"):
            save_token(d["token"], email)
            print("✅ تم تسجيل الدخول وحفظ الصلاحية على جهاز الكالي بنجاح!")
            return d["token"]
        else:
            print("❌", d.get("message", "بيانات الدخول غير صحيحة"))
    except Exception as e:
        print("❌ خطأ اتصال بالسيرفر:", e)
    return None

def call_admin_api(payload):
    token = get_saved_token()
    payload["token"] = token
    try:
        r = requests.post(ADMIN_API, json=payload, timeout=15)
        d = r.json()
        if not d.get("success") and "غير مصرح" in str(d.get("message", "")):
            new_tk = ensure_login()
            if new_tk:
                payload["token"] = new_tk
                r = requests.post(ADMIN_API, json=payload, timeout=15)
                d = r.json()
        return d
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_current_adult_pin():
    try:
        r = requests.get(f"{ADULT_API}?_t=1", timeout=10)
        d = r.json()
        return d.get("adult_pin", "2000")
    except Exception:
        return "2000"

def print_codes(codes):
    print("\n" + "=" * 88)
    print(f"{'#':<3} | {'الكود (10 أرقام)':<14} | {'اسم الزبون':<18} | {'الحالة':<11} | {'المتبقي':<10} | {'الأجهزة':<8} | {'الانتهاء'}")
    print("-" * 88)
    if not codes:
        print("   لا توجد كودات مسجلة حالياً.")
    for idx, c in enumerate(codes, 1):
        st_map = {
            "active": "🟢 فعال",
            "unused": "🔵 جديد",
            "suspended": "⛔ موقوف",
            "expired": "🔴 منتهي"
        }
        st_txt = st_map.get(c.get("status"), c.get("status", ""))
        days_txt = f"{c.get('days_left', 0)} يوم"
        devs_txt = f"{c.get('device_count', 0)}/{c.get('max_devices', 1)}"
        print(f"{idx:<3} | {c['code']:<14} | {str(c.get('customer_name') or 'مشترك')[:18]:<18} | {st_txt:<11} | {days_txt:<10} | {devs_txt:<8} | {c.get('expires_date_str', '-')}")
    print("=" * 88 + "\n")

def main():
    while True:
        adult_pin = get_current_adult_pin()
        print("\n👑 ==========[ الباسم سات | لوحة تحكم الكالي الشاملة ]========== 👑")
        print(" 1) ⚡ توليد كود اشتراك جديد (10 أرقام)")
        print(" 2) 📋 عرض كافة الكودات والأيام والأجهزة")
        print(" 3) ⏳ تعديل / تمديد عدد الأيام لكود")
        print(" 4) 📺 تعديل / زيادة عدد الأجهزة المسموحة لنفس الكود")
        print(" 5) ✏️  تعديل اسم الزبون على الكود")
        print(" 6) ⏸️  إيقاف مؤقت / إعادة تفعيل كود")
        print(" 7) 📱 تصفير قفل الأجهزة المسجلة للكود")
        print(" 8) 🗑️  حذف وإلغاء كود نهائياً")
        print(f" 9) 🔒 تغيير رمز القفل العائلي (الحالي: {adult_pin})")
        print("10) 🔑 تغيير باسورد أو إيميل الإدارة")
        print(" 0) 🚪 خروج")
        print("===================================================================")
        ch = input("👈 اختر رقم العملية: ").strip()

        if ch == "0":
            print("👋 يعطيك العافية يا أبو باسم!")
            break
        elif ch == "1":
            name = input("👤 اسم الزبون: ").strip() or "مشترك جديد"
            days = int(input("⏳ عدد الأيام (مثال 30): ").strip() or "30")
            devs = int(input("📺 عدد الأجهزة المسموحة (افتراضي 1): ").strip() or "1")
            res = call_admin_api({"action": "create", "customer_name": name, "duration_days": days, "max_devices": devs})
            if res.get("success") and res.get("codes"):
                newest = res["codes"][0]
                print(f"\n🎉 تم توليد الكود بنجاح:  [ {newest['code']} ]  | الزبون: {name} | المدة: {days} يوم | الأجهزة: {devs}")
                print_codes(res.get("codes", []))
            else:
                print("❌ خطأ:", res.get("message"))
        elif ch == "2":
            res = call_admin_api({"action": "list"})
            if res.get("success"):
                print_codes(res.get("codes", []))
            else:
                print("❌ خطأ:", res.get("message"))
        elif ch == "3":
            code = input("🔢 أدخل الكود (10 أرقام): ").strip()
            days = int(input("⏳ أدخل عدد الأيام الجديد: ").strip())
            res = call_admin_api({"action": "update_days", "code": code, "days": days})
            if res.get("success"):
                print(f"✅ تم تحديث مدة الكود ({code}) إلى {days} يوم!")
                print_codes(res.get("codes", []))
        elif ch == "4":
            code = input("🔢 أدخل الكود (10 أرقام): ").strip()
            devs = int(input("📺 أدخل عدد الأجهزة الجديد (مثال 2 أو 3): ").strip())
            res = call_admin_api({"action": "update_devices", "code": code, "max_devices": devs})
            if res.get("success"):
                print(f"✅ تم تحديث عدد الأجهزة المسموحة للكود ({code}) إلى {devs} أجهزة!")
                print_codes(res.get("codes", []))
        elif ch == "5":
            code = input("🔢 أدخل الكود (10 أرقام): ").strip()
            new_name = input("✏️ أدخل اسم الزبون الجديد: ").strip()
            if new_name:
                res = call_admin_api({"action": "update_name", "code": code, "customer_name": new_name})
                if res.get("success"):
                    print(f"✅ تم تعديل اسم الزبون للكود ({code}) إلى: {new_name}")
                    print_codes(res.get("codes", []))
        elif ch == "6":
            code = input("🔢 أدخل الكود (10 أرقام): ").strip()
            res = call_admin_api({"action": "toggle_active", "code": code})
            if res.get("success"):
                print(f"🔄 تم تغيير حالة الكود ({code}) بنجاح!")
                print_codes(res.get("codes", []))
        elif ch == "7":
            code = input("🔢 أدخل الكود (10 أرقام): ").strip()
            res = call_admin_api({"action": "reset_devices", "code": code})
            if res.get("success"):
                print(f"📱 تم تصفير الأجهزة المسجلة للكود ({code}) بنجاح!")
                print_codes(res.get("codes", []))
        elif ch == "8":
            code = input("🔢 أدخل الكود المراد حذفه (10 أرقام): ").strip()
            confirm = input(f"⚠️ هل أنت متأكد من حذف الكود {code} نهائياً؟ (y/n): ").strip().lower()
            if confirm in ("y", "yes", "نعم"):
                res = call_admin_api({"action": "delete", "code": code})
                if res.get("success"):
                    print(f"🗑️ تم حذف الكود ({code}) نهائياً!")
                    print_codes(res.get("codes", []))
        elif ch == "9":
            print(f"🔒 الرمز السري الحالي للقفل العائلي هو: ({adult_pin})")
            new_pin = input("🔒 أدخل الرمز الجديد للقفل العائلي: ").strip()
            if new_pin:
                tk = get_saved_token()
                r = requests.post(ADULT_API, json={"token": tk, "adult_pin": new_pin}, timeout=15).json()
                if not r.get("success") and "غير مصرح" in str(r.get("message", "")):
                    tk = ensure_login()
                    if tk:
                        r = requests.post(ADULT_API, json={"token": tk, "adult_pin": new_pin}, timeout=15).json()
                if r.get("success"):
                    print(f"✅ تم تغيير رمز القفل العائلي إلى ({r.get('adult_pin')}) على السيرفر والمنصة فوراً!")
                else:
                    print("❌ خطأ:", r.get("message"))
        elif ch == "10":
            old_p = input("🔑 كلمة المرور الحالية للإدارة: ").strip()
            new_p = input("🆕 كلمة المرور الجديدة للإدارة: ").strip()
            new_em = input("📧 إيميل جديد (اتركه فارغاً للإبقاء على الحالي): ").strip()
            if old_p and new_p:
                r = requests.post(PASS_API, json={"old_password": old_p, "new_password": new_p, "new_email": new_em}, timeout=15).json()
                if r.get("success") and r.get("token"):
                    save_token(r["token"], r.get("email", "satalet@gmail.com"))
                    print("✅ تم تغيير باسورد الإدارة وتحديث التوكن المحفوظ على الكالي بنجاح!")
                else:
                    print("❌ خطأ:", r.get("message"))

if __name__ == "__main__":
    main()
