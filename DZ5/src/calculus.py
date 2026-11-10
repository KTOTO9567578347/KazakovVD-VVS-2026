import numpy as np

def calculate_riemann_sum(F, L: float, R: float, N: int, method: str):
    """Вычислительный модуль: считает интеграл, фильтруя inf/nan из сумм"""
    dx = (R - L) / N
    x_edges = np.linspace(L, R, N + 1)

    if method == "Левые":
        x_eval = x_edges[:-1]
        align = "edge"
        x_bar_pos = x_eval
    elif method == "Правые":
        x_eval = x_edges[1:]
        align = "edge"
        x_bar_pos = x_eval - dx
    else:  # Средние
        x_eval = x_edges[:-1] + dx / 2
        align = "center"
        x_bar_pos = x_eval

    y_eval = F(x_eval)
    
    valid_mask = np.isfinite(y_eval)
    integral_value = np.sum(y_eval[valid_mask]) * dx
    
    return integral_value, x_eval, y_eval, x_bar_pos, align, dx