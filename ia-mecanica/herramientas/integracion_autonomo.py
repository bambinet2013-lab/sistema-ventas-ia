#!/usr/bin/env python3
"""
🔄 INTEGRACIÓN DEL AGENTE AUTÓNOMO CON EL SISTEMA MEGA
"""

import threading
import time
from agente_autonomo import AgenteAutonomo
import sistema_mega  # Tu sistema mega existente

class SistemaIntegrado:
    def __init__(self):
        print("🚀 INICIALIZANDO SISTEMA INTEGRADO + AGENTE AUTÓNOMO")
        
        # Inicializar ambos sistemas
        self.mega = sistema_mega.SistemaMega()
        self.agente = AgenteAutonomo("MegaBot")
        
        # Hilo para el sistema mega
        self.thread_mega = threading.Thread(target=self.mega.iniciar)
        self.thread_mega.daemon = True
        
        print("✅ Sistemas inicializados")
    
    def iniciar(self):
        # Iniciar mega en segundo plano
        self.thread_mega.start()
        
        # Modo interactivo con el agente
        print("\n🤖 MODO INTERACTIVO DEL AGENTE AUTÓNOMO")
        print("Comandos: /salir, /lista, /mega (ver dashboard)")
        
        while True:
            try:
                entrada = input("\n💬 Tú: ").strip()
                
                if entrada.lower() == '/salir':
                    break
                elif entrada.lower() == '/lista':
                    print(self.agente.listar_habilidades())
                elif entrada.lower() == '/mega':
                    self.mega.mostrar_dashboard()
                else:
                    respuesta = self.agente.procesar(entrada)
                    print(f"🤖 Agente: {respuesta}")
                    
            except KeyboardInterrupt:
                break
        
        print("\n👋 Sistemas detenidos")

if __name__ == "__main__":
    sistema = SistemaIntegrado()
    sistema.iniciar()
