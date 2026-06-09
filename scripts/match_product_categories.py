"""
将 products 表中的中文 category 名映射到系统 categories 表的 id。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Category, Product
from sqlalchemy import text

# ===== 映射规则 =====
# key = products.category 的值
# value = categories.name（必须完全一致）
CATEGORY_MAP = {
    "手机": "手机",
    "电脑": "电脑",
    "平板": "平板",
    "手表": "智能穿戴",   # 产品中的"手表"映射到系统的"智能穿戴"
    "音频": "耳机/音响",
    "影音": "电视",       # 影音类产品映射到电视目录
    "摄影": "摄影器材",
    "家电": "家电",
    "游戏": "游戏娱乐",
    "VR": "游戏娱乐",     # VR 产品归入游戏娱乐
    "外设": "数码外设",
    "存储": "存储",
    "充电配件": "充电配件",
    "网络设备": "网络设备",
    "车辆": "电动车",     # 产品中车辆主要是电动车
    "家具": "家居",
    "其他": "其他",
}

def main():
    db = SessionLocal()

    # 先建分类名称→ID 的查找表
    cats = db.query(Category).all()
    name_to_id = {c.name: c.id for c in cats}
    print(f"系统共 {len(cats)} 个分类")

    mapped = 0
    unmapped = []
    for prod_name, sys_cat_name in CATEGORY_MAP.items():
        cat_id = name_to_id.get(sys_cat_name)
        if cat_id is None:
            print(f"❌ 找不到系统分类 \"{sys_cat_name}\"（来自产品分类 \"{prod_name}\"）")
            unmapped.append(prod_name)
            continue

        # 更新该分类的所有产品
        count = db.execute(
            text(f"UPDATE products SET category_id = {cat_id} WHERE category = '{prod_name}'")
        ).rowcount
        mapped += count
        print(f"  \"{prod_name}\" → \"{sys_cat_name}\"(id={cat_id}) → {count}条")

    db.commit()

    # 检查是否有遗漏
    result = db.execute(text("SELECT DISTINCT category FROM products WHERE category_id IS NULL AND category IS NOT NULL"))
    for r in result:
        name = r[0]
        cnt = db.execute(text(f"SELECT COUNT(*) FROM products WHERE category = '{name}'")).scalar()
        print(f"⚠️ 未匹配: \"{name}\" ({cnt}条)")
        unmapped.append(name)

    print(f"\n✅ 已匹配 {mapped} 条")
    if unmapped:
        print(f"⚠️ 未匹配: {len(unmapped)} 个分类")
    
    # 验证
    total = db.query(Product).count()
    has_id = db.query(Product).filter(Product.category_id != None).count()
    print(f"产品总数: {total}, 有 category_id: {has_id}")

if __name__ == "__main__":
    main()
