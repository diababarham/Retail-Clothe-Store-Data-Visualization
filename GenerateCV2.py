from __future__ import annotations
from datetime import date, timedelta
import argparse
import random
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import zipfile

logging.basicConfig(level=logging.INFO, format="%(message)s")


def generate_dataset(
    out_dir: Path,
    sales_rows_count: int = 100_000,
    customers_count: int = 10_000,
    products_count: int = 1_000,
    seed: int = 42,
) -> Path:
    random.seed(seed)
    np.random.seed(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # 1. dimDate
    # -----------------------------
    start_date = date(2024, 1, 1)
    end_date = date(2026, 3, 30)

    dates = []
    current = start_date
    while current <= end_date:
        dates.append({
            "DateKey": int(current.strftime("%Y%m%d")),
            "theDate": current.isoformat(),
            "Day": current.day,
            "Month": current.month,
            "Quarter": (current.month - 1) // 3 + 1,
            "Year": current.year,
        })
        current += timedelta(days=1)

    dimDate = pd.DataFrame(dates)
    dimDate["theDate"] = pd.to_datetime(dimDate["theDate"])

    # -----------------------------
    # 2. dimStore
    # -----------------------------
    stores = []
    dubai = ["Dubai Mall", "Mall of Emirates", "City Centre Mirdif", "Dubai Hills Mall", 
             "Festival City", "Ibn Battuta", "Dubai Marina Mall", "Mercato Mall", "Outlet Village"]
    abudhabi = ["Yas Mall", "Marina Mall", "Abu Dhabi Mall", "Al Wahda Mall", "Dalma Mall", "Galleria Al Maryah"]
    others = [("Sharjah", "City Centre Sharjah"), ("Sharjah", "Sahara Centre"), ("Ajman", "City Centre Ajman"),
              ("Ras Al Khaimah", "RAK Mall"), ("Fujairah", "Fujairah City Centre")]

    store_id = 1
    for name in dubai:
        stores.append([store_id, f"H&M {name}", "Dubai", "UAE", "Dubai", random.choice(["Mall", "Outlet", "Standalone"]), "2018-01-01"])
        store_id += 1
    for name in abudhabi:
        stores.append([store_id, f"H&M {name}", "Abu Dhabi", "UAE", "Abu Dhabi", random.choice(["Mall", "Outlet", "Standalone"]), "2019-01-01"])
        store_id += 1
    for city, name in others:
        stores.append([store_id, f"H&M {name}", city, "UAE", city, random.choice(["Mall", "Outlet", "Standalone"]), "2020-01-01"])
        store_id += 1

    dimStore = pd.DataFrame(stores, columns=["storeID", "storeName", "City", "Country", "Region", "storeType", "openingDate"])
    dimStore = dimStore.astype({"storeID": "int32", "storeName": "string", "City": "category", "Country": "category",
                               "Region": "category", "storeType": "category", "openingDate": "string"})

    # -----------------------------
    # 3. dimProduct
    # -----------------------------
    categories = {
        "Men": ["T-Shirt", "Jeans", "Hoodie", "Jacket", "Shirt"],
        "Women": ["Dress", "Top", "Jeans", "Skirt", "Blazer"],
        "Kids": ["Kids Tee", "Kids Jeans", "Kids Hoodie", "Kids Jacket"],
        "Accessories": ["Cap", "Bag", "Scarf", "Belt"],
    }
    colors = ["Black", "White", "Blue", "Red", "Green", "Beige", "Grey"]
    sizes = ["XS", "S", "M", "L", "XL"]
    seasons = ["Summer", "Winter", "Spring", "Autumn"]

    products = []
    for pid in range(1, products_count + 1):
        category = random.choices(["Men", "Women", "Kids", "Accessories"], weights=[30, 40, 20, 10])[0]
        sub = random.choice(categories[category])
        products.append([
            pid, f"{category} {sub} {pid}", category, sub, "H&M",
            random.choice(seasons), random.choice(colors), random.choice(sizes),
            category if category != "Accessories" else "Unisex", random.randint(1, 50)
        ])

    dimProduct = pd.DataFrame(products, columns=["productID", "productName", "Category", "subCategory", "Brand",
                                                 "Season", "Color", "Size", "Gender", "supplierId"])
    dimProduct = dimProduct.astype({"productID": "int32", "productName": "string", "Category": "category",
                                    "subCategory": "category", "Brand": "category", "Season": "category",
                                    "Color": "category", "Size": "category", "Gender": "category", "supplierId": "int32"})

    price_map = {  # Used for realistic pricing
        "T-Shirt": (40, 120), "Jeans": (120, 300), "Hoodie": (100, 250), "Jacket": (200, 600),
        "Shirt": (80, 220), "Dress": (120, 450), "Top": (50, 180), "Skirt": (80, 220),
        "Blazer": (180, 500), "Kids Tee": (30, 90), "Kids Jeans": (60, 150),
        "Kids Hoodie": (80, 180), "Kids Jacket": (120, 250), "Cap": (30, 80),
        "Bag": (80, 300), "Scarf": (40, 120), "Belt": (40, 150),
    }

    # -----------------------------
    # 4. dimCustomer
    # -----------------------------
    first_names = ["Ahmed", "Sara", "Ali", "Noor", "Omar", "Layla", "Fatima", "John", "Emma", "Mia"]
    last_names = ["Khan", "Ali", "Smith", "Johnson", "Hassan", "Brown", "Wilson", "Taylor", "Clark", "Davis"]
    cities = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Fujairah", "RAK"]

    customers = []
    for cid in range(1, customers_count + 1):
        customers.append([
            cid, random.choice(first_names), random.choice(last_names),
            random.choice(["Male", "Female"]),
            random.choices(["18-25", "26-35", "36-50", "50+"], weights=[35, 40, 20, 5])[0],
            "UAE", random.choice(cities),
            random.choices(["Bronze", "Silver", "Gold"], weights=[60, 30, 10])[0]
        ])

    dimCustomer = pd.DataFrame(customers, columns=["customerID", "FirstName", "LastName", "Gender",
                                                   "AgeGroup", "Country", "City", "LoyaltyTier"])
    dimCustomer = dimCustomer.astype({"customerID": "int32", "FirstName": "string", "LastName": "string",
                                      "Gender": "category", "AgeGroup": "category", "Country": "category",
                                      "City": "category", "LoyaltyTier": "category"})

    # -----------------------------
    # 5. factSales
    # -----------------------------
    payment_methods = ["Cash", "Card"]
    channels = ["Store", "Online"]
    date_keys = dimDate["DateKey"].tolist()
    store_ids = dimStore["storeID"].tolist()

    sales_rows = []
    for sid in range(1, sales_rows_count + 1):
        product = dimProduct.sample(1).iloc[0]
        sub = product["subCategory"]
        low, high = price_map.get(sub, (50, 200))

        unit_price = round(random.uniform(low, high), 2)
        cost_price = round(unit_price * random.uniform(0.45, 0.65), 2)
        qty = random.randint(1, 5)
        gross = qty * unit_price
        discount = round(gross * random.uniform(0, 0.25), 2)

        sales_rows.append([
            sid, random.choice(date_keys), random.choice(store_ids), int(product["productID"]),
            random.randint(1, max(1, customers_count)), qty, unit_price, discount, cost_price,
            random.choice(payment_methods), random.choice(channels)
        ])

    factSales = pd.DataFrame(sales_rows, columns=[
        "salesId", "dateKey", "storeId", "productId", "CustomerId",
        "quantitySold", "unitPrice", "discAmount", "costPrice",
        "paymentMethod", "salesChannel"
    ])

    factSales["revenue"] = (factSales["quantitySold"] * factSales["unitPrice"] - factSales["discAmount"]).round(2)
    factSales["grossProfit"] = (factSales["revenue"] - factSales["quantitySold"] * factSales["costPrice"]).round(2)

    # -----------------------------
    # 6. factInventory 
    # -----------------------------
    inventory_rows = []
    current_date = start_date
    inv_id = 1

    while current_date <= end_date:
        product = dimProduct.sample(1).iloc[0]
        sub = product["subCategory"]
        low, high = price_map.get(sub, (50, 200))
        unit_cost = round(random.uniform(low * 0.45, high * 0.65), 2)

        opening = random.randint(20, 500)
        received = random.randint(0, 200)
        sold = random.randint(0, opening + received)
        returned = random.randint(0, 20)
        closing = opening + received - sold + returned

        inventory_rows.append([
            inv_id,
            int(current_date.strftime("%Y%m%d")),   # dateKey
            random.choice(store_ids),
            int(product["productID"]),
            opening, received, sold, returned, closing,
            random.randint(10, 50), unit_cost,
            round(closing * unit_cost, 2)
        ])
        inv_id += 1
        current_date += timedelta(days=1)

    factInventory = pd.DataFrame(inventory_rows, columns=[
        "invId", "dateKey", "storeId", "productId",
        "openingStock", "stockRecieved", "stockSold", "stockReturned",
        "closingStock", "reorderLevel", "unitCost", "InventoryValue"
    ])

    # -----------------------------
    # 7. factFinancials 
    # -----------------------------
    tmp = factSales.copy()
    tmp["cogs_calc"] = tmp["quantitySold"] * tmp["costPrice"]

    financial_base = tmp.groupby(["dateKey", "storeId"], as_index=False).agg(
        Revenue=("revenue", "sum"),
        COGS=("cogs_calc", "sum")
    ).round(2)

    financial_rows = []
    for idx, row in financial_base.iterrows():
        revenue = row["Revenue"]
        cogs = row["COGS"]

        op_exp = round(revenue * random.uniform(0.12, 0.22), 2)
        marketing = round(revenue * random.uniform(0.03, 0.08), 2)
        tax = round(revenue * random.uniform(0.03, 0.05), 2)

        financial_rows.append([
            idx + 1, int(row["dateKey"]), int(row["storeId"]),
            revenue, cogs, op_exp, marketing, tax
        ])

    factFinancials = pd.DataFrame(financial_rows, columns=[
        "FinancialId", "dateKey", "storeId", "Revenue", "COGS",
        "operatingExpenses", "marketingExpenses", "taxAmount"
    ])

    factFinancials["grossProfit"] = (factFinancials["Revenue"] - factFinancials["COGS"]).round(2)
    factFinancials["netProfit"] = (
        factFinancials["Revenue"] - factFinancials["COGS"] -
        factFinancials["operatingExpenses"] - factFinancials["marketingExpenses"] -
        factFinancials["taxAmount"]
    ).round(2)

    # -----------------------------
    # Export CSVs + ZIP
    # -----------------------------
    tables = {
        "dimDate.csv": dimDate,
        "dimStore.csv": dimStore,
        "dimProduct.csv": dimProduct,
        "dimCustomer.csv": dimCustomer,
        "factSales.csv": factSales,
        "factInventory.csv": factInventory,
        "factFinancials.csv": factFinancials,
    }

    for filename, df in tables.items():
        csv_path = out_dir / filename
        df.to_csv(str(csv_path), index=False)

    zip_path = out_dir / "hm_powerbi_dataset.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename in tables.keys():
            zf.write(out_dir / filename, arcname=filename)

    logging.info("Dataset generated successfully.")
    logging.info("ZIP file: %s", zip_path)
    logging.info("Table sizes:")
    for name, df in tables.items():
        logging.info(f"{name}: {len(df):,} rows")

    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic H&M dataset CSVs")
    parser.add_argument("--out", "-o", type=Path, default=Path("generated_dataset"), help="Output directory")
    parser.add_argument("--sales", type=int, default=100_000, help="Number of sales rows")
    parser.add_argument("--customers", type=int, default=10_000, help="Number of customers")
    parser.add_argument("--products", type=int, default=1_000, help="Number of products")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    generate_dataset(
        out_dir=args.out,
        sales_rows_count=args.sales,
        customers_count=args.customers,
        products_count=args.products,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()