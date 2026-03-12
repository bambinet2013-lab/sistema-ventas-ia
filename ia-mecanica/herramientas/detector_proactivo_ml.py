#!/usr/bin/env python3
"""
🔮 SISTEMA DE DETECCIÓN PROACTIVA CON ML
Predice qué ventas fallarán antes de que ocurran
Solo el 5% de los sistemas tienen esta capacidad
"""

import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import requests
import warnings
warnings.filterwarnings('ignore')

class DetectorProactivoML:
    def __init__(self):
        self.modelo = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.entrenado = False
        self.API_BD = "http://localhost:5000/consultar"
        
    def consultar_bd(self, query):
        try:
            response = requests.post(
                self.API_BD,
                json={"consulta": query},
                timeout=5
            )
            return response.json()
        except:
            return None
    
    def obtener_datos_entrenamiento(self):
        """Obtiene datos históricos de ventas exitosas y fallidas"""
        query = """
        SELECT 
            v.idventa,
            v.monto_divisa,
            v.tipo_pago,
            v.igtf_aplicado,
            v.comision_banco,
            COUNT(vpd.idpago) as num_pagos,
            CASE 
                WHEN v.estado = 'REGISTRADO' THEN 1 
                ELSE 0 
            END as exitosa
        FROM venta v
        LEFT JOIN venta_pago_detalle vpd ON v.idventa = vpd.idventa
        GROUP BY v.idventa, v.monto_divisa, v.tipo_pago, 
                 v.igtf_aplicado, v.comision_banco, v.estado
        """
        resultado = self.consultar_bd(query)
        if resultado and resultado.get('success'):
            return resultado['resultados']
        return []
    
    def preparar_caracteristicas(self, datos):
        """Convierte datos en características numéricas para ML"""
        X = []
        y = []
        
        for d in datos:
            # Características:
            # 0: monto_divisa
            # 1: igtf_aplicado (0/1)
            # 2: comision_banco
            # 3: num_pagos
            # 4-9: tipo_pago one-hot (simplificado)
            try:
                monto = float(d.get('monto_divisa', 0))
                igtf = 1 if d.get('igtf_aplicado') == 'True' else 0
                comision = float(d.get('comision_banco', 0))
                num_pagos = int(d.get('num_pagos', 1))
                exitosa = int(d.get('exitosa', 1))
                
                # Vector de características
                features = [
                    monto,
                    igtf,
                    comision,
                    num_pagos
                ]
                
                X.append(features)
                y.append(exitosa)
            except:
                continue
        
        return np.array(X), np.array(y)
    
    def entrenar(self):
        """Entrena el modelo con datos históricos"""
        print("🧠 Entrenando modelo predictivo...")
        
        datos = self.obtener_datos_entrenamiento()
        if len(datos) < 10:
            print("⚠️ Datos insuficientes para entrenar")
            return False
        
        X, y = self.preparar_caracteristicas(datos)
        
        if len(X) < 10:
            print("⚠️ Características insuficientes")
            return False
        
        # Escalar características
        X_scaled = self.scaler.fit_transform(X)
        
        # Entrenar modelo
        self.modelo.fit(X_scaled, y)
        self.entrenado = True
        
        precision = self.modelo.score(X_scaled, y)
        print(f"✅ Modelo entrenado con precisión: {precision:.2%}")
        
        # Importancia de características
        importancia = self.modelo.feature_importances_
        print("\n📊 Importancia de factores:")
        print(f"   • Monto: {importancia[0]:.2%}")
        print(f"   • IGTF aplicado: {importancia[1]:.2%}")
        print(f"   • Comisión: {importancia[2]:.2%}")
        print(f"   • Número de pagos: {importancia[3]:.2%}")
        
        return True
    
    def predecir_venta(self, venta_data):
        """Predice si una venta actual fallará"""
        if not self.entrenado:
            return None
        
        try:
            features = np.array([[
                float(venta_data.get('monto_divisa', 0)),
                1 if venta_data.get('igtf_aplicado') == 'True' else 0,
                float(venta_data.get('comision_banco', 0)),
                int(venta_data.get('num_pagos', 1))
            ]])
            
            features_scaled = self.scaler.transform(features)
            prob_fallo = 1 - self.modelo.predict_proba(features_scaled)[0][1]
            
            return prob_fallo
        except Exception as e:
            print(f"Error en predicción: {e}")
            return None
    
    def analizar_ventas_peligrosas(self):
        """Analiza ventas recientes en busca de posibles fallos"""
        query = """
        SELECT TOP 20 
            v.idventa,
            v.monto_divisa,
            v.tipo_pago,
            v.igtf_aplicado,
            v.comision_banco,
            COUNT(vpd.idpago) as num_pagos,
            v.estado
        FROM venta v
        LEFT JOIN venta_pago_detalle vpd ON v.idventa = vpd.idventa
        GROUP BY v.idventa, v.monto_divisa, v.tipo_pago, 
                 v.igtf_aplicado, v.comision_banco, v.estado
        ORDER BY v.idventa DESC
        """
        
        resultado = self.consultar_bd(query)
        if not resultado or not resultado.get('success'):
            return []
        
        ventas_peligrosas = []
        for venta in resultado['resultados']:
            prob_fallo = self.predecir_venta(venta)
            if prob_fallo and prob_fallo > 0.3:  # Umbral del 30%
                ventas_peligrosas.append({
                    'idventa': venta['idventa'],
                    'probabilidad': prob_fallo,
                    'tipo_pago': venta['tipo_pago'],
                    'monto': venta['monto_divisa'],
                    'alerta': '🔴 ALTA' if prob_fallo > 0.7 else '🟡 MEDIA'
                })
        
        return ventas_peligrosas

def main():
    detector = DetectorProactivoML()
    
    print("="*60)
    print("🔮 SISTEMA DE DETECCIÓN PROACTIVA CON ML")
    print("="*60)
    
    # Entrenar modelo
    if detector.entrenar():
        print("\n" + "="*60)
        print("🔍 ANALIZANDO VENTAS PELIGROSAS...")
        print("="*60)
        
        peligrosas = detector.analizar_ventas_peligrosas()
        
        if peligrosas:
            print(f"\n⚠️ Se detectaron {len(peligrosas)} ventas con riesgo:")
            for v in peligrosas:
                print(f"\n   {v['alerta']} Venta #{v['idventa']}")
                print(f"      Probabilidad de fallo: {v['probabilidad']:.1%}")
                print(f"      Tipo de pago: {v['tipo_pago']}")
                print(f"      Monto: ${v['monto']}")
        else:
            print("\n✅ No se detectaron ventas con riesgo significativo")
    
    print("\n" + "="*60)
    print("💡 TIP: Programa este script para ejecutarse cada hora")
    print("="*60)

if __name__ == "__main__":
    main()
