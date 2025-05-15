from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
from mysql.connector import Error
from datetime import date

app = FastAPI()

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'gas_inventory_db'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

# Pydantic models for request/response validation
class SupplierCreate(BaseModel):
    supplier_name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

class SupplierResponse(SupplierCreate):
    supplier_id: int
    created_at: str
    updated_at: str

class CylinderTypeCreate(BaseModel):
    capacity_kg: float
    description: Optional[str] = None

class CylinderTypeResponse(CylinderTypeCreate):
    type_id: int
    created_at: str

class InventoryResponse(BaseModel):
    inventory_id: int
    supplier_id: int
    type_id: int
    empty_count: int
    full_count: int
    last_updated: str
    supplier_name: str
    capacity_kg: float

class RestockingCreate(BaseModel):
    supplier_id: int
    type_id: int
    quantity: int
    unit_price: float
    restock_date: date
    received_by: Optional[str] = None
    notes: Optional[str] = None

class RestockingResponse(RestockingCreate):
    restock_id: int
    total_cost: float
    created_at: str
    supplier_name: str
    capacity_kg: float

class SaleCreate(BaseModel):
    inventory_id: int
    quantity: int
    unit_price: float
    sale_date: date
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    sold_by: Optional[str] = None
    notes: Optional[str] = None

class SaleResponse(SaleCreate):
    sale_id: int
    total_amount: float
    created_at: str
    supplier_name: str
    capacity_kg: float

# CRUD operations for Suppliers
@app.post("/suppliers/", response_model=SupplierResponse)
def create_supplier(supplier: SupplierCreate, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    query = """
    INSERT INTO suppliers (supplier_name, contact_person, phone, email, address)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        supplier.supplier_name,
        supplier.contact_person,
        supplier.phone,
        supplier.email,
        supplier.address
    )
    
    try:
        cursor.execute(query, values)
        db.commit()
        supplier_id = cursor.lastrowid
        cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        new_supplier = cursor.fetchone()
        return new_supplier
    except Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating supplier: {e}")
    finally:
        cursor.close()

@app.get("/suppliers/", response_model=List[SupplierResponse])
def read_suppliers(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM suppliers")
        suppliers = cursor.fetchall()
        return suppliers
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error fetching suppliers: {e}")
    finally:
        cursor.close()

@app.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def read_supplier(supplier_id: int, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        supplier = cursor.fetchone()
        if supplier is None:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return supplier
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error fetching supplier: {e}")
    finally:
        cursor.close()

@app.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int, 
    supplier: SupplierCreate, 
    db: mysql.connector.MySQLConnection = Depends(get_db_connection)
):
    cursor = db.cursor(dictionary=True)
    query = """
    UPDATE suppliers 
    SET supplier_name = %s, contact_person = %s, phone = %s, email = %s, address = %s
    WHERE supplier_id = %s
    """
    values = (
        supplier.supplier_name,
        supplier.contact_person,
        supplier.phone,
        supplier.email,
        supplier.address,
        supplier_id
    )
    
    try:
        cursor.execute(query, values)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Supplier not found")
        db.commit()
        cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        updated_supplier = cursor.fetchone()
        return updated_supplier
    except Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating supplier: {e}")
    finally:
        cursor.close()

@app.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Supplier not found")
        db.commit()
        return {"message": "Supplier deleted successfully"}
    except Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting supplier: {e}")
    finally:
        cursor.close()

# CRUD operations for Cylinder Types
@app.post("/cylinder-types/", response_model=CylinderTypeResponse)
def create_cylinder_type(cylinder_type: CylinderTypeCreate, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    query = """
    INSERT INTO cylinder_types (capacity_kg, description)
    VALUES (%s, %s)
    """
    values = (
        cylinder_type.capacity_kg,
        cylinder_type.description
    )
    
    try:
        cursor.execute(query, values)
        db.commit()
        type_id = cursor.lastrowid
        cursor.execute("SELECT * FROM cylinder_types WHERE type_id = %s", (type_id,))
        new_type = cursor.fetchone()
        return new_type
    except Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating cylinder type: {e}")
    finally:
        cursor.close()

@app.get("/cylinder-types/", response_model=List[CylinderTypeResponse])
def read_cylinder_types(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM cylinder_types")
        types = cursor.fetchall()
        return types
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error fetching cylinder types: {e}")
    finally:
        cursor.close()

# CRUD operations for Inventory
@app.get("/inventory/", response_model=List[InventoryResponse])
def read_inventory(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        SELECT i.*, s.supplier_name, ct.capacity_kg 
        FROM inventory i
        JOIN suppliers s ON i.supplier_id = s.supplier_id
        JOIN cylinder_types ct ON i.type_id = ct.type_id
        """
        cursor.execute(query)
        inventory = cursor.fetchall()
        return inventory
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error fetching inventory: {e}")
    finally:
        cursor.close()

@app.put("/inventory/{inventory_id}/transfer")
def transfer_cylinders(
    inventory_id: int, 
    from_status: str,  # 'empty' or 'full'
    to_status: str,    # 'empty' or 'full'
    quantity: int,
    db: mysql.connector.MySQLConnection = Depends(get_db_connection)
):
    if from_status not in ['empty', 'full'] or to_status not in ['empty', 'full']:
        raise HTTPException(status_code=400, detail="Status must be 'empty' or 'full'")
    
    if from_status == to_status:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same status")
    
    cursor = db.cursor(dictionary=True)
    try:
        # Check current counts
        cursor.execute("SELECT * FROM inventory WHERE inventory_id = %s FOR UPDATE", (inventory_id,))
        inventory = cursor.fetchone()
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory record not found")
        
        # Verify we have enough to transfer
        from_count = inventory[f"{from_status}_count"]
        if from_count < quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough {from_status} cylinders (available: {from_count}, requested: {quantity})"
            )
        
        # Update counts
        update_query = f"""
        UPDATE inventory 
        SET {from_status}_count = {from_status}_count - %s,
            {to_status}_count = {to_status}_count + %s
        WHERE inventory_id = %s
        """
        cursor.execute(update_query, (quantity, quantity, inventory_id))
        db.commit()
        
        # Return updated inventory
        cursor.execute("SELECT * FROM inventory WHERE inventory_id = %s", (inventory_id,))
        updated_inventory = cursor.fetchone()
        return updated_inventory
    except Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error transferring cylinders: {e}")
    finally:
        cursor.close()

