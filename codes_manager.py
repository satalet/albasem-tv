#!/usr/bin/env python3
import hashlib
import requests

API_URL = "https://albasem-tv.duckdns.org/api/codes/admin"
ADMIN_TOKEN = hashlib.sha256("satalet@gmail.com:Basem@2026:ALBASEM_SALT_2026".encode()).hexdigest()

def call_api(payload):
    payload["token"] = ADMIN_TOKEN
    r = requests.post(API_URL, json=payload, timeout=15)
    return r.json()

def print_codes(codes):
    print("\n" + "="*76)
    print(f"{'الكود (10 أرقام)':<14} | {'اسم الزبون':<18} | {'الحالة':<12} | {'الأيام المتبقية':<12} | {'الأجهزة'}")
    print("-" * 76)
    for c in codes:
        print(f"{c['code']:<14} | {c['customer_name'][:18]:<18} | {c['status']:<12} | {str(c['days_left']) + ' يوم':<12} | {c['device_count']}/{c['max_devices']}")
    print("="*76 + "\n")

def main():
    while True:
        print("👑 الباسم سات - برنامج إدارة وتوليد الكودات (10 أرقام) 👑")
        print("1) ⚡ توليد كود جديد لزبون")
        print("2) 📋 عرض كافة الكودات والأيام المتبقية")
        print("3) ⏳ تعديل / تمديد عدد الأيام لكود")
        print("4) 📺 تعديل / زيادة عدد الأجهزة المسموحة على نفس الكود")
        print("5) ⏸️ إيقاف مؤقت / إعادة تفعيل كود")
        print("6) 📱 تصفير قفل الأجهزة المسجلة للكود")
        print("7) 🗑️ حذف وإلغاء كود نهائياً")
        print("0) خروج")
        ch = input("اختر رقم العملية: ").strip()
        if ch == "0":
            break
        elif ch == "1":
            name = input("اسم الزبون: ").strip() or "زبون جديد"
            days = int(input("عدد الأيام (مثال 30): ").strip() or "30")
            devs = int(input("عدد الأجهزة المسموحة (افتراضي 1): ").strip() or "1")
            res = call_api({"action": "create", "customer_name": name, "duration_days": days, "max_devices": devs})
            if res.get("success") and res.get("codes"):
                newest = res["codes"][0]
                print(f"\n🎉 تم توليد الكود بنجاح:  {newest['code']}  (المدة: {days} يوم | الأجهزة: {devs})\n")
        elif ch == "2":
            res = call_api({"action": "list"})
            print_codes(res.get("codes", []))
        elif ch == "3":
            code = input("أدخل الكود (10 أرقام): ").strip()
            days = int(input("أدخل عدد الأيام الجديد: ").strip())
            res = call_api({"action": "update_days", "code": code, "days": days})
            print("✅ تم تحديث الأيام بنجاح!")
            print_codes(res.get("codes", []))
        elif ch == "4":
            code = input("أدخل الكود (10 أرقام): ").strip()
            devs = int(input("أدخل عدد الأجهزة المسموح الجديد (مثال 2 أو 3): ").strip())
            res = call_api({"action": "update_devices", "code": code, "max_devices": devs})
            print(f"✅ تم تحديث الحد المسموح إلى {devs} أجهزة على نفس الكود!")
            print_codes(res.get("codes", []))
        elif ch == "5":
            code = input("أدخل الكود (10 أرقام): ").strip()
            res = call_api({"action": "toggle_active", "code": code})
            print("🔄 تم تغيير حالة الكود!")
            print_codes(res.get("codes", []))
        elif ch == "6":
            code = input("أدخل الكود (10 أرقام): ").strip()
            res = call_api({"action": "reset_devices", "code": code})
            print("📱 تم تصفير الأجهزة المرتبطة بالكود!")
        elif ch == "7":
            code = input("أدخل الكود المراد حذفه (10 أرقام): ").strip()
            res = call_api({"action": "delete", "code": code})
            print("🗑️ تم حذف الكود نهائياً!")
            print_codes(res.get("codes", []))

if __name__ == "__main__":
    main()
