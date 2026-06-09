#!/usr/bin/env python3
"""
Insert 10000 test asset records into ChiWu asset management database.
"""
import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "/home/mzh205/.openclaw/workspace/chiwu/data/chiwu.db"

# Product templates for realistic names
PRODUCT_TEMPLATES = [
    # (category_id_range, templates)
    (range(1,2), ["华为智慧屏", "小米电视", "索尼电视", "三星电视", "LG电视", "创维电视", "TCL电视", "海信电视"]),
    (range(2,3), ["iPhone", "Samsung Galaxy S", "小米", "华为 Mate", "OPPO Find", "vivo X", "荣耀", "一加"]),
    (range(3,4), ["MacBook Air", "MacBook Pro", "ThinkPad X1", "Dell XPS", "华为 MateBook", "小米 Book", "Surface Laptop", "ROG 幻"]),
    (range(4,5), ["iPad Pro", "iPad Air", "iPad", "iPad mini", "华为 MatePad", "小米平板", "三星 Tab S", "联想小新 Pad"]),
    (range(5,6), ["Apple Watch", "小米手环", "华为 Watch", "三星 Galaxy Watch", "佳明 Forerunner", "Fitbit", "OPPO Watch", "荣耀手环"]),
    (range(6,7), ["AirPods Pro", "Sony WH-1000XM", "Bose QC", "小米耳机", "华为 FreeBuds", "JBL", "漫步者", "Soundcore"]),
    (range(7,8), ["美的空调", "格力空调", "海尔冰箱", "西门子冰箱", "松下洗衣机", "小天鹅洗衣机", "戴森吸尘器", "石头扫地机"]),
    (range(8,9), ["索尼 XR", "三星 QLED", "LG OLED", "小米电视", "TCL 雷鸟", "海信 ULED", "创维", "华为智慧屏"]),
    (range(9,10), ["海尔冰箱", "西门子冰箱", "松下冰箱", "美的冰箱", "容声冰箱", "卡萨帝冰箱", "三星冰箱", "东芝冰箱"]),
    (range(10,11), ["格力空调", "美的空调", "海尔空调", "大金空调", "三菱电机", "松下空调", "奥克斯空调", "华凌空调"]),
    (range(11,12), ["小天鹅洗衣机", "松下洗衣机", "海尔洗衣机", "西门子洗衣机", "美的洗衣机", "LG洗衣机", "三星洗衣机", "博世洗衣机"]),
    (range(12,13), ["美的微波炉", "松下微波炉", "格兰仕微波炉", "飞利浦空气炸锅", "九阳豆浆机", "苏泊尔电饭煲", "小熊烤箱", "东菱咖啡机"]),
    (range(13,14), ["戴森吸尘器", "石头扫地机", "科沃斯扫地机", "追觅吸尘器", "云鲸扫地机", "米家扫拖机", "小狗吸尘器", "360扫地机"]),
    (range(14,15), ["索尼 α7", "佳能 EOS R", "尼康 Z", "富士 X-T", "松下 Lumix", "徕卡 Q", "哈苏 X", "大疆 Pocket"]),
    (range(15,16), ["索尼 α7 IV", "索尼 α7R V", "佳能 EOS R5", "佳能 EOS R6", "尼康 Z8", "尼康 Zf", "富士 X-T5", "松下 S5"]),
    (range(16,17), ["索尼 FE 24-70", "索尼 FE 70-200", "佳能 RF 24-105", "佳能 RF 50", "尼康 Z 24-70", "尼康 Z 50", "适马 35", "腾龙 28-75"]),
    (range(17,18), ["DJI Mini", "DJI Air", "大疆 Mavic", "大疆 Avata", "大疆 FPV", "Autel EVO", "大疆 Inspire", "大疆 Phantom"]),
    (range(18,19), ["三脚架", "相机包", "滤镜套裝", "SD卡", "稳定器", "麦克风", "补光灯", "快装板"]),
    (range(19,20), ["丰田凯美瑞", "本田雅阁", "宝马3系", "奔驰C级", "奥迪A4", "特斯拉 Model 3", "大众帕萨特", "比亚迪汉"]),
    (range(20,21), ["宝马5系", "奔驰E级", "奥迪A6", "特斯拉 Model Y", "比亚迪宋", "理想L7", "蔚来ES6", "小鹏P7"]),
    (range(21,22), ["雅迪电动车", "小牛电动车", "九号电动车", "爱玛电动车", "台铃电动车", "绿源电动车", "新日电动车", "五星钻豹"]),
    (range(22,23), ["捷安特", "美利达", "Trek", "Specialized", "喜德盛", "迪卡侬", "永久自行车", "凤凰自行车"]),
    (range(23,24), ["宜家沙发", "顾家沙发", "MUJI沙发", "芝华仕沙发", "懒人沙发", "日式沙发", "北欧沙发", "电竞椅"]),
    (range(24,25), ["芝华仕头等舱", "顾家家居沙发", "北欧表情沙发", "宜家沙发", "minimax沙发", "造作沙发", "HAY沙发", "梵几沙发"]),
    (range(25,26), ["丝涟床垫", "舒达床垫", "席梦思床垫", "喜临门床垫", "慕思床垫", "雅兰床垫", "穗宝床垫", "泰普尔床垫"]),
    (range(26,27), ["宜家桌子", "北欧书桌", "升降桌", "电竞桌", "实木餐桌", "折叠桌", "边桌", "梳妆台"]),
    (range(27,28), ["飞利浦台灯", "米家台灯", "宜家台灯", "Yeelight", "柏曼台灯", "明基护眼灯", "欧普台灯", "松下台灯"]),
    (range(28,29), ["宜家收纳柜", "MUJI收纳盒", "塑料收纳箱", "布艺收纳", "书架", "鞋柜", "置物架", "抽屉收纳"]),
    (range(29,30), ["划船机", "跑步机", "动感单车", "椭圆机", "哑铃套装", "瑜伽垫", "引体向上架", "跳绳"]),
    (range(30,31), ["划船机", "跑步机", "动感单车", "椭圆机", "史密斯机", "龙门架", "哑铃架", "引体向上器"]),
    (range(31,32), ["帐篷", "睡袋", "登山包", "冲锋衣", "登山杖", "户外椅", "保温杯", "头灯"]),
    (range(32,33), ["斯伯丁篮球", "威尔胜篮球", "李宁篮球", "LI-NING羽毛球拍", "尤尼克斯羽毛球拍", "蝴蝶乒乓球拍", "红双喜乒乓球", "Wilson网球拍"]),
    (range(33,34), ["PS5", "Xbox Series X", "Nintendo Switch", "Steam Deck", "PS VR2", "Xbox手柄", "Switch Pro手柄", "游戏方向盘"]),
    (range(34,35), ["PS5 光驱版", "PS5 数字版", "Xbox Series X", "Xbox Series S", "Nintendo Switch", "Switch OLED", "Steam Deck", "ROG Ally"]),
    (range(35,36), ["卡坦岛", "卡卡頌", "璀璨宝石", "七大奇迹", "画物语", "三国杀", "狼人杀", "UNO"]),
    (range(36,37), ["乐高", "万代模型", "田宫模型", "GUNDAM", "变形金刚", "芭比娃娃", "遥控车", "无人机玩具"]),
    (range(37,38), ["邮票珍藏", "纪念币", "古董钟表", "瓷器", "紫砂壶", "玉石", "钱币", "徽章"]),
    (range(38,39), ["劳力士", "欧米茄", "卡西欧", "Apple Watch", "浪琴", "天梭", "西铁城", "精工"]),
    (range(39,40), ["初音未来", "米库", "明日方舟", "原神手办", "Fate手办", "高达", "龙珠", "海贼王手办"]),
    (range(40,41), ["宝可梦卡", "游戏王卡", "MTG卡", "三国杀卡", "球星卡", "海贼王卡", "数码暴龙卡", "龙珠卡"]),
    (range(41,42), ["油画", "水墨画", "版画", "雕塑", "摄影作品", "装置艺术", "陶瓷", "数字艺术"]),
    (range(42,43), ["羽绒服", "冲锋衣", "西装", "大衣", "卫衣", "衬衫", "牛仔裤", "T恤"]),
    (range(43,44), ["Moncler羽绒服", "Canada Goose", "始祖鸟冲锋衣", "北面冲锋衣", "优衣库大衣", "ZARA西装", "H&M卫衣", "Nike卫衣"]),
    (range(44,45), ["Nike", "Adidas", "Jordan", "New Balance", "ASICS", "Converse", "Vans", "Onitsuka Tiger"]),
    (range(45,46), ["LV包包", "Gucci包包", "Chanel包包", "爱马仕包包", "Prada背包", "北面背包", "Osprey背包", "MCM书包"]),
    (range(46,47), ["卡地亚手镯", "潘多拉手链", "Tiffany项链", "APM耳环", "DW手表", "雷朋眼镜", "GM墨镜", "皮带"]),
    (range(47,48), ["罗技鼠标", "雷蛇键盘", "Cherry键盘", "Filco键盘", "罗技键盘", "雷蛇鼠标", "ikbc键盘", "阿米洛键盘"]),
    (range(48,49), ["罗技MX", "雷蛇蝰蛇", "罗技G Pro", "Filco圣手", "Leopold", "HHKB", "宁芝", "阿米洛"]),
    (range(49,50), ["戴尔显示器", "LG显示器", "三星显示器", "AOC显示器", "华硕显示器", "明基显示器", "小米显示器", "优派显示器"]),
    (range(50,51), ["三星SSD", "西部数据SSD", "希捷HDD", "致态SSD", "闪迪SD卡", "金士顿U盘", "雷克沙TF卡", "海康威视存储"]),
]