# CRUD operations for Restocking
@app.post("/restocking/", response_model=RestockingResponse)
def create_restocking(restocking: RestockingCreate, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        # Start transaction
        db.start_transaction()
        
        # 1. Add restocking record
        query = """
        INSERT INTO restocking 
        (supplier_id, type_id, quantity, unit_price, restock_date, received_by, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            restocking.supplier_id,
            restocking.type_id,
            restocking.quantity,
            restocking.unit_price,
            restocking.restock_date,
            restocking.received_by,
            restocking.notes
        )
        cursor.execute(query, values)
        restock_id = cursor.lastrowid
        
        # 2. Update inventory (add to full_count)
        # First check if inventory record exists
        cursor.execute("""
        SELECT inventory_id FROM inventory 
        WHERE supplier_id = %s AND type_id = %s
        """, (restocking.supplier_id, restocking.type_id))
        inventory = cursor.fetchone()
        
        if inventory:
            # Update existing inventory
            cursor.execute("""
            UPDATE inventory 
            SET full_count = full_count + %s
            WHERE supplier_id = %s AND type_id = %s
            """, (restocking.quantity, restocking.supplier_id, restocking.type_id))
        else:
            # Create new inventory record
            cursor.execute("""
            INSERT INTO inventory (supplier_id, type_id, empty_count, full_count)
            VALUES (%s, %s, 0, %s)
            """, (restocking.supplier_id, restocking.type_id, restocking.quantity))
        
        # Commit transaction
        db.commit()
        
        # Return the created restocking record with joined data
        cursor.execute("""
        SELECT r.*, s.supplier_name, ct.capacity_kg 
        FROM restocking r
        JOIN suppliers s ON r.supplier_id = s.supplier_id
        JOIN cylinder_types ct ON r.type_id = ct.type_id
        WHERE r.restock_id = %s
        """, (restock_id,))
        new_restocking = cursor.fetchone()
        return new_restocking
    except Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing restocking: {e}")
    finally:
        cursor.close()

@app.get("/restocking/", response_model=List[RestockingResponse])
def read_restockings(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        SELECT r.*, s.supplier_name, ct.capacity_kg 
        FROM restocking r
        JOIN suppliers s ON r.supplier_id = s.supplier_id
        JOIN cylinder_types ct ON r.type_id = ct.type_id
        ORDER BY r.restock_date DESC
        """
        cursor.execute(query)
        restockings = cursor.fetchall()
        return restockings
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error fetching restockings: {e}")
    finally:
        cursor.close()

# CRUD operations for Sales
@app.post("/sales/", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        # Start transaction
        db.start_transaction()
        
        # 1. Verify inventory has enough full cylinders
        cursor.execute("""
        SELECT i.*, s.supplier_name, ct.capacity_kg 
        FROM inventory i
        JOIN suppliers s ON i.supplier_id = s.supplier_id
        JOIN cylinder_types ct ON i.type_id = ct.type_id
        WHERE i.inventory_id = %s FOR UPDATE
        """, (sale.inventory_id,))
        inventory = cursor.fetchone()
        
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory record not found")
        
        if inventory['full_count'] < sale.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough full cylinders (available: {inventory['full_count']}, requested: {sale.quantity})"
            )
        
        # 2. Add sale record
        query = """
        INSERT INTO sales 
        (inventory_id, quantity, unit_price, sale_date, customer_name, customer_phone, sold_by, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            sale.inventory_id,
            sale.quantity,
            sale.unit_price,
            sale.sale_date,
            sale.customer_name,
            sale.customer_phone,
            sale.sold_by,
            sale.notes
        )
        cursor.execute(query, values)
        sale_id = cursor.lastrowid
        
        # 3. Update inventory (remove from full_count, add to empty_count)
        cursor.execute("""
        UPDATE inventory 
        SET full_count = full_count - %s,
            empty_count = empty_count + %s
        WHERE inventory_id = %s
        """, (sale.quantity, sale.quantity, sale.inventory_id))
        
        # Commit transaction
        db.commit()
        
        # Return the created sale record with joined data
        cursor.execute("""
        SELECT s.*, sup.supplier_name, ct.capacity_kg 
        FROM sales s
        JOIN inventory i ON s.inventory_id = i.inventory_id
        JOIN suppliers sup ON i.supplier_id = sup.supplier_id
        JOIN cylinder_types ct ON i.type_id = ct.type_id
        WHERE s.sale_id = %s
        """, (sale_id,))
        new_sale = cursor.fetchone()
        return new_sale
    except Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing sale: {e}")
    finally:
        cursor.close()

@app.get("/sales/", response_model=List[SaleResponse])
def read_sales(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        SELECT s.*, sup.supplier_name, ct.capacity_kg 
        FROM sales s
        JOIN inventory i ON s.inventory_id = i.inventory_id
        JOIN suppliers sup ON i.supplier_id = sup.supplier_id
        JOIN cylinder_types ct ON i.type_id = ct.type_id
        ORDER BY s.sale_date DESC
        """
        cursor.execute(query)
        sales = cursor.fetchall()
        return sales
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error fetching sales: {e}")
    finally:
        cursor.close()

@app.get("/inventory/summary")
def get_inventory_summary(db: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    try:
        # Summary by supplier and cylinder type
        query = """
        SELECT 
            s.supplier_name,
            ct.capacity_kg,
            SUM(i.empty_count) AS total_empty,
            SUM(i.full_count) AS total_full,
            SUM(i.empty_count + i.full_count) AS total_cylinders
        FROM inventory i
        JOIN suppliers s ON i.supplier_id = s.supplier_id
        JOIN cylinder_types ct ON i.type_id = ct.type_id
        GROUP BY s.supplier_name, ct.capacity_kg
        ORDER BY s.supplier_name, ct.capacity_kg
        """
        cursor.execute(query)
        summary = cursor.fetchall()
        
        # Total summary
        cursor.execute("""
        SELECT 
            SUM(empty_count) AS grand_total_empty,
            SUM(full_count) AS grand_total_full,
            SUM(empty_count + full_count) AS grand_total_cylinders
        FROM inventory
        """)
        totals = cursor.fetchone()
        
        return {
            "summary_by_type": summary,
            "totals": totals
        }
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error fetching inventory summary: {e}")
    finally:
        cursor.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)