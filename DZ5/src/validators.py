import numpy as np

MODES = ["Левая", "Правая", "Центр"]
DEFAULT = 2

SAFE_DICT = {
            'x': None,  # Будет подставляться массив значений
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
            'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
            'exp': np.exp, 'log': np.log, 'log10': np.log10,
            'sqrt': np.sqrt, 'abs': np.absolute, 'pi': np.pi, 'e': np.e,
            'power': np.power
        }

def is_mode(text: str):
    global MODES
    if text in MODES:
        return True
    return False

def is_float(text: str):
    try:
        val = float(text)
        return True
    except:
        return False

def is_nat(text: str):
    try:
        val = int(text)
        if val <= 0:
            return False
        return True
    except:
        return False

def check_bounds(L_t: str, R_t: str):
    if ((not is_float(L_t)) or (not is_float(R_t))):
        return False

    L = float(L_t)
    R = float(R_t)

    if (R <= L):
        return False

    return True

def create_vectorized_function(expression_str: str):
    """
    Улучшенная фабрика функций. Безопасно переваривает деление на ноль,
    возвращая np.inf / np.nan, и передает готовую функцию дальше в пайплайн.
    """
    safe_dict = {
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
        'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
        'exp': np.exp, 'log': np.log, 'log10': np.log10,
        'sqrt': np.sqrt, 'abs': np.absolute, 'pi': np.pi, 'e': np.e
    }
    
    expr = expression_str.strip()
    if not expr:
        raise ValueError("Выражение не может быть пустым.")

    def generated_function(x):
        x_array = np.asarray(x, dtype=np.float64)
        
        context = safe_dict.copy()
        context['x'] = x_array
        
        result = eval(expr, {"__builtins__": None}, context)
        
        if isinstance(result, (int, float)):
            return np.full_like(x_array, float(result))
            
        return result

    return generated_function