#!/usr/bin/env python3
"""
🤖 VERSIÓN INTERACTIVA DEL AGENTE AUTÓNOMO
Uso: python3 agente_interactivo.py
"""

from agente_autonomo import AgenteAutonomo

def main():
    print("="*60)
    print("🤖 AGENTE AUTÓNOMO INTERACTIVO")
    print("="*60)
    
    # Crear el agente
    agente = AgenteAutonomo("MegaBot")
    
    print("\nComandos especiales:")
    print("  /salir  - Terminar la sesión")
    print("  /lista  - Ver todas las habilidades")
    print("  /ayuda  - Mostrar este mensaje")
    print("-"*60)
    
    while True:
        try:
            entrada = input("\n💬 Tú: ").strip()
            
            if entrada.lower() == '/salir':
                print("👋 ¡Hasta luego!")
                break
            elif entrada.lower() == '/lista':
                print(agente.listar_habilidades())
                continue
            elif entrada.lower() == '/ayuda':
                print("\nComandos: /salir, /lista, /ayuda")
                print("Para crear una habilidad, escribe algo como:")
                print('  "crea una herramienta calculadora"')
                print('  "aprende a consultar el clima"')
                continue
            
            # Procesar la entrada
            respuesta = agente.procesar(entrada)
            print(f"🤖 Agente: {respuesta}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupción detectada. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
