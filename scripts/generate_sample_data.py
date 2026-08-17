"""
MerchIq Sample Data Generator
Populates all 6 business dimensions with realistic retail data:
- Inventory, Pricing, Promotions, Region, Weather, Competitor
"""
import os
import sys
import random
from datetime import datetime, timedelta
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("TESTING", "false")

from app.core.database import SessionLocal, engine, Base
from app.models import models
from app.core.config import settings

Base.metadata.create_all(bind=engine)

REGIONS = [
    {"name": "Northeast", "code": "NE", "country": "USA", "population": 55_000_000, "avg_income": 78000, "climate_zone": "humid_subtropical"},
    {"name": "Southeast", "code": "SE", "country": "USA", "population": 98_000_000, "avg_income": 62000, "climate_zone": "humid_subtropical"},
    {"name": "Midwest", "code": "MW", "country": "USA", "population": 68_000_000, "avg_income": 65000, "climate_zone": "humid_continental"},
    {"name": "Southwest", "code": "SW", "country": "USA", "population": 42_000_000, "avg_income": 68000, "climate_zone": "arid"},
    {"name": "West Coast", "code": "WC", "country": "USA", "population": 53_000_000, "avg_income": 85000, "climate_zone": "mediterranean"},
]

STORES_PER_REGION = 3

CATEGORIES = [
    {"name": "Dairy", "margin_target": 0.32},
    {"name": "Produce", "margin_target": 0.38},
    {"name": "Bakery", "margin_target": 0.55},
    {"name": "Meat & Seafood", "margin_target": 0.30},
    {"name": "Grocery", "margin_target": 0.26},
    {"name": "Frozen", "margin_target": 0.28},
    {"name": "Beverages", "margin_target": 0.34},
    {"name": "Snacks", "margin_target": 0.42},
]

PRODUCTS = [
    ("Organic Whole Milk 1 Gallon", "Dairy", 3.20, 5.99, 8.6),
    ("Skim Milk 1 Gallon", "Dairy", 2.80, 4.99, 8.6),
    ("Greek Yogurt Plain 32oz", "Dairy", 2.10, 4.49, 2.0),
    ("Free-Range Eggs Dozen", "Dairy", 3.40, 6.99, 0.7),
    ("Cheddar Block Sharp 8oz", "Dairy", 2.90, 5.49, 0.5),

    ("Avocado Hass Premium", "Produce", 1.20, 2.49, 0.2),
    ("Organic Baby Spinach 5oz", "Produce", 1.50, 3.99, 0.3),
    ("Blueberries 6oz Pint", "Produce", 2.30, 4.99, 0.3),
    ("Bananas Organic per lb", "Produce", 0.50, 0.99, 1.0),
    ("Tomatoes Roma per lb", "Produce", 0.90, 1.99, 1.0),
    ("Orange Juice Pulp Free 52oz", "Produce", 2.80, 5.49, 3.5),

    ("Sourdough Artisan Loaf", "Bakery", 2.60, 7.99, 1.2),
    ("Whole Wheat Bread Sliced", "Bakery", 1.80, 4.49, 1.4),
    ("Croissant Butter Each", "Bakery", 0.90, 2.99, 0.1),
    ("Blueberry Muffin 4pk", "Bakery", 1.70, 4.99, 0.8),
    ("Bagels Plain Half Dozen", "Bakery", 1.20, 3.99, 0.7),

    ("Chicken Breast Boneless 1lb", "Meat & Seafood", 4.20, 7.99, 1.0),
    ("Ground Beef 80/20 1lb", "Meat & Seafood", 3.80, 6.49, 1.0),
    ("Grass Fed Beef 1lb", "Meat & Seafood", 7.50, 12.99, 1.0),
    ("Fresh Atlantic Salmon 1lb", "Meat & Seafood", 9.80, 17.99, 1.0),
    ("Shrimp 21-25ct Frozen 1lb", "Meat & Seafood", 7.50, 14.99, 1.0),
    ("Pork Chops Bone-In 1lb", "Meat & Seafood", 3.00, 5.99, 1.0),

    ("Pasta Marinara Sauce 24oz", "Grocery", 1.30, 3.49, 1.5),
    ("Peanut Butter Crunchy 18oz", "Grocery", 1.90, 4.79, 1.1),
    ("Olive Oil Extra Virgin 16oz", "Grocery", 4.80, 9.99, 1.0),
    ("Canned Tuna in Water 5oz", "Grocery", 0.70, 1.79, 0.3),
    ("White Rice Long Grain 5lb", "Grocery", 3.10, 6.99, 5.0),
    ("Pasta Spaghetti 16oz", "Grocery", 0.80, 1.99, 1.0),
    ("Black Beans Canned 15oz", "Grocery", 0.55, 1.29, 0.9),
    ("Sugary Cereal Family Size", "Grocery", 2.30, 5.49, 1.5),

    ("Frozen Pizza Margherita", "Frozen", 3.10, 6.49, 1.0),
    ("Frozen Mixed Vegetables 16oz", "Frozen", 0.90, 2.29, 1.0),
    ("Ice Cream Vanilla 1.5qt", "Frozen", 2.80, 5.99, 1.4),
    ("Frozen Fries Crinkle Cut 28oz", "Frozen", 1.60, 3.99, 1.8),

    ("Almond Milk Unsweetened 64oz", "Beverages", 2.20, 4.49, 4.0),
    ("Cola Soda 12pk 12oz", "Beverages", 3.00, 6.99, 9.5),
    ("Bottled Water 24pk 16oz", "Beverages", 2.10, 4.99, 26.4),
    ("Craft Beer IPA 6pk 12oz", "Beverages", 6.80, 11.99, 4.3),

    ("Potato Chips Plain 8oz", "Snacks", 1.40, 3.99, 0.5),
    ("Tortilla Chips 10oz", "Snacks", 1.10, 3.49, 0.6),
    ("Chocolate Chip Cookies 12oz", "Snacks", 2.00, 4.79, 0.8),
    ("Protein Bar Variety 12pk", "Snacks", 11.00, 24.99, 2.5),
    ("Mixed Nuts Premium 16oz", "Snacks", 5.80, 12.99, 1.0),
]