# Model/suffix variations for more realism
MODEL_VARIANTS = ["Pro", "Max", "Ultra", "Plus", "Lite", "Air", "Mini", "SE", "Gen", ""]
COLORS = ["深空灰", "银色", "金色", "蓝色", "绿色", "粉色", "白色", "黑色", "白色/银色", "午夜色", "星光色", "紫色", "红色"]

# Status distribution
STATUS_WEIGHTS = [0.80, 0.12, 0.08]  # active, sold, discarded
STATUS_OPTIONS = ["active", "sold", "discarded"]

# Currency options
CURRENCIES = ["CNY", "USD", "HKD", "JPY"]
CURRENCY_WEIGHTS = [0.85, 0.08, 0.05, 0.02]


def random_date(start_year=2020, end_year=2026):
    """Generate a random date between start_year-01-01 and end_year-12-31."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def pick_product(category_id):
    """Pick a realistic product name based on category_id."""
    for cat_range, templates in PRODUCT_TEMPLATES:
        if category_id in cat_range:
            base = random.choice(templates)
            break
    else:
        base = f"分类{category_id}物品"

    suffix = f"#{random.randint(1, 9999):04d}"
    variant = random.choice(MODEL_VARIANTS)
    color = random.choice(COLORS)
    
    if variant:
        name = f"{base} {variant} {suffix}"
    else:
        name = f"{base} {suffix}"
    
    # Occasionally add color
    if random.random() < 0.3:
        name += f" ({color})"
    
    return name


def generate_serial():
    """Generate a fake serial number."""
    prefix = random.choice(["SN", "MZ", "CH", "WL", "HW", "SG", "AP", "DE", "LN", "SZ"])
    nums = ''.join(random.choices('0123456789ABCDEF', k=10))
    return f"{prefix}-{nums}"


def generate_notes(category_id, status):
    """Generate contextual notes."""
    if status == "sold":
        return f"已售出，售价¥{random.randint(100, 50000)}"
    elif status == "discarded":
        reasons = ["因故障报废", "已折旧清零", "已回收处理", "超过使用寿命", "外观严重损坏"]
        return random.choice(reasons)
    
    # Active items may or may not have notes
    if random.random() < 0.25:
        templates = [
            "日常使用，状态良好",
            "闲置未用，近全新",
            "已过保，自行维护中",
            "循环使用中",
            "配件齐全",
            "轻微磨损",
            "保修期内，正常使用",
        ]
        return random.choice(templates)
    return ""


def main():
    random.seed(42)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check existing count
    cursor.execute("SELECT COUNT(*) FROM assets")
    existing_count = cursor.fetchone()[0]
    print(f"Existing records: {existing_count}")
    
    target = 10000
    batch_size = 500  # Insert in batches for performance
    
    records = []
    
    for i in range(target):
        category_id = random.randint(1, 57)  # categories 1-57
        
        name = pick_product(category_id)
        status = random.choices(STATUS_OPTIONS, weights=STATUS_WEIGHTS, k=1)[0]
        purchase_price = round(random.uniform(50, 80000), 2)
        purchase_date = random_date(2020, 2026).strftime("%Y-%m-%d")
        
        # current_value: for active items, depreciate from purchase_price
        # for sold/discarded, current_value reflects residual
        if status == "active":
            age_years = (datetime.now() - datetime.strptime(purchase_date, "%Y-%m-%d")).days / 365.25
            depreciation = min(0.9, age_years * 0.15)
            current_value = round(purchase_price * (1 - depreciation), 2)
        elif status == "sold":
            current_value = round(purchase_price * random.uniform(0.3, 0.8), 2)
        else:  # discarded
            current_value = 0.0
        
        serial_number = generate_serial()
        notes = generate_notes(category_id, status)
        cover_photo = ""
        image = ""
        
        currency = random.choices(CURRENCIES, weights=CURRENCY_WEIGHTS, k=1)[0]
        channel_id = random.randint(1, 5) if random.random() < 0.8 else None
        
        # purchase_date ± random days for target_date
        target_date_val = random_date(2023, 2027).strftime("%Y-%m-%d")
        target_price = round(purchase_price * random.uniform(0.5, 1.5), 2)
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        record = (
            name, category_id, channel_id, purchase_price, purchase_date,
            current_value, target_price, target_date_val, status, currency,
            i,  # sort_index
            cover_photo, image, notes,
            None, None, None,  # warranty fields
            now, now,  # created_at, updated_at
            round(current_value * random.uniform(0.1, 0.5), 2)  # residual_value
        )
        records.append(record)
        
        if len(records) >= batch_size:
            cursor.executemany("""
                INSERT INTO assets (
                    name, category_id, channel_id, purchase_price, purchase_date,
                    current_value, target_price, target_date, status, currency_code,
                    sort_index, cover_photo, image, notes,
                    warranty_months, warranty_start_date, warranty_end_date,
                    created_at, updated_at, residual_value
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            conn.commit()
            print(f"Inserted {i + 1} records...")
            records = []
    
    # Insert remaining
    if records:
        cursor.executemany("""
            INSERT INTO assets (
                name, category_id, channel_id, purchase_price, purchase_date,
                current_value, target_price, target_date, status, currency_code,
                sort_index, cover_photo, image, notes,
                warranty_months, warranty_start_date, warranty_end_date,
                created_at, updated_at, residual_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()
        print(f"Inserted {target} records...")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM assets")
    final_count = cursor.fetchone()[0]
    print(f"\n✅ Total records after insertion: {final_count}")
    print(f"   New records added: {final_count - existing_count}")
    
    # Sample check
    cursor.execute("SELECT id, name, category_id, status, purchase_price, purchase_date FROM assets ORDER BY id LIMIT 5")
    print("\n📋 First 5 records:")
    for row in cursor.fetchall():
        print(f"   ID={row[0]}, Name={row[1]}, Cat={row[2]}, Status={row[3]}, Price=¥{row[4]}, Date={row[5]}")
    
    cursor.execute("SELECT id, name, category_id, status, purchase_price, purchase_date FROM assets ORDER BY id DESC LIMIT 5")
    print("\n📋 Last 5 records:")
    for row in cursor.fetchall():
        print(f"   ID={row[0]}, Name={row[1]}, Cat={row[2]}, Status={row[3]}, Price=¥{row[4]}, Date={row[5]}")
    
    # Status distribution
    cursor.execute("SELECT status, COUNT(*) FROM assets GROUP BY status")
    print("\n📊 Status distribution:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")
    
    conn.close()


if __name__ == "__main__":
    main()
