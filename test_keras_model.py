"""
Script de prueba para verificar que el modelo Keras se carga correctamente.
"""
import os
from flower_classifier import FlowerClassifier
from utils import Logger

def test_keras_model():
    """Prueba el clasificador con el modelo Keras."""
    Logger.log("=" * 60)
    Logger.log("Probando FlowerClassifier con modelo Keras (.h5)")
    Logger.log("=" * 60)
    
    # Crear clasificador
    classifier = FlowerClassifier()
    
    # Intentar cargar modelo
    Logger.log("\n1. Cargando modelo...")
    success = classifier.load_model()
    
    if success:
        Logger.log("✓ Modelo cargado exitosamente", "SUCCESS")
    else:
        Logger.log("⚠ Modelo no encontrado o error al cargar", "WARNING")
    
    # Verificar estructura del modelo
    if classifier.model is not None:
        Logger.log("\n2. Información del modelo:")
        Logger.log(f"   - Tipo: {type(classifier.model)}")
        Logger.log(f"   - Ruta: {classifier.model_path}")
        
        try:
            classifier.model.summary()
        except:
            Logger.log("   - No se pudo mostrar el resumen del modelo")
    
    # Probar predicción con una imagen de prueba
    Logger.log("\n3. Probando predicción...")
    test_images = [
        'fotos_flores_proyecto/flor 1.png',
        'fotos_flores_proyecto/flor 2.png',
        'objectos/gato.jpg',
        'objectos/perro.png'
    ]
    
    for img_path in test_images:
        full_path = os.path.join(os.path.dirname(__file__), img_path)
        if os.path.exists(full_path):
            try:
                label, confidence = classifier.predict(full_path)
                Logger.log(f"   - {img_path}: {label} ({confidence*100:.2f}%)")
            except Exception as e:
                Logger.log(f"   - Error con {img_path}: {e}", "ERROR")
        else:
            Logger.log(f"   - No encontrada: {img_path}", "WARNING")
    
    Logger.log("\n" + "=" * 60)
    Logger.log("Prueba completada")
    Logger.log("=" * 60)

if __name__ == "__main__":
    test_keras_model()
