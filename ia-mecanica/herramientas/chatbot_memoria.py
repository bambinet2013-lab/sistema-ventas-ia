#!/usr/bin/env python3
"""
🤖 CHATBOT CON MEMORIA Y CONTEXTO
Recuerda conversaciones anteriores y aprende de ellas
Sistema similar a los que usan empresas Fortune 500
"""

import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import os

class ChatbotMemoria:
    def __init__(self):
        self.memoria_file = "memoria_chatbot.json"
        self.contexto_actual = []
        self.conocimiento = self.cargar_memoria()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.vectores_entrenados = False
        
    def cargar_memoria(self):
        try:
            with open(self.memoria_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "conversaciones": [],
                "preguntas_frecuentes": {},
                "contextos": {},
                "estadisticas": {
                    "total_interacciones": 0,
                    "usuarios_unicos": 0
                }
            }
    
    def guardar_memoria(self):
        with open(self.memoria_file, 'w') as f:
            json.dump(self.conocimiento, f, indent=2)
    
    def recordar_conversacion(self, usuario_id, mensaje, respuesta):
        """Guarda una interacción en la memoria"""
        self.conocimiento["conversaciones"].append({
            "usuario": usuario_id,
            "fecha": datetime.now().isoformat(),
            "mensaje": mensaje,
            "respuesta": respuesta
        })
        
        # Mantener solo últimas 1000 conversaciones
        if len(self.conocimiento["conversaciones"]) > 1000:
            self.conocimiento["conversaciones"] = self.conocimiento["conversaciones"][-1000:]
        
        self.guardar_memoria()
    
    def buscar_respuesta_similar(self, mensaje):
        """Busca respuestas a preguntas similares en el pasado"""
        if len(self.conocimiento["conversaciones"]) < 5:
            return None
        
        # Preparar textos para comparación
        textos = []
        respuestas = []
        for conv in self.conocimiento["conversaciones"][-50:]:  # Últimas 50
            textos.append(conv["mensaje"])
            respuestas.append(conv["respuesta"])
        
        # Vectorizar
        vectores = self.vectorizer.fit_transform(textos + [mensaje])
        vector_mensaje = vectores[-1]
        vectores_historicos = vectores[:-1]
        
        # Calcular similitudes
        similitudes = cosine_similarity(vector_mensaje, vectores_historicos)[0]
        
        # Encontrar la más similar
        max_sim = np.max(similitudes)
        if max_sim > 0.6:  # Umbral de similitud
            idx = np.argmax(similitudes)
            return {
                "respuesta": respuestas[idx],
                "confianza": float(max_sim),
                "original": textos[idx]
            }
        return None
    
    def aprender_pregunta_frecuente(self, pregunta, respuesta):
        """Aprende una pregunta frecuente para respuestas rápidas"""
        # Normalizar pregunta
        pregunta_norm = pregunta.lower().strip()
        
        if pregunta_norm not in self.conocimiento["preguntas_frecuentes"]:
            self.conocimiento["preguntas_frecuentes"][pregunta_norm] = {
                "respuesta": respuesta,
                "veces_preguntada": 1,
                "ultima_vez": datetime.now().isoformat()
            }
        else:
            self.conocimiento["preguntas_frecuentes"][pregunta_norm]["veces_preguntada"] += 1
            self.conocimiento["preguntas_frecuentes"][pregunta_norm]["ultima_vez"] = datetime.now().isoformat()
        
        self.guardar_memoria()
    
    def responder(self, usuario_id, mensaje):
        """Función principal para responder mensajes"""
        print(f"\n🧠 Procesando: '{mensaje}'")
        
        # Buscar en preguntas frecuentes
        pregunta_norm = mensaje.lower().strip()
        if pregunta_norm in self.conocimiento["preguntas_frecuentes"]:
            data = self.conocimiento["preguntas_frecuentes"][pregunta_norm]
            respuesta = f"[RECORDADO] {data['respuesta']}"
            print(f"📚 Respuesta de FAQ (veces usada: {data['veces_preguntada']})")
            self.recordar_conversacion(usuario_id, mensaje, respuesta)
            return respuesta
        
        # Buscar conversación similar
        similar = self.buscar_respuesta_similar(mensaje)
        if similar:
            respuesta = f"[SIMILAR - {similar['confianza']:.0%} coincidencia] {similar['respuesta']}"
            print(f"🔄 Respuesta basada en conversación similar ({similar['confianza']:.0%})")
            self.recordar_conversacion(usuario_id, mensaje, respuesta)
            return respuesta
        
        # Respuesta por defecto (aquí conectarías con tu agente real)
        respuesta = f"Procesando consulta: {mensaje} (conectando con agente...)"
        print("💬 Nueva consulta - sin referencias previas")
        
        # Aprender para futuro
        self.aprender_pregunta_frecuente(mensaje, respuesta)
        self.recordar_conversacion(usuario_id, mensaje, respuesta)
        
        return respuesta
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de uso y aprendizaje"""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DEL CHATBOT CON MEMORIA")
        print("="*60)
        
        print(f"\n📝 Total de conversaciones: {len(self.conocimiento['conversaciones'])}")
        print(f"📚 Preguntas frecuentes aprendidas: {len(self.conocimiento['preguntas_frecuentes'])}")
        
        if self.conocimiento['preguntas_frecuentes']:
            print("\n🔥 Preguntas más frecuentes:")
            top_preguntas = sorted(
                self.conocimiento['preguntas_frecuentes'].items(),
                key=lambda x: x[1]['veces_preguntada'],
                reverse=True
            )[:5]
            
            for pregunta, data in top_preguntas:
                print(f"   • '{pregunta[:50]}...' - {data['veces_preguntada']} veces")

def main():
    chatbot = ChatbotMemoria()
    
    print("🤖 CHATBOT CON MEMORIA Y CONTEXTO")
    print("="*60)
    print("Comandos: /stats, /salir")
    print("="*60)
    
    usuario = "junior"
    
    while True:
        mensaje = input("\nTú: ").strip()
        
        if mensaje.lower() == '/salir':
            break
        elif mensaje.lower() == '/stats':
            chatbot.mostrar_estadisticas()
            continue
        
        respuesta = chatbot.responder(usuario, mensaje)
        print(f"Bot: {respuesta}")

if __name__ == "__main__":
    main()
