# Importar las librerías necesarias
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import pandas as pd
from datetime import datetime

def create_gantt(df: pd.DataFrame):
    # 1. Limpieza y preparación de datos
    df.columns = ['proyecto', 'tarea', 'descripcion', 'inicio_plan', 'fin_plan', 'dias_plan', 'peso', 'estado', 'inicio_real', 'fin_real', 'progreso', 'visible', 'nombre_proyecto', 'OE', 'Y-Q']

    df = df[df['visible'] == 1].copy()

    if df.empty:
        return None 
    
    for col in ['inicio_plan', 'fin_plan', 'inicio_real', 'fin_real']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    today = pd.to_datetime(datetime.today().date())
    df.loc[(df['fin_real'].isnull()) & (df['inicio_real'].notnull()), 'fin_real'] = today
    
    df['duracion_plan'] = (df['fin_plan'] - df['inicio_plan']).dt.days
    df['duracion_real'] = (df['fin_real'] - df['inicio_real']).dt.days
    
    # Ordenar tareas
    df = df.sort_values(
        by=['proyecto', 'inicio_plan', 'fin_plan', 'tarea'],
        ascending=[True, True, True, True]
    )
    df = df.iloc[::-1].reset_index(drop=True)

    # 2. Creación del Gráfico
    num_tareas = len(df)
    fig, ax = plt.subplots(figsize=(12, num_tareas * 0.6))

    # --- LÍNEA VERTICAL PARA EL DÍA ACTUAL ---  
    min_date = df[['inicio_plan', 'inicio_real']].min(axis=1).min()
    max_date = df[['fin_plan', 'fin_real']].max(axis=1).max()

    if pd.notna(min_date) and pd.notna(max_date) and min_date <= today <= max_date:
        ax.axvline(x=today, color='black', linestyle='--', linewidth=1.5, zorder=10)
        ax.text(today, ax.get_ylim()[1], ' Hoy', va='bottom', ha='left', color='black', weight='bold')

    # 3. Dibujar las barras
    for i, row in df.iterrows():  
        # Barras para tiempos planificados          
        if pd.notna(row['inicio_plan']):
            color_plan = 'grey' if row['estado'] == 'Cancelada' else 'cornflowerblue'
            ax.barh(y=row['tarea'], left=row['inicio_plan'], width=row['duracion_plan'], 
                    height=0.6, color=color_plan, zorder=2)

        # Barras para tiempos reales
        if pd.notna(row['inicio_real']):
            ax.barh(y=row['tarea'], left=row['inicio_real'], width=row['duracion_real'], 
                    height=0.6, color='mediumseagreen', alpha=0.8, zorder=3)
                                        
    # ==============================================================================
    # 4. Formateo y Estilo del Gráfico
    # ==============================================================================
    
    # --- CONFIGURACIÓN EJE PRINCIPAL (Día 1 de cada mes) ---
    # Locator: Busca el día 1 de cada mes
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    # Formatter: Muestra Mes-Año (Ej: Ene-24) solo en los días 1
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
    
    # --- CONFIGURACIÓN EJE SECUNDARIO (Día 15 de cada mes) ---
    # Locator: Busca el día 15 de cada mes
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))
    # Nota: No ponemos Formatter al minor para que no salgan textos amontonados
    
    # --- ESTILOS DE CUADRÍCULA (GRID) ---
    # Grid PRINCIPAL (Día 1): Línea sólida gris
    ax.grid(visible=True, which='major', axis='x', linestyle='-', color='gray', alpha=0.4)
    
    # Grid SECUNDARIA (Día 15): Línea punteada más fina
    ax.grid(visible=True, which='minor', axis='x', linestyle=':', color='gray', alpha=0.4)
    
    # Grid Horizontal (opcional, para separar tareas)
    ax.grid(visible=True, axis='y', linestyle='--', color='gray', alpha=0.3)

    # Rotar etiquetas del eje X para lectura fácil
    plt.xticks(rotation=45, ha='right')
    
    # Leyenda
    planned_patch = mpatches.Patch(color='cornflowerblue', label='Planeado')
    real_patch = mpatches.Patch(color='mediumseagreen', label='Real')
    ax.legend(ncol=2, handles=[planned_patch, real_patch], bbox_to_anchor=(0.5, 1), loc='lower center', frameon=False)

    plt.tight_layout(rect=[0, 0, 0.85, 1])

    return plt

# Llamada a la función
create_gantt(xl("TablaTareas[#Todo]", headers=True))