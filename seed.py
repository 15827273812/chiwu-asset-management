import datetime
from database import SessionLocal, engine, Base
from models import Category, Channel

# 预设分类
PRESET_CATEGORIES = [
    ("电子产品", "💻", [("手机", "📱"), ("电脑", "💻"), ("平板", "📟"), ("智能穿戴", "⌚"), ("耳机/音响", "🎧")]),
    ("家电", "🏠", [("电视", "📺"), ("冰箱", "🧊"), ("空调", "❄️"), ("洗衣机", "🧺"), ("厨房电器", "🍳"), ("清洁电器", "🧹")]),
    ("摄影器材", "📷", [("相机", "📷"), ("镜头", "🔭"), ("无人机", "✈️"), ("配件", "🎒")]),
    ("交通", "🚗", [("汽车", "🚗"), ("电动车", "🛵"), ("自行车", "🚲")]),
    ("家居", "🛋️", [("沙发/椅", "🛋️"), ("床/床垫", "🛏️"), ("桌子", "🪑"), ("灯具", "💡"), ("收纳", "🗄️")]),
    ("运动户外", "⚽", [("健身器材", "🏋️"), ("户外装备", "🏕️"), ("球类", "⚽")]),
    ("游戏娱乐", "🎮", [("游戏机", "🎮"), ("桌游", "🎲"), ("玩具", "🧸")]),
    ("收藏品", "💎", [("手表", "⌚"), ("手办", "🎎"), ("卡牌", "🃏"), ("艺术品", "🎨")]),
    ("服饰箱包", "👕", [("衣服", "👕"), ("鞋", "👟"), ("包", "🎒"), ("配饰", "💍")]),
    ("数码外设", "🖱️", [("键鼠", "⌨️"), ("显示器", "🖥️"), ("存储", "💾"), ("充电配件", "🔋"), ("网络设备", "📡")]),
    ("乐器", "🎸", [("吉他", "🎸"), ("键盘乐器", "🎹"), ("管弦乐", "🎺")]),
    ("其他", "📦", []),
]

PRESET_CHANNELS = ["淘宝", "京东", "天猫", "拼多多", "线下", "官网", "闲鱼", "海淘", "赠品", "其他"]


def init_db():
    Base.metadata.create_all(engine)
    # 迁移：为已有数据库添加 image 列
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('assets')]
    if 'image' not in columns:
        with engine.connect() as conn:
            conn.execute(text('ALTER TABLE assets ADD COLUMN image TEXT'))
            conn.commit()
            print("✅ 已添加 image 列到 assets 表")
    db = SessionLocal()
    try:
        # 初始化分类
        existing = db.query(Category).count()
        if existing == 0:
            for parent_name, parent_icon, children in PRESET_CATEGORIES:
                parent = Category(name=parent_name, icon=parent_icon, is_system=True,
                                  sort_index=len(PRESET_CATEGORIES))
                db.add(parent)
                db.flush()
                for i, (cname, cicon) in enumerate(children):
                    child = Category(name=cname, icon=cicon, parent_id=parent.id, sort_index=i)
                    db.add(child)
            db.commit()
            print(f"✅ 已初始化 {len(PRESET_CATEGORIES)} 个预设分类")

        # 初始化渠道
        existing_channels = db.query(Channel).count()
        if existing_channels == 0:
            for i, ch in enumerate(PRESET_CHANNELS):
                db.add(Channel(name=ch, is_preset=True, sort_index=i))
            db.commit()
            print(f"✅ 已初始化 {len(PRESET_CHANNELS)} 个预设渠道")

    finally:
        db.close()


if __name__ == "__main__":
    init_db()
