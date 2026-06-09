#!/usr/bin/env python3
"""将 product_db.json 导入到数据库中 products 表"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
from models import Product

def main():
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "product_db.json")
    if not os.path.exists(json_path):
        print(f"未找到: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    db = SessionLocal()
    try:
        # 清空旧数据
        db.query(Product).delete()
        for i, item in enumerate(items):
            p = Product(
                name=item.get("name", ""),
                brand=item.get("brand", ""),
                category=item.get("category", ""),
                price=item.get("price"),
                year=item.get("year"),
                icon=item.get("icon", ""),
                icon_url=item.get("icon_url", ""),
                keywords=json.dumps(item.get("keywords", []), ensure_ascii=False),
            )
            db.add(p)
        db.commit()
        print(f"✅ 成功导入 {len(items)} 条产品至数据库")
    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
