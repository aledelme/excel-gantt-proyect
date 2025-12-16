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
    # Invertimos para que el primer proyecto (alfabéticamente) quede arriba visualmente
    df = df.iloc[::-1].reset_index(drop=True)

    # 2. Configuración del Gráfico
    num_tareas = len(df)
    num_proyectos = df['proyecto'].nunique()
    
    # CORRECCIÓN 1: Calculamos altura para TODOS los encabezados de proyecto (incluido el primero)
    altura_fig = (num_tareas * 0.6) + (num_proyectos * 1.0) 
    
    fig, ax = plt.subplots(figsize=(12, max(altura_fig, 4)))

    # --- LÍNEA VERTICAL PARA EL DÍA ACTUAL ---  
    min_date = df[['inicio_plan', 'inicio_real']].min(axis=1).min()
    max_date = df[['fin_plan', 'fin_real']].max(axis=1).max()

    # Centro visual para los textos
    if pd.notna(min_date) and pd.notna(max_date):
        x_center = min_date + (max_date - min_date) / 2
    else:
        x_center = today

    if pd.notna(min_date) and pd.notna(max_date) and min_date <= today <= max_date:
        ax.axvline(x=today, color='black', linestyle='--', linewidth=1.5, zorder=10)
        ax.text(today, ax.get_ylim()[1], ' Hoy', va='bottom', ha='left', color='black', weight='bold')

    # 3. Dibujar las barras y líneas divisorias
    y_cursor = 0 
    yticks = []
    yticklabels = []
    
    for i, row in df.iterrows():  
        # --- LÓGICA DE SEPARADOR (Entre proyectos) ---
        if i > 0 and row['proyecto'] != df.iloc[i-1]['proyecto']:
            y_cursor += 0.8
            ax.axhline(y=y_cursor, color='black', linewidth=1, linestyle='-', zorder=1)
            
            # Texto del proyecto que queda DEBAJO de la línea (i-1)
            proj_code = df.iloc[i-1]['proyecto']
            proj_name = df.iloc[i-1]['nombre_proyecto']
            label_text = f"{proj_name} ({proj_code})"
            
            ax.text(x_center, y_cursor, label_text, 
                    ha='center', va='center', 
                    color='black', weight='bold', fontsize=9,
                    backgroundcolor='white', zorder=15)
            y_cursor += 0.8
        
        # --- DIBUJO DE BARRAS ---
        if pd.notna(row['inicio_plan']):
            color_plan = 'grey' if row['estado'] == 'Cancelada' else 'cornflowerblue'
            ax.barh(y=y_cursor, left=row['inicio_plan'], width=row['duracion_plan'], 
                    height=0.6, color=color_plan, zorder=2)

        if pd.notna(row['inicio_real']):
            ax.barh(y=y_cursor, left=row['inicio_real'], width=row['duracion_real'], 
                    height=0.6, color='mediumseagreen', alpha=0.8, zorder=3)
        
        yticks.append(y_cursor)
        yticklabels.append(row['tarea'])
        y_cursor += 1

    # --- CORRECCIÓN 2: LÍNEA FINAL (TOP) PARA EL PRIMER PROYECTO ---
    # Al terminar el bucle, estamos en la parte superior. Falta la cabecera del último grupo procesado.
    if not df.empty:
        y_cursor += 0.8
        ax.axhline(y=y_cursor, color='black', linewidth=1, linestyle='-', zorder=1)
        
        # Usamos la última fila del DF (que corresponde visualmente a la tarea más alta)
        top_row = df.iloc[-1]
        label_text = f"{top_row['nombre_proyecto']} ({top_row['proyecto']})"
        
        ax.text(x_center, y_cursor, label_text, 
                ha='center', va='center', 
                color='black', weight='bold', fontsize=9,
                backgroundcolor='white', zorder=15)
        # Espacio final arriba del todo
        y_cursor += 0.5

    # ==============================================================================
    # 4. Formateo y Estilo
    # ==============================================================================
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)

    # Ajustamos el límite Y para que se vea bien la última línea
    ax.set_ylim(-1, y_cursor)

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))
    
    ax.grid(visible=True, which='major', axis='x', linestyle='-', color='gray', alpha=0.4)
    ax.grid(visible=True, which='minor', axis='x', linestyle=':', color='gray', alpha=0.4)
    ax.grid(visible=True, axis='y', linestyle='--', color='gray', alpha=0.3)

    plt.xticks(rotation=45, ha='right')
    
    planned_patch = mpatches.Patch(color='cornflowerblue', label='Planeado')
    real_patch = mpatches.Patch(color='mediumseagreen', label='Real')
    # Ajustamos leyenda para que no pise el título superior
    ax.legend(ncol=2, handles=[planned_patch, real_patch], bbox_to_anchor=(0.5, 1.02), loc='lower center', frameon=False)

    plt.tight_layout(rect=[0, 0, 0.95, 0.95]) # Margen extra arriba

    return plt

create_gantt(xl("TablaTareas[#Todo]", headers=True))