"""
Prueba rápida de la funcionalidad de ventana emergente de procesamiento.
"""
from utils import show_image_processing_demo, Logger
import os

def test_popup():
    """Prueba la ventana emergente con una imagen de flor."""
    print("=" * 60)
    print("PRUEBA DE VENTANA EMERGENTE DE PROCESAMIENTO")
    print("=" * 60)
    
    # Buscar una imagen de flor
    test_dir = os.path.join("fotos_flores_proyecto", "flores", "test")
    
    if os.path.exists(test_dir):
        images = [f for f in os.listdir(test_dir) if f.endswith('.jpg')]
        if images:
            test_image = os.path.join(test_dir, images[0])
            print(f"\nUsando imagen de prueba: {test_image}")
            print("\n⏰ La ventana se cerrará automáticamente en 5 segundos...\n")
            
            show_image_processing_demo(test_image, duration=5)
            
            print("\n✅ Prueba completada!")
            print("Esta ventana aparecerá cada vez que la abeja detecte una flor u objeto.")
        else:
            print("❌ No se encontraron imágenes en el directorio de test")
    else:
        print(f"❌ No se encontró el directorio: {test_dir}")

if __name__ == "__main__":
    test_popup()
