import datetime
import sqlalchemy
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum

class AssetStatus(str, enum.Enum):
    active = "active"       # 在用
    sold = "sold"           # 已出售
    discarded = "discarded" # 报废/赠送
    lost = "lost"           # 丢失

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True)
    purchase_price = Column(Float, nullable=True)
    purchase_date = Column(Date, nullable=True)
    current_value = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True)  # 目标价格（来自心愿或手动设定）
    target_date = Column(Date, nullable=True)    # 目标日期
    residual_value = Column(Float, nullable=True)  # 预估残值（用户手动填）
    status = Column(String(20), default="active")
    currency_code = Column(String(3), default="CNY")
    sort_index = Column(Integer, default=0)
    cover_photo = Column(Text, nullable=True)       # base64 缩略图
    image = Column(Text, nullable=True)              # 照片 base64
    notes = Column(Text, nullable=True)
    warranty_months = Column(Integer, nullable=True)  # 保质期月数
    warranty_start_date = Column(Date, nullable=True) # 保质期起始日（默认=购买日）
    warranty_end_date = Column(Date, nullable=True)   # 保障到期日（前端计算）
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    category = relationship("Category", backref="assets")
    channel = relationship("Channel", backref="assets")
    maintenances = relationship("Maintenance", backref="asset", cascade="all, delete-orphan", order_by="Maintenance.date.desc()")

    @property
    def holding_days(self):
        if not self.purchase_date:
            return 0
        delta = datetime.date.today() - self.purchase_date
        return max(1, delta.days)

    @property
    def total_maintenance_cost(self):
        return sum((m.amount or 0) for m in self.maintenances)

    @property
    def tco(self):
        return (self.purchase_price or 0) + self.total_maintenance_cost

    @property
    def net_cost(self):
        """净成本 = 购买价 + 维护费 - 残值（优先手动残值，无则按品类自动算）"""
        residual = self.residual_value
        if residual is None:
            # 自动残值（品类折旧率表）
            residual = self._auto_residual_value() or 0
        return max(0, self.tco - residual)

    # 品类残值率配置（顶级分类ID → 年折旧率）
    _DEPRECIATION_RATES = {
        1: 0.15, 7: 0.20, 14: 0.15, 19: 0.15, 23: 0.20,
        29: 0.20, 33: 0.15, 37: 0.10, 42: 0.25, 47: 0.15,
        53: 0.15, 57: 0.20,
    }

    def _auto_residual_value(self):
        if not self.purchase_price or not self.purchase_date:
            return None
        days = self.holding_days
        if days < 365:
            return round(self.purchase_price * 0.8, 2)
        # 查品类
        rate = 0.20
        if self.category_id:
            # 简单用自身 category_id（因为子类没存父子关系）
            rate = self._DEPRECIATION_RATES.get(self.category_id, 0.20)
        years = days / 365.0
        value = self.purchase_price * ((1 - rate) ** years)
        return round(max(value, 0), 2)

    @property
    def daily_cost(self):
        """日均成本 = net_cost / 持有天数（减去残值的实际日均支出）"""
        days = self.holding_days
        if days <= 0 or not self.purchase_price:
            return None
        return round(self.net_cost / days, 2)

    @property
    def warranty_status(self):
        """warranty_status: 'warrantying' (保障中), 'expired' (已过保), 'none' (无保修)"""
        if not self.warranty_months or self.warranty_months <= 0:
            return 'none'
        # 优先用前端传入的 warranty_end_date
        if self.warranty_end_date:
            if datetime.date.today() <= self.warranty_end_date:
                return 'warrantying'
            return 'expired'
        start = self.warranty_start_date or self.purchase_date
        if not start:
            return 'none'
        # 精确月份计算（与前端的 setMonth 一致）
        m = self.warranty_months
        y = start.year + (start.month - 1 + m) // 12
        mo = (start.month - 1 + m) % 12 + 1
        d = min(start.day, __import__('calendar').monthrange(y, mo)[1])
        end = datetime.date(y, mo, d)
        if datetime.date.today() <= end:
            return 'warrantying'
        return 'expired'


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    icon = Column(String(10), default="📦")
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_index = Column(Integer, default=0)
    is_system = Column(Boolean, default=False)

    children = relationship("Category", backref=sqlalchemy.orm.backref("parent", remote_side=[id]),
                             cascade="all, delete-orphan")


class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    is_preset = Column(Boolean, default=False)
    sort_index = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)


class Maintenance(Base):
    __tablename__ = "maintenances"
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    title = Column(String(100), nullable=False)
    amount = Column(Float, nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    brand = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)  # 品类名（手机/手表/电脑...）
    price = Column(Float, nullable=True)          # 参考价
    year = Column(Integer, nullable=True)         # 发布年份
    icon = Column(String(50), nullable=True)      # mdi:xxx
    icon_url = Column(String(200), nullable=True)
    keywords = Column(Text, nullable=True)        # JSON 数组 ["关键词1", "关键词2"]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class WishItem(Base):
    __tablename__ = "wish_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    target_price = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    target_date = Column(Date, nullable=True)
    note = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True)
    is_done = Column(Boolean, default=False)
    converted_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    converted_asset = relationship("Asset")
    category = relationship("Category", foreign_keys=[category_id])
    channel = relationship("Channel", foreign_keys=[channel_id])
