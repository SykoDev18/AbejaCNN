"""
Utilidades generales para el proyecto.
Incluye funciones de procesamiento de imágenes, logging y helpers.
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os
import random
from datetime import datetime


class ImageProcessor:
    """Clase para procesamiento avanzado de imágenes con técnicas de ecualización y mejora."""
    
    @staticmethod
    def equalize_histogram_global(image):
        """
        Ecualización global de histograma.
        Mejora el contraste general de la imagen.
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if len(image.shape) == 3:  # Color image
            # Convertir a espacio de color YCrCb
            ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
            # Ecualizar solo el canal Y (luminancia)
            ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
            # Convertir de vuelta a RGB
            equalized = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
        else:  # Grayscale
            equalized = cv2.equalizeHist(image)
        
        return Image.fromarray(equalized)
    
    @staticmethod
    def equalize_histogram_adaptive(image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Ecualización adaptativa de histograma (CLAHE).
        Mejora el contraste local, especialmente útil para imágenes subexpuestas.
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if len(image.shape) == 3:  # Color image
            # Convertir a LAB para aplicar CLAHE en el canal L
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            equalized = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        else:  # Grayscale
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            equalized = clahe.apply(image)
        
        return Image.fromarray(equalized)
    
    @staticmethod
    def apply_gaussian_blur(image, kernel_size=5):
        """Aplica suavizado Gaussiano."""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        return Image.fromarray(blurred)
    
    @staticmethod
    def apply_median_blur(image, kernel_size=5):
        """Aplica suavizado de mediana (útil para eliminar ruido de sal y pimienta)."""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        blurred = cv2.medianBlur(image, kernel_size)
        return Image.fromarray(blurred)
    
    @staticmethod
    def apply_average_blur(image, kernel_size=5):
        """Aplica suavizado promedio."""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        blurred = cv2.blur(image, (kernel_size, kernel_size))
        return Image.fromarray(blurred)
    
    @staticmethod
    def enhance_contrast(image, factor=1.5):
        """Mejora el contraste usando PIL."""
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def enhance_brightness(image, factor=1.2):
        """Ajusta el brillo de la imagen."""
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def sharpen_image(image):
        """Aplica nitidez a la imagen."""
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        return image.filter(ImageFilter.SHARPEN)
    
    @staticmethod
    def resize_image(image, size=(224, 224), method=Image.LANCZOS):
        """
        Redimensiona imagen usando interpolación de alta calidad.
        method puede ser: Image.NEAREST, Image.BILINEAR, Image.BICUBIC, Image.LANCZOS
        """
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        return image.resize(size, method)
    
    @staticmethod
    def create_underexposed(image, factor=0.5):
        """Crea una versión subexpuesta de la imagen."""
        return ImageProcessor.enhance_brightness(image, factor)
    
    @staticmethod
    def create_overexposed(image, factor=1.5):
        """Crea una versión sobreexpuesta de la imagen."""
        return ImageProcessor.enhance_brightness(image, factor)
    
    @staticmethod
    def calculate_metrics(image):
        """
        Calcula métricas de calidad de imagen:
        - Contraste (desviación estándar)
        - Entropía (medida de información)
        - Brillo promedio
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convertir a escala de grises si es necesario
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Contraste (desviación estándar)
        contrast = np.std(gray)
        
        # Entropía
        histogram = cv2.calcHist([gray], [0], None, [256], [0, 256])
        histogram = histogram.ravel() / histogram.sum()
        entropy = -np.sum(histogram * np.log2(histogram + 1e-7))
        
        # Brillo promedio
        brightness = np.mean(gray)
        
        return {
            'contrast': contrast,
            'entropy': entropy,
            'brightness': brightness
        }
    
    @staticmethod
    def preprocess_for_model(image, apply_augmentation=True):
        """
        Pipeline completo de preprocesamiento para el modelo Transformer.
        Incluye ecualización, mejora de contraste y redimensionamiento.
        """
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        processed_images = []
        
        # Imagen original redimensionada
        img_resized = ImageProcessor.resize_image(image, size=(224, 224))
        processed_images.append(img_resized)
        
        if apply_augmentation:
            # Versión con ecualización global
            img_eq_global = ImageProcessor.equalize_histogram_global(image)
            img_eq_global = ImageProcessor.resize_image(img_eq_global, size=(224, 224))
            processed_images.append(img_eq_global)
            
            # Versión con ecualización adaptativa (CLAHE)
            img_eq_adaptive = ImageProcessor.equalize_histogram_adaptive(image)
            img_eq_adaptive = ImageProcessor.resize_image(img_eq_adaptive, size=(224, 224))
            processed_images.append(img_eq_adaptive)
            
            # Versión con contraste mejorado
            img_contrast = ImageProcessor.enhance_contrast(image, factor=1.5)
            img_contrast = ImageProcessor.resize_image(img_contrast, size=(224, 224))
            processed_images.append(img_contrast)
        
        return processed_images


class Logger:
    """Sistema de logging para el proyecto."""
    
    @staticmethod
    def log(message, level="INFO"):
        """Registra un mensaje con timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    @staticmethod
    def log_metrics(metrics, filename="metrics_results.txt"):
        """Guarda métricas en un archivo."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Timestamp: {timestamp}\n")
            for key, value in metrics.items():
                f.write(f"{key}: {value}\n")
            f.write(f"{'='*60}\n")


def load_random_object_sprite(objects_dir):
    """Carga un sprite de objeto aleatorio desde la carpeta objectos."""
    try:
        object_files = [f for f in os.listdir(objects_dir) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if object_files:
            random_object = random.choice(object_files)
            return os.path.join(objects_dir, random_object)
        return None
    except Exception as e:
        Logger.log(f"Error cargando sprite de objeto: {e}", "ERROR")
        return None


def load_random_flower_photo(flowers_dir):
    """Carga una foto de flor real aleatoria desde fotos_flores_proyecto."""
    try:
        flower_files = [f for f in os.listdir(flowers_dir) 
                       if f.lower().endswith('.png') and 'flor' in f.lower()]
        if flower_files:
            random_flower = random.choice(flower_files)
            return os.path.join(flowers_dir, random_flower)
        return None
    except Exception as e:
        Logger.log(f"Error cargando foto de flor: {e}", "ERROR")
        return None


def load_random_flower_test_image(test_dir):
    """Selecciona una imagen de flor aleatoria desde el conjunto de prueba."""
    try:
        flower_files = [
            f for f in os.listdir(test_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
        if flower_files:
            random_flower = random.choice(flower_files)
            return os.path.join(test_dir, random_flower)
        return None
    except Exception as e:
        Logger.log(f"Error cargando imagen de flor de prueba: {e}", "ERROR")
        return None


def load_random_object_image(objects_dir):
    """Selecciona una imagen de objeto aleatoria desde la carpeta de objetos."""
    try:
        object_files = [
            f for f in os.listdir(objects_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
        if object_files:
            random_object = random.choice(object_files)
            return os.path.join(objects_dir, random_object)
        return None
    except Exception as e:
        Logger.log(f"Error cargando imagen de objeto: {e}", "ERROR")
        return None


def manhattan_distance(pos1, pos2):
    """Calcula la distancia Manhattan entre dos posiciones."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def euclidean_distance(pos1, pos2):
    """Calcula la distancia Euclidiana entre dos posiciones."""
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def get_neighbors(position, grid_size):
    """
    Obtiene los vecinos válidos de una posición en la cuadrícula.
    Retorna lista de tuplas (x, y) vecinas.
    """
    x, y = position
    neighbors = []
    
    # Arriba, Derecha, Abajo, Izquierda
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            neighbors.append((nx, ny))
    
    return neighbors


# Variable global para mantener referencia a la última ventana abierta
_last_processing_window = None


def show_image_processing_demo(image_path, duration=5):
    """
    Muestra una ventana emergente con las técnicas de procesamiento aplicadas.
    Se cierra automáticamente después del tiempo especificado.
    Cierra la ventana anterior si existe.
    
    Args:
        image_path: Ruta a la imagen a procesar
        duration: Tiempo en segundos antes de cerrar (default: 5)
    """
    import matplotlib
    matplotlib.use('TkAgg')  # Backend para ventanas no bloqueantes
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import threading
    
    global _last_processing_window
    
    try:
        # Cerrar la ventana anterior si existe
        if _last_processing_window is not None:
            try:
                plt.close(_last_processing_window)
                Logger.log("Ventana anterior cerrada")
            except:
                pass
        
        # Cargar imagen original
        original_image = Image.open(image_path)
        if original_image.mode == 'P' and 'transparency' in original_image.info:
            original_image = original_image.convert('RGBA')
        if original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
        
        # Aplicar técnicas de procesamiento
        techniques = {
            'Original': original_image,
            'Ecualización\nGlobal': ImageProcessor.equalize_histogram_global(original_image),
            'CLAHE\n(Adaptativa)': ImageProcessor.equalize_histogram_adaptive(original_image),
            'Contraste\nMejorado': ImageProcessor.enhance_contrast(original_image, factor=1.5),
            'Subexpuesta': ImageProcessor.create_underexposed(original_image, factor=0.6),
            'Sobreexpuesta': ImageProcessor.create_overexposed(original_image, factor=1.4),
        }
        
        # Crear figura
        fig, axes = plt.subplots(2, 3, figsize=(12, 7))
        fig.canvas.manager.set_window_title('🔬 Procesamiento de Imagen Detectada')
        fig.suptitle('🔬 Técnicas de Procesamiento Aplicadas en Tiempo Real', 
                     fontsize=14, fontweight='bold')
        
        axes = axes.ravel()
        
        # Mostrar imágenes
        for idx, (name, img) in enumerate(techniques.items()):
            axes[idx].imshow(img)
            axes[idx].set_title(name, fontsize=10, fontweight='bold')
            axes[idx].axis('off')
            
            # Agregar métricas
            metrics = ImageProcessor.calculate_metrics(img)
            text = f"Contraste: {metrics['contrast']:.1f}\n"
            text += f"Entropía: {metrics['entropy']:.1f}\n"
            text += f"Brillo: {metrics['brightness']:.1f}"
            
            axes[idx].text(0.02, 0.98, text, 
                    transform=axes[idx].transAxes,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                    fontsize=8)
        
        # Agregar contador de tiempo
        filename = os.path.basename(image_path)
        fig.text(0.5, 0.02, f'📸 Imagen: {filename} | ⏰ Se cerrará en {duration} segundos', 
                ha='center', fontsize=10, style='italic', 
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        
        # Guardar referencia a esta ventana
        _last_processing_window = fig
        
        # Cerrar automáticamente después del tiempo especificado
        def close_window():
            import time
            time.sleep(duration)
            try:
                plt.close(fig)
                global _last_processing_window
                if _last_processing_window == fig:
                    _last_processing_window = None
            except:
                pass
        
        # Iniciar timer en thread separado
        timer_thread = threading.Thread(target=close_window, daemon=True)
        timer_thread.start()
        
        # Mostrar ventana (no bloqueante)
        plt.show(block=False)
        plt.pause(0.1)  # Pequeña pausa para que se renderice
        
        Logger.log(f"🔬 Ventana de procesamiento mostrada por {duration} segundos")
        
    except Exception as e:
        Logger.log(f"Error mostrando demo de procesamiento: {e}", "ERROR")
        import traceback
        traceback.print_exc()
