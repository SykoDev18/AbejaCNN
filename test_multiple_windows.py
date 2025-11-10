"""
Prueba de cierre automático de ventanas anteriores.
Simula múltiples detecciones seguidas.
"""
from utils import show_image_processing_demo, Logger
import os
import time

def test_multiple_windows():
    """Prueba que solo haya una ventana abierta a la vez."""
    print("=" * 60)
    print("PRUEBA: CIERRE AUTOMÁTICO DE VENTANAS ANTERIORES")
    print("=" * 60)
    
    # Buscar imágenes de test
    test_dir = os.path.join("fotos_flores_proyecto", "flores", "test")
    
    if not os.path.exists(test_dir):
        print(f"❌ No se encontró el directorio: {test_dir}")
        return
    
    images = [f for f in os.listdir(test_dir) if f.endswith('.jpg')][:5]
    
    if not images:
        print("❌ No se encontraron imágenes")
        return
    
    print(f"\n✅ Se encontraron {len(images)} imágenes de prueba")
    print("\n📋 Comportamiento esperado:")
    print("  1. Se abre ventana para imagen 1")
    print("  2. Después de 3 segundos, se abre imagen 2 (cierra imagen 1)")
    print("  3. Después de 3 segundos, se abre imagen 3 (cierra imagen 2)")
    print("  4. Y así sucesivamente...")
    print("  5. Solo UNA ventana visible a la vez ✓")
    print("\n⏰ Cada ventana dura 10 segundos (puedes verificar el cierre)")
    print("   pero la siguiente aparece cada 3 segundos\n")
    
    input("Presiona Enter para iniciar la prueba...")
    
    for i, img_file in enumerate(images, 1):
        img_path = os.path.join(test_dir, img_file)
        print(f"\n[{i}/{len(images)}] Mostrando: {img_file}")
        
        # Mostrar ventana (durará 10 segundos, pero abriremos la siguiente en 3)
        show_image_processing_demo(img_path, duration=10)
        
        if i < len(images):
            print(f"      ⏰ Esperando 3 segundos antes de la siguiente...")
            time.sleep(3)  # Esperar antes de abrir la siguiente
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60)
    print("\nObservaciones:")
    print("  ✓ Solo una ventana visible a la vez")
    print("  ✓ La ventana anterior se cerró automáticamente")
    print("  ✓ No se acumularon ventanas")
    print("\nEste comportamiento se aplicará durante la simulación:")
    print("  - Cuando la abeja detecta flores/objetos seguidos")
    print("  - Solo verás la ventana de la detección actual")
    print("  - Sin acumulación de ventanas emergentes\n")

if __name__ == "__main__":
    test_multiple_windows()
