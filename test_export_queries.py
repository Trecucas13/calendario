#!/usr/bin/env python3
"""
Test script to verify the corrected export SQL queries work properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config import db
from sqlalchemy import text
import pandas as pd

def test_export_query():
    """Test the export query used in both CSV and Excel functions"""
    
    print("🔍 Testing export query...")
    
    try:
        # Test the corrected SQL query
        query = """
            SELECT DISTINCT
                r.id,
                r.tipo_id, 
                r.num_id, 
                r.primer_nombre, 
                r.segundo_nombre,
                r.primer_apellido,
                r.segundo_apellido,
                r.fecha,
                r.edad,
                r.estado_afiliacion,
                r.regimen_afiliacion,
                r.telefonos,
                r.direccion,
                r.municipio,
                r.subregion,
                r.proceso,
                -- Asegurar que cantidad_gestiones se incluya correctamente
                COALESCE(r.cantidad_gestiones, 0) as cantidad_gestiones,
                -- Datos de la gestión más reciente
                (
                    SELECT g.motivo 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as motivo,
                (
                    SELECT g.fecha_gestion 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as fecha_gestion,
                (
                    SELECT g.tipificacion 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as tipificacion,
                (
                    SELECT g.comentario 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as comentario,
                (
                    SELECT g.usuario 
                    FROM gestion g 
                    WHERE g.registro_id = r.id 
                    ORDER BY g.fecha_gestion DESC 
                    LIMIT 1
                ) as asesor
            FROM registro_base r
            ORDER BY r.id
            LIMIT 5
        """
        
        results = db.session.execute(text(query)).fetchall()
        
        print(f"✅ Query executed successfully!")
        print(f"📊 Found {len(results)} records (limited to 5 for testing)")
        
        if results:
            # Create DataFrame to test pandas processing
            columns = ['id', 'tipo_id', 'num_id', 'primer_nombre', 'segundo_nombre',
                      'primer_apellido', 'segundo_apellido', 'fecha', 'edad',
                      'estado_afiliacion', 'regimen_afiliacion', 'telefonos', 'direccion',
                      'municipio', 'subregion', 'proceso', 'cantidad_gestiones',
                      'motivo', 'fecha_gestion', 'tipificacion', 'comentario', 'asesor']
            
            df = pd.DataFrame(results, columns=columns)
            
            print(f"📋 DataFrame columns: {list(df.columns)}")
            print(f"🔢 cantidad_gestiones values: {df['cantidad_gestiones'].tolist()}")
            
            # Test dropping the id column
            df_export = df.drop('id', axis=1)
            print(f"📤 Export DataFrame columns (after dropping id): {list(df_export.columns)}")
            
            # Check for gestión data
            gestiones_count = df['motivo'].notna().sum()
            print(f"🎯 Records with gestión data: {gestiones_count}/{len(df)}")
            
            print("\n📋 Sample data (first record):")
            for col in df.columns:
                print(f"  {col}: {df.iloc[0][col]}")
                
        else:
            print("⚠️ No records found")
            
    except Exception as e:
        print(f"❌ Error testing query: {e}")
        import traceback
        traceback.print_exc()

def test_cantidad_gestiones_column():
    """Test if cantidad_gestiones column exists and has data"""
    
    print("\n🔍 Testing cantidad_gestiones column...")
    
    try:
        # Check if column exists
        column_check = db.session.execute(
            text("""SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'registro_base' 
                    AND column_name = 'cantidad_gestiones'
                )""")
        ).scalar()
        
        if column_check:
            print("✅ cantidad_gestiones column exists")
            
            # Get some statistics
            stats = db.session.execute(
                text("""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(cantidad_gestiones) as records_with_column,
                        SUM(COALESCE(cantidad_gestiones, 0)) as total_gestiones,
                        AVG(COALESCE(cantidad_gestiones, 0)) as avg_gestiones,
                        MAX(COALESCE(cantidad_gestiones, 0)) as max_gestiones
                    FROM registro_base
                """)
            ).fetchone()
            
            print(f"📊 Column statistics:")
            print(f"  Total records: {stats[0]}")
            print(f"  Records with column data: {stats[1]}")
            print(f"  Total gestiones: {stats[2]}")
            print(f"  Average gestiones per record: {stats[3]:.2f}")
            print(f"  Max gestiones for a record: {stats[4]}")
            
        else:
            print("❌ cantidad_gestiones column does NOT exist")
            print("💡 Run the setup_cantidad_gestiones.sql script first")
            
    except Exception as e:
        print(f"❌ Error testing cantidad_gestiones column: {e}")

if __name__ == "__main__":
    print("🧪 Testing export functionality...")
    
    # You would need to import your Flask app context here
    # For now, this is just the testing structure
    
    print("⚠️ Note: This script needs to be run within a Flask app context")
    print("💡 You can test the queries directly in your database management tool")
    
    # The actual tests would go here when run with proper Flask context:
    # test_cantidad_gestiones_column()
    # test_export_query()
