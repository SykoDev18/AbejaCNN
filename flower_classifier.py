"""
Modelo de clasificación basado en Keras/TensorFlow.
Clasifica imágenes como 'flor' o 'objeto' (no-flor).
"""
import tensorflow as tf
from tensorflow import keras
from keras.utils import img_to_array
from PIL import Image
import os
import numpy as np
from config import *
from utils import ImageProcessor, Logger


class FlowerDataset:
    """Dataset personalizado para entrenamiento del clasificador con Keras."""
    
    def __init__(self, root_dir, apply_augmentation=True):
        """
        Args:
            root_dir: Directorio raíz con subcarpetas 'flores' y 'objetos'
            apply_augmentation: Si True, aplica aumento de datos con procesamiento de imágenes
        """
        self.root_dir = root_dir
        self.apply_augmentation = apply_augmentation
        self.samples = []
        self.classes = ['flower', 'object']
        self.class_to_idx = {'flower': 0, 'object': 1}
        
        # Cargar rutas de imágenes
        self._load_samples()
    
    def _load_samples(self):
        """Carga las rutas de todas las imágenes y sus etiquetas."""
        # Buscar carpetas de flores
        flower_folders = ['daisy', 'dandelion', 'rose', 'sunflower', 'tulip']
        
        # Cargar flores
        train_dir = self.root_dir
        for folder in flower_folders:
            folder_path = os.path.join(train_dir, folder)
            if os.path.exists(folder_path):
                for img_file in os.listdir(folder_path):
                    if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(folder_path, img_file)
                        self.samples.append((img_path, 0))  # 0 = flower
        
        Logger.log(f"Cargadas {len(self.samples)} flores del dataset")
    
    def __len__(self):
        return len(self.samples)
    
    def get_data(self):
        """Retorna los datos como arrays de numpy para Keras."""
        images = []
        labels = []
        
        for img_path, label in self.samples:
            try:
                image = Image.open(img_path).convert('RGB')
            except:
                # Crear imagen de respaldo si falla la carga
                image = Image.new('RGB', (224, 224), color=(128, 128, 128))
            
            # Aplicar aumento de datos con procesamiento avanzado
            if self.apply_augmentation:
                # Seleccionar aleatoriamente una técnica de procesamiento
                augmentation_type = np.random.randint(0, 5)
                
                if augmentation_type == 0:
                    # Original
                    pass
                elif augmentation_type == 1:
                    # Ecualización global
                    image = ImageProcessor.equalize_histogram_global(image)
                elif augmentation_type == 2:
                    # Ecualización adaptativa (CLAHE)
                    image = ImageProcessor.equalize_histogram_adaptive(image)
                elif augmentation_type == 3:
                    # Subexpuesta
                    image = ImageProcessor.create_underexposed(image, factor=0.6)
                elif augmentation_type == 4:
                    # Sobreexpuesta
                    image = ImageProcessor.create_overexposed(image, factor=1.4)
            
            # Redimensionar y convertir a array
            image = image.resize((IMAGE_SIZE, IMAGE_SIZE))
            img_array = img_to_array(image)
            images.append(img_array)
            labels.append(label)
        
        return np.array(images), np.array(labels)


