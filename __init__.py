import os
import random

class FaceGeneratorNode:
    @classmethod
    def INPUT_TYPES(cls):
        wildcards_dir = os.path.join(os.path.dirname(__file__), "Wildcards")
        os.makedirs(wildcards_dir, exist_ok=True)
        
        dynamic_inputs = {}
        
        if os.path.exists(wildcards_dir):
            for filename in sorted(os.listdir(wildcards_dir)):
                if filename.endswith(".txt"):
                    param_name_raw = os.path.splitext(filename)[0]
                    param_name = param_name_raw.replace(" ", "_")
                    
                    file_path = os.path.join(wildcards_dir, filename)
                    values = []
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            values = [line.strip() for line in f if line.strip()]
                    except Exception as e:
                        print(f"[FaceGenerator] Ошибка чтения {filename}: {e}")
                    
                    options = ["Disabled", "Random"] + values
                    dynamic_inputs[param_name] = (options, {"default": "Disabled"})

        return {
            "required": {
                # Временно закомментированный ResultType
                # "ResultType": (["Natural", "json", "list"], {"default": "Natural"}),
                
                # Добавляем seed для обхода кэша ComfyUI и управления рандомом
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "control_after_generate": "randomize"}),
                
                # Глобальный переключатель Random перед основным блоком
                "Global_Random": ([False, True], {"default": False}),
                
                # Увеличенные поля для текста
                "PrePrompt": ("STRING", {"multiline": True, "default": ""}),
                "PostPrompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": dynamic_inputs
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate"
    CATEGORY = "prompt"

    def generate(self, seed, Global_Random, PrePrompt, PostPrompt, **kwargs):
        # Инициализируем генератор случайных чисел переданным seed, 
        # чтобы рандомизация менялась каждый раз при изменении seed
        random.seed(seed)
        
        main_prompt_lines = []
        wildcards_dir = os.path.join(os.path.dirname(__file__), "Wildcards")

        for param_key, selected_value in kwargs.items():
            if Global_Random and selected_value != "Disabled":
                selected_value = "Random"

            if selected_value == "Disabled":
                continue
            
            param_label = param_key.replace("_", " ")
            val_to_use = selected_value
            
            if selected_value == "Random":
                possible_files = [f"{param_label}.txt", f"{param_key}.txt"]
                file_path = None
                
                for pf in possible_files:
                    full_path = os.path.join(wildcards_dir, pf)
                    if os.path.exists(full_path):
                        file_path = full_path
                        break
                
                if file_path and os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        values = [line.strip() for line in f if line.strip()]
                    if values:
                        val_to_use = random.choice(values)

            main_prompt_lines.append(f"{param_label}: {val_to_use}")

        main_prompt_str = "\n".join(main_prompt_lines)
        
        parts = []
        if PrePrompt.strip():
            parts.append(PrePrompt.strip())
        if main_prompt_str.strip():
            parts.append(main_prompt_str.strip())
        if PostPrompt.strip():
            parts.append(PostPrompt.strip())

        final_prompt = "\n".join(parts)
        return (final_prompt,)

NODE_CLASS_MAPPINGS = {
    "FaceGenerator": FaceGeneratorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FaceGenerator": "Face Generator"
}