import os
import random

class FaceGeneratorNode:
    @classmethod
    def INPUT_TYPES(cls):
        """
        Динамическое сканирование папки Wildcards при загрузке/обновлении ноды.
        """
        wildcards_dir = os.path.join(os.path.dirname(__file__), "Wildcards")
        os.makedirs(wildcards_dir, exist_ok=True)
        
        dynamic_inputs = {}
        
        if os.path.exists(wildcards_dir):
            for filename in sorted(os.listdir(wildcards_dir)):
                if filename.endswith(".txt"):
                    # Название параметра из имени файла
                    param_name_raw = os.path.splitext(filename)[0]
                    # Заменяем пробелы на нижнее подчеркивание для внутреннего ключа
                    param_name = param_name_raw.replace(" ", "_")
                    
                    file_path = os.path.join(wildcards_dir, filename)
                    values = []
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            values = [line.strip() for line in f if line.strip()]
                    except Exception as e:
                        print(f"[FaceGenerator] Ошибка чтения {filename}: {e}")
                    
                    # Первые два обязательных значения: Disabled и Random
                    options = ["Disabled", "Random"] + values
                    dynamic_inputs[param_name] = (options, {"default": "Disabled"})

        return {
            # Обязательные стандартные поля
            "required": {
                "ResultType": (["Natural", "json", "list"], {"default": "Natural"}),
                "PrePrompt": ("STRING", {"multiline": True, "default": ""}),
                "PostPrompt": ("STRING", {"multiline": True, "default": ""}),
            },
            # Динамически загружаемые параметры из папки Wildcards
            "optional": dynamic_inputs
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate"
    CATEGORY = "prompt"

    def generate(self, ResultType, PrePrompt, PostPrompt, **kwargs):
        main_prompt_lines = []
        wildcards_dir = os.path.join(os.path.dirname(__file__), "Wildcards")

        for param_key, selected_value in kwargs.items():
            # Если выбрано "Disabled" — параметр игнорируется
            if selected_value == "Disabled":
                continue
            
            # Возвращаем пробелы вместо нижних подчеркиваний для вывода
            param_label = param_key.replace("_", " ")
            val_to_use = selected_value
            
            # Если выбрано "Random" — берем случайное значение из файла
            if selected_value == "Random":
                file_path = os.path.join(wildcards_dir, f"{param_label}.txt")
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        values = [line.strip() for line in f if line.strip()]
                    if values:
                        val_to_use = random.choice(values)
            
            # Базовый формат вывода: Название параметра: Значение параметра
            main_prompt_lines.append(f"{param_label}: {val_to_use}")

        # Сборка MainPrompt
        main_prompt_str = ", ".join(main_prompt_lines)
        
        # Разделитель пробелами между PrePrompt, MainPrompt и PostPrompt
        parts = []
        if PrePrompt.strip():
            parts.append(PrePrompt.strip())
        if main_prompt_str.strip():
            parts.append(main_prompt_str.strip())
        if PostPrompt.strip():
            parts.append(PostPrompt.strip())

        final_prompt = ", ".join(parts)
        return (final_prompt,)

# Регистрация ноды в ComfyUI
NODE_CLASS_MAPPINGS = {
    "FaceGenerator": FaceGeneratorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FaceGenerator": "Face Generator"
}