PROMOTION_TYPES = [
    {"name": "Summer Kickoff Sale", "type": "PERCENT_OFF", "discount_pct": 20, "start_off": -80, "duration": 14, "budget": 12000},
    {"name": "4th of July Special", "type": "FLASH_SALE", "discount_pct": 25, "start_off": -50, "duration": 3, "budget": 8000},
    {"name": "Back to School Bundle", "type": "BUNDLE", "discount_pct": 15, "start_off": -30, "duration": 21, "budget": 10000},
    {"name": "Flash Sale #3", "type": "FLASH_SALE", "discount_pct": 25, "start_off": -10, "duration": 3, "budget": 15000},
    {"name": "Labor Day Weekend", "type": "PERCENT_OFF", "discount_pct": 18, "start_off": -3, "duration": 4, "budget": 9000},
    {"name": "Fall Harvest Promotion", "type": "BOGO", "discount_pct": 50, "start_off": 5, "duration": 10, "budget": 13000},
]

COMPETITORS = [
    {"name": "MegaMart", "market_share": 28.5, "website": "megamart.example.com", "is_online": True, "regions_present": "Northeast,Southeast,Midwest,Southwest,West Coast"},
    {"name": "FreshPlus", "market_share": 14.2, "website": "freshplus.example.com", "is_online": False, "regions_present": "Northeast,West Coast"},
    {"name": "BudgetGrocer", "market_share": 18.7, "website": "budgetgrocer.example.com", "is_online": True, "regions_present": "Southeast,Midwest,Southwest"},
    {"name": "OrganicHub", "market_share": 6.8, "website": "organichub.example.com", "is_online": True, "regions_present": "West Coast,Northeast"},
]


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate():
    print("🚀 Starting MerchIq sample data generation...")
    db = SessionLocal()

    try:
        # ---------- REGIONS ----------
        print("  → Regions...", end=" ")
        region_objs = []
        for r in REGIONS:
            region = models.Region(**r)
            db.add(region)
            region_objs.append(region)
        db.flush()
        print(f"{len(region_objs)} regions")

        # ---------- STORES ----------
        print("  → Stores...", end=" ")
        store_objs = []
        for region in region_objs:
            for s in range(STORES_PER_REGION):
                store = models.Store(
                    name=f"{region.name} Store #{s+1}",
                    store_code=f"{region.code}-{1000+s}",
                    region_id=region.id,
                    address=f"{random.randint(100,9999)} Main St",
                    city={"Northeast":"Boston","Southeast":"Atlanta","Midwest":"Chicago","Southwest":"Phoenix","West Coast":"Seattle"}[region.name],
                    state={"Northeast":"MA","Southeast":"GA","Midwest":"IL","Southwest":"AZ","West Coast":"WA"}[region.name],
                    zip_code=f"{random.randint(10000,99999)}",
                    size_sqft=round(random.uniform(12000, 45000), -2),
                    opening_date=datetime(2018 + s, 1 + s, 15).date(),
                    is_active=True,
                )
                db.add(store)
                store_objs.append(store)
        db.flush()
        print(f"{len(store_objs)} stores")

        # ---------- CATEGORIES ----------
        print("  → Categories...", end=" ")
        cat_objs = {}
        for c in CATEGORIES:
            cat = models.Category(**c)
            db.add(cat)
            cat_objs[c["name"]] = cat
        db.flush()
        print(f"{len(cat_objs)} categories")

        # ---------- PRODUCTS ----------
        print("  → Products...", end=" ")
        product_objs = {}
        for idx, (name, cat, cost, base, weight) in enumerate(PRODUCTS):
            p = models.Product(
                sku=f"SKU-{10000 + idx}",
                name=name,
                description=f"Premium {name} — high-quality, sourced from trusted suppliers.",
                category_id=cat_objs[cat].id,
                brand=random.choice(["MerchIq Select", "Organic Farms Co.", "Artisan Kitchen", "Value Basics", "Premium Harvest"]),
                unit="unit",
                cost_price=cost,
                base_price=base,
                weight_kg=weight,
                is_active=True,
            )
            db.add(p)
            product_objs[name] = p
        db.flush()
        print(f"{len(product_objs)} products")

        # ---------- PROMOTIONS ----------
        print("  → Promotions...", end=" ")
        promo_objs = []
        today = datetime.utcnow().date()
        for promo in PROMOTION_TYPES:
            start = today + timedelta(days=promo["start_off"])
            end = start + timedelta(days=promo["duration"])
            p = models.Promotion(
                name=promo["name"],
                description=f"{promo['name']} — limited time {promo['type']}.",
                promotion_type=promo["type"],
                start_date=start,
                end_date=end,
                discount_percent=promo["discount_pct"],
                discount_amount=0.0,
                min_quantity=1,
                max_discount=50.0,
                budget=promo["budget"],
                is_active=True,
            )
            db.add(p)
            promo_objs.append(p)
        db.flush()
        # attach products
        for promo in promo_objs:
            promo_products = random.sample(list(product_objs.values()), k=random.randint(8, 20))
            for p in promo_products:
                db.add(models.PromotionProduct(promotion_id=promo.id, product_id=p.id))
        print(f"{len(promo_objs)} promotions")

        # ---------- INVENTORY ----------
        print("  → Inventory records...", end=" ")
        inv_count = 0
        for store in store_objs:
            for p in product_objs.values():
                base_demand = 5 + random.random() * 40
                on_hand = int(max(0, random.gauss(base_demand * 5, base_demand * 2)))
                inv = models.Inventory(
                    product_id=p.id,
                    store_id=store.id,
                    quantity_on_hand=on_hand,
                    quantity_reserved=int(on_hand * random.uniform(0, 0.08)),
                    quantity_on_order=int(base_demand * random.uniform(0, 1.5)) if on_hand < base_demand * 2 else 0,
                    reorder_point=int(max(5, base_demand * random.uniform(0.6, 1.2))),
                    reorder_quantity=int(base_demand * random.uniform(3, 8)),
                    lead_time_days=random.randint(2, 14),
                    last_restock_date=datetime.utcnow() - timedelta(days=random.randint(0, 18)),
                    expiry_date=(datetime.utcnow() + timedelta(days=random.randint(14, 90))).date() if p.category_id == cat_objs["Dairy"].id or p.category_id == cat_objs["Produce"].id or p.category_id == cat_objs["Bakery"].id or p.category_id == cat_objs["Meat & Seafood"].id else None,
                )
                db.add(inv)
                inv_count += 1
        db.flush()
        print(f"{inv_count} inventory records")

        # ---------- SALES ----------
        print("  → Sales history (180 days)...", end=" ")
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=180)
        sales_count = 0
        all_products = list(product_objs.values())
        all_stores = store_objs
        region_map = {s.id: s.region_id for s in all_stores}

        active_promo_ranges = []
        for promo in promo_objs:
            active_promo_ranges.append((promo.id, promo.start_date, promo.end_date, promo.discount_percent,
                                        [pp.product_id for pp in db.query(models.PromotionProduct).filter(models.PromotionProduct.promotion_id == promo.id).all()]))

        transaction_counter = 1
        # Sample one txn per store per day with ~5-15 line items each (use batch approach for speed)
        sale_bulk = []
        current = start_date
        while current <= today:
            day_of_week = current.weekday()
            day_factor = 1.0
            if day_of_week >= 5:
                day_factor = 1.35
            if current.month == 12 and current.day > 18:
                day_factor = 1.5

            for store in all_stores:
                region_factor = 1.0 + (hash(store.id) % 30 - 15) / 100
                weather_factor = 1.0
                if random.random() < 0.12:
                    weather_factor = 0.7 + random.random() * 0.2

                num_txns = int(random.randint(25, 80) * day_factor * region_factor * weather_factor)
                for _ in range(num_txns):
                    txn_id = f"TXN-{transaction_counter:08d}"
                    transaction_counter += 1
                    num_items = random.randint(1, 10)
                    chosen_products = random.sample(all_products, k=min(num_items, len(all_products)))
                    for p in chosen_products:
                        base_qty = 1
                        if random.random() < 0.15:
                            base_qty = random.randint(2, 4)

                        unit_price = p.base_price
                        discount_amount = 0.0
                        promo_id = None
                        for (pid, ps, pe, pdisc, p_products) in active_promo_ranges:
                            if ps <= current <= pe and p.id in p_products:
                                promo_id = pid
                                discount_amount = unit_price * (pdisc / 100)
                                unit_price = unit_price - discount_amount
                                break

                        qty = base_qty
                        total = unit_price * qty
                        cost = p.cost_price * qty

                        sale_bulk.append(dict(
                            sale_date=current,
                            product_id=p.id,
                            store_id=store.id,
                            region_id=region_map[store.id],
                            quantity_sold=qty,
                            unit_price=round(unit_price, 2),
                            discount_amount=round(discount_amount * qty, 2),
                            total_amount=round(total, 2),
                            cost_amount=round(cost, 2),
                            promotion_id=promo_id,
                            transaction_id=txn_id,
                        ))
                        sales_count += 1

            # commit in chunks
            if len(sale_bulk) >= 5000:
                db.bulk_insert_mappings(models.Sale, sale_bulk)
                sale_bulk = []
                db.flush()
            current += timedelta(days=1)

        if sale_bulk:
            db.bulk_insert_mappings(models.Sale, sale_bulk)
            db.flush()
        print(f"{sales_count} sale records")

        # ---------- PRICE HISTORY ----------
        print("  → Price history...", end=" ")
        ph_count = 0
        for p in product_objs.values():
            base = p.base_price
            changes = random.randint(2, 5)
            current_price = base
            start_p = start_date
            for _ in range(changes):
                days = random.randint(25, 60)
                end_p = min(today, start_p + timedelta(days=days))
                delta_pct = random.uniform(-0.08, 0.08)
                new_price = round(current_price * (1 + delta_pct), 2)
                if new_price < p.cost_price * 1.1:
                    new_price = round(p.cost_price * 1.15, 2)
                db.add(models.PriceHistory(
                    product_id=p.id, price=new_price, price_type="retail",
                    effective_date=start_p, end_date=end_p,
                    reason=random.choice(["Seasonal", "Cost adjustment", "Promotion repricing", "Competitive matching", "Category review"]),
                ))
                ph_count += 1
                current_price = new_price
                start_p = end_p + timedelta(days=1)
                if start_p > today:
                    break
        print(f"{ph_count} price history records")

        # ---------- WEATHER ----------
        print("  → Weather data (180 days per region)...", end=" ")
        w_count = 0
        base_climate = {
            "humid_subtropical": {"temp_avg": 20, "temp_range": 15, "precip": 3.5, "snow": 0.5},
            "humid_continental": {"temp_avg": 12, "temp_range": 25, "precip": 2.8, "snow": 8},
            "arid": {"temp_avg": 24, "temp_range": 18, "precip": 0.4, "snow": 0.1},
            "mediterranean": {"temp_avg": 18, "temp_range": 12, "precip": 0.8, "snow": 0.2},
        }
        for region in region_objs:
            climate = base_climate[region.climate_zone]
            d = start_date
            while d <= today:
                yday = d.timetuple().tm_yday
                seasonality = np.sin(2 * np.pi * (yday - 80) / 365) * (climate["temp_range"] / 2)
                t_avg = climate["temp_avg"] + seasonality + random.gauss(0, 2.5)
                t_min = t_avg - random.uniform(2, 6)
                t_max = t_avg + random.uniform(3, 8)
                precip = max(0, climate["precip"] * random.weibullvariate(1, 0.8))
                snow = max(0, climate["snow"] * random.random() if t_avg < 3 else 0)
                w_type = "Sunny"
                if precip > 5:
                    w_type = "Heavy Rain"
                elif precip > 1:
                    w_type = "Rain"
                elif snow > 2:
                    w_type = "Snow"
                elif t_max > 32:
                    w_type = "Hot"
                elif t_min < -5:
                    w_type = "Cold"
                elif precip > 0:
                    w_type = "Drizzle"

                db.add(models.Weather(
                    record_date=d,
                    region_id=region.id,
                    temperature_avg=round(t_avg, 1),
                    temperature_min=round(t_min, 1),
                    temperature_max=round(t_max, 1),
                    precipitation_mm=round(precip, 1),
                    snowfall_cm=round(snow, 1),
                    humidity=round(random.uniform(35, 90), 1),
                    wind_speed_kmh=round(random.uniform(2, 35), 1),
                    weather_type=w_type,
                ))
                w_count += 1
                d += timedelta(days=1)
        print(f"{w_count} weather records")

        # ---------- COMPETITORS & PRICES ----------
        print("  → Competitors & prices...", end=" ")
        comp_objs = []
        for c in COMPETITORS:
            co = models.Competitor(**c)
            db.add(co)
            comp_objs.append(co)
        db.flush()

        cp_count = 0
        sample_p = random.sample(list(product_objs.values()), k=25)
        for p in sample_p:
            d = start_date
            while d <= today:
                if random.random() < 0.15 or d == start_date:
                    for co in comp_objs:
                        comp_price = round(p.base_price * random.uniform(0.85, 1.15), 2)
                        db.add(models.CompetitorPrice(
                            product_id=p.id, competitor_id=co.id,
                            price=comp_price, record_date=d,
                            in_stock=random.random() < 0.9,
                            shipping_cost=round(random.uniform(0, 4.99), 2),
                        ))
                        cp_count += 1
                d += timedelta(days=14)
        print(f"{len(comp_objs)} competitors, {cp_count} price records")

        db.commit()
        print("\n✅ Sample data generation complete!")
        print(f"\nSummary:")
        print(f"  Regions:        {len(region_objs)}")
        print(f"  Stores:         {len(store_objs)}")
        print(f"  Categories:     {len(cat_objs)}")
        print(f"  Products:       {len(product_objs)}")
        print(f"  Promotions:     {len(promo_objs)}")
        print(f"  Inventory:      {inv_count}")
        print(f"  Sales:          {sales_count}")
        print(f"  Price History:  {ph_count}")
        print(f"  Weather:        {w_count}")
        print(f"  Competitors:    {len(comp_objs)}")
        print(f"  Comp. Prices:   {cp_count}")
        print("\n🚀 Platform ready! Start backend: `cd backend && uvicorn app.main:app --reload`")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate()
