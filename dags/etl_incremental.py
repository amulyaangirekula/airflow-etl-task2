import psycopg2
import psycopg2.extras


def run_incremental_etl():

    conn = psycopg2.connect(
        host='host.docker.internal',
        port=5432,
        dbname='postgres',
        user='postgres',
        password='amulya'
    )

    cursor = conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor
    )

    # ----------------------------
    # GET WATERMARK
    # ----------------------------

    cursor.execute("""
    SELECT MAX(order_date)
    FROM analytics_db.sales_summary
    """)

    watermark = cursor.fetchone()[0]

    print(f"Last loaded order date: {watermark}")

    # ----------------------------
    # EXTRACT ORDERS
    # ----------------------------

    cursor.execute("""
    SELECT *
    FROM orders_db.orders
    WHERE status = 'completed'
    AND order_date > %s
    """, (watermark,))

    orders = cursor.fetchall()

    # ----------------------------
    # EXTRACT PRODUCTS
    # ----------------------------

    cursor.execute("""
    SELECT *
    FROM products_db.products
    """)

    products = {
        row['product_id']: row
        for row in cursor.fetchall()
    }

    rows_skipped = 0

    # ----------------------------
    # TRANSFORM
    # ----------------------------

    transformed = []

    for order in orders:

        product = products.get(order['product_id'])

        if not product:
            rows_skipped += 1
            continue

        total_amount = (
            order['quantity']
            * product['unit_price']
        )

        order_month = (
            order['order_date']
            .strftime('%Y-%m')
        )

        transformed.append((
            order['order_id'],
            order['customer_name'],
            product['product_name'],
            product['category'],
            order['quantity'],
            product['unit_price'],
            total_amount,
            order['order_date'],
            order_month,
            order['status']
        ))

    # ----------------------------
    # LOAD
    # ----------------------------

    insert_query = """
    INSERT INTO analytics_db.sales_summary (
        order_id,
        customer_name,
        product_name,
        category,
        quantity,
        unit_price,
        total_amount,
        order_date,
        order_month,
        status
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (order_id) DO NOTHING
    """

    cursor.executemany(
        insert_query,
        transformed
    )

    print("\n===== ETL SUMMARY =====")
    print(f"Orders Extracted : {len(orders)}")
    print(f"Products Extracted : {len(products)}")
    print(f"Rows Skipped : {rows_skipped}")
    print(f"Rows Loaded : {len(transformed)}")

    # ----------------------------
    # REFRESH CUSTOMER TOTALS
    # ----------------------------

    cursor.execute("""
    DELETE FROM analytics_db.customer_totals
    """)

    cursor.execute("""
    INSERT INTO analytics_db.customer_totals
    SELECT
        customer_name,
        SUM(total_amount) AS total_spend,
        COUNT(*) AS order_count
    FROM analytics_db.sales_summary
    GROUP BY customer_name
    """)

    conn.commit()

    cursor.close()
    conn.close()

    print(
        f"Loaded {len(transformed)} records into analytics_db.sales_summary"
    )


if __name__ == "__main__":
    run_incremental_etl()