class FlowerClassifier:
    """
    Clase wrapper para el clasificador de flores usando Keras/TensorFlow.
    Maneja carga de modelo y predicción.
    """
    
    def __init__(self, model_path=None):
        # Usar el modelo .h5 por defecto
        if model_path is None:
            model_path = os.path.join(MODELS_DIR, 'modelo_flores_rapido.h5')
        
        self.model_path = model_path
        self.model = None
        self.input_size = IMAGE_SIZE  # Por defecto usar config
        
        Logger.log(f"FlowerClassifier inicializado")
        Logger.log(f"Ruta del modelo: {self.model_path}")
    
    def _preprocess_image(self, image):
        """
        Preprocesa una imagen para predicción.
        
        Args:
            image: PIL Image
            
        Returns:
            Array de numpy normalizado
        """
        # Redimensionar al tamaño correcto del modelo
        image = image.resize((self.input_size, self.input_size))
        
        # Convertir a array
        img_array = img_to_array(image)
        
        # Normalizar (0-255 -> 0-1)
        img_array = img_array / 255.0
        
        # Expandir dimensiones para batch
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def train(self, train_dir=TRAIN_DIR, epochs=EPOCHS, batch_size=BATCH_SIZE):
        """
        Entrena el modelo clasificador.
        
        Args:
            train_dir: Directorio con datos de entrenamiento
            epochs: Número de épocas
            batch_size: Tamaño del batch
        """
        Logger.log(f"Iniciando entrenamiento por {epochs} épocas...")
        
        # Crear dataset
        dataset = FlowerDataset(train_dir, apply_augmentation=True)
        
        if len(dataset) == 0:
            Logger.log("Dataset vacío, no se puede entrenar", "ERROR")
            return
        
        # Obtener datos
        X, y = dataset.get_data()
        
        # Normalizar imágenes
        X = X / 255.0
        
        # Crear modelo si no existe
        if self.model is None:
            self.model = self._create_model()
        
        # Entrenar
        Logger.log(f"Entrenando con {len(X)} muestras...")
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        # Guardar modelo
        self.save_model()
        Logger.log("Entrenamiento completado")
    
    def _create_model(self):
        """Crea un modelo de clasificación con Keras."""
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(128, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Flatten(),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(NUM_CLASSES, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def load_model(self):
        """Carga un modelo preentrenado desde archivo .h5"""
        if not os.path.exists(self.model_path):
            Logger.log(f"No se encontró modelo en {self.model_path}", "WARNING")
            Logger.log("Creando modelo nuevo sin entrenar")
            self.model = self._create_model()
            return False
        
        try:
            self.model = keras.models.load_model(self.model_path)
            Logger.log(f"Modelo cargado desde {self.model_path}")
            
            # Detectar el tamaño de entrada del modelo cargado
            input_shape = self.model.input_shape
            if input_shape and len(input_shape) >= 2:
                self.input_size = input_shape[1]  # Obtener altura de la imagen
                Logger.log(f"Tamaño de entrada detectado: {self.input_size}x{self.input_size}")
            
            return True
        except Exception as e:
            Logger.log(f"Error cargando modelo: {e}", "ERROR")
            self.model = self._create_model()
            return False
    
    def save_model(self):
        """Guarda el modelo entrenado en formato .h5"""
        if self.model is None:
            Logger.log("No hay modelo para guardar", "WARNING")
            return
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        try:
            self.model.save(self.model_path)
            Logger.log(f"Modelo guardado en {self.model_path}")
        except Exception as e:
            Logger.log(f"Error guardando modelo: {e}", "ERROR")
    
    def predict(self, image):
        """
        Predice la clase de una imagen.
        
        Args:
            image: PIL Image o ruta a imagen
            
        Returns:
            Tupla (class_name, probability)
        """
        if self.model is None:
            self.load_model()
        
        # Cargar imagen si es una ruta
        if isinstance(image, str):
            try:
                image = Image.open(image).convert('RGB')
            except:
                Logger.log("Error cargando imagen para predicción", "ERROR")
                return "unknown", 0.0
        
        # Preprocesar
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        img_array = self._preprocess_image(image)
        
        # Predicción
        predictions = self.model.predict(img_array, verbose=0)
        
        # Determinar si el modelo tiene salida binaria (1 neurona) o multiclase (2+ neuronas)
        if predictions.shape[-1] == 1:
            # Modelo binario con sigmoid (0 = flor, > 0.5 = objeto)
            confidence = float(predictions[0][0])
            if confidence > 0.5:
                predicted_label = 'objeto'
                confidence = confidence  # Ya está normalizado
            else:
                predicted_label = 'flor'
                confidence = 1.0 - confidence  # Invertir para mostrar confianza en 'flor'
        else:
            # Modelo multiclase con softmax
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            class_names = ['flor', 'objeto']
            predicted_label = class_names[predicted_class]
        
        return predicted_label, confidence
    
    def evaluate(self, test_dir):
        """
        Evalúa el modelo en un conjunto de test.
        
        Args:
            test_dir: Directorio con datos de test
            
        Returns:
            Dict con métricas de evaluación
        """
        if self.model is None:
            self.load_model()
        
        dataset = FlowerDataset(test_dir, apply_augmentation=False)
        X, y = dataset.get_data()
        
        # Normalizar
        X = X / 255.0
        
        # Evaluar
        results = self.model.evaluate(X, y, verbose=0)
        loss, accuracy = results[0], results[1]
        
        Logger.log(f"Accuracy en test: {accuracy*100:.2f}%")
        
        return {
            'accuracy': accuracy * 100,
            'loss': loss,
            'total': len(y)
        }

