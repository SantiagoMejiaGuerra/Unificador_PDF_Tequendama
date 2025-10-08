# Se realizara un codigo que unifique la información repetida en un mismo documento PDF para que no haya documentos repetidos y toda la infromación este en el mismo archivo pero con paginas diferentes

import os
import customtkinter
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import fitz
import sys
import re
from collections import defaultdict

# Primero crearemos la ventana principal y los wodgets que permitiran al usuario selecionar las carpetas.
# Además creamos diferentes funciones que nos ayudaran a mejorar nuestro codigo para manejar diferentes errores

# Modo de apariencia por defecto de la ventana
customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")


# Creamos variables globales para almacenar rutas que se seleccionen
source_folder = ""
destination_folder = ""


def extract_document_identification_info(filename):
    """
    Extrae información de la identificación del nombre del archivo
    busca patrones como CC1001526294, TI12345678, etc.
    """
    # Limpiamos el nombre del archivo antes de aplicar el regex
    # Eliminamos los espacios tanto al inicio como al final
    clean_filename = filename.strip()

    # Eliminamos extensiones duplicadas (ej: nombre.PDF.pdf --> nombre.pdf)
    pattern_double_ext = r'\.(?:pdf|PDF)\.(?:pdf|PDF)$'
    clean_filename = re.sub(pattern_double_ext, '.pdf', clean_filename, flags=re.IGNORECASE)

    # Busca el patron para capturar el tipo de docuemento, fromato, tipo y el numero de ID
    pattern = r'^(.*?)_.*_(F\d+)_(CC|TI|RC|CE|CN|PT)(\d{6,15})\b'
    search = re.search(pattern, filename.upper(), re.IGNORECASE)

    if search:
        return search.group(1).upper(), search.group(2).upper(), search.group(3).upper(), search.group(4)
    
    return None, None, None, None

def create_grouping_key(tipo_documento, numero_id):
    """
    Crea una clave unica para agrupar archivos por tipo de documento y ID
    """
    return f"{tipo_documento}_{numero_id}"

def get_display_name(filename):
    """
    Obtendra el nombre limpio del archivo sin mostrar las sobles extensiones.
    """

    clean_name = filename.strip()
    # Elimina las extensiones duplicadas
    pattern = r'\.(?:pdf|PDF)\.(?:pdf|PDF)$'
    clean_name = re.sub(pattern, '.pdf', clean_name, flags=re.IGNORECASE)
    return clean_name


def change_apparence_mode(new_apparence_mode):
    """
    Cambia el modo de apariencia (claro u oscuro) según el valor del switch
    """
    if new_apparence_mode == 1:
        customtkinter.set_appearance_mode("Dark")
    else:
        customtkinter.set_appearance_mode("Light")


def interfaz_usuario():
    """
    Se creara la ventana de la interfaz de usuario
    """
    root = customtkinter.CTk()
    root.title("Unificador y Organizador de PDF")
    root.geometry("500x450") # Le damos el tamaño a la ventana

    def on_closing():
        root.destroy()
        sys.exit()
        
    # Asigna la función de cierre al protocolo WM_DELETE_WINDOW
    root.protocol("WM_DELETE_WINDOW", on_closing)

    main_frame = customtkinter.CTkFrame(root, corner_radius=10)
    main_frame.pack(padx=20, pady=20, expand=True, fill='both')

    # Ponemos selector de apariencia por medio de un switch
    apparence_mode_label = customtkinter.CTkLabel(main_frame, text="Modo de Apariencia", font=("Helvetica", 12, "bold"))
    apparence_mode_label.pack(anchor="w", padx=20, pady=(10, 0))

    apparence_mode_switch = customtkinter.CTkSwitch(main_frame,  text="Claro / Oscuro", command=lambda: change_apparence_mode(apparence_mode_switch.get()),
                                                    onvalue=1, offvalue=0)
    apparence_mode_switch.pack(anchor="w", padx=20)

    # Titulo principal
    title_label = customtkinter.CTkLabel(main_frame, text="Organizador de Documentos", font=customtkinter.CTkFont(size=20, weight="bold"))
    title_label.pack(pady=(0,20))

    # Aqui seleccionamos la carpeta de origen donde estan todas las subcarpetas con la infromación
    source_label= customtkinter.CTkLabel(main_frame, text="1. Seleccione la carpeta principal con los PDF's:", font=("Helvetica", 12))
    source_label.pack(pady=(5, 0))

    global source_path
    source_path = customtkinter.CTkLabel(main_frame, text="", wraplength=450, fg_color="transparent", text_color="gray")
    source_path.pack(pady=(0,5))

    btn_select_source= customtkinter.CTkButton(main_frame, text="Seleccionar Carpeta de Origen", command=select_source_folder, corner_radius=8)
    btn_select_source.pack()

    # Pondremos separadores entre una sección y otra
    separetor = customtkinter.CTkLabel(main_frame, height=1, fg_color="gray", text="", corner_radius=4)
    separetor.pack(fill="x", padx=5, pady=10)

    # Ahora si seleccionamos la carpeta de destino
    dest_label = customtkinter.CTkLabel(main_frame, text="2. Selecciona la carpeta de destino:", font=("Helvetica", 12))
    dest_label.pack(pady=(5,0))

    global dest_path_label
    dest_path_label = customtkinter.CTkLabel(main_frame, text="", wraplength=450, fg_color="transparent", text_color="gray")
    dest_path_label.pack(pady=(0, 5))

    btn_select_dest = customtkinter.CTkButton(main_frame, text="Seleccionar Carpeta de Destino", command=select_destination_folder, corner_radius=8)
    btn_select_dest.pack()

    # Agregamos por ultimo el boton que ejecutara el proceso
    global process_button
    process_button = customtkinter.CTkButton(main_frame, text="Inciar Proceso de Organización", state=tk.DISABLED, command=start_processing, corner_radius=8, fg_color="#01949c", hover_color="darkblue")
    process_button.pack(pady=(20, 0))

    root.mainloop()
# ----- ------ ----- -----
# Creamos las funciones de selección que estas actualizan las variables globales y habilitan los botone
def select_source_folder():
    """
    Permitira al Usuario seleccionar la carpeta de origen.
    """
    global source_folder
    source_folder = filedialog.askdirectory(title="Selecciona la Carpeta de Origen")
    if source_folder:
        source_path.configure(text=f"Carpeta de Origen: {source_folder}")
        check_folders_selected()

def select_destination_folder():
    """
    Permite que el usuario pueda seleccionar la carpeta de destino
    """
    global destination_folder
    destination_folder = filedialog.askdirectory(title="Seleccione la Carpeta de Destino")
    if destination_folder:
        dest_path_label.configure(text=f"Carpeta de Destino: {destination_folder}")
        check_folders_selected()

def check_folders_selected():
    """
    Habilitara el boton de 'Inicio de proceso' simpre y cuando se hayan seleccionado las carpetas
    """
    if source_folder and destination_folder:
        process_button.configure(state=tk.NORMAL)

def start_processing():
    """
    Inicara el proceso principal que sera la unificación y organización. 
    """
    process_pdf(source_folder, destination_folder)


# Luego de tener la logica de la ventana, implementaremos las funciones que buscaran los duplicados, realizaran la unificación de la infromación
# y además realizara el proceso de mover los archivos PDF


def find_duplicate_files(root_folder):
    """
    Recorre la carpta y encuentra archivos que deben unificarse.

    CRITERIOS DE UNIFICACIÓN:
    1. Mismo tipo de documento (HAO, CRC, PDC, etc)
    2. Mismo número de identificación
    """

    groups_by_key = defaultdict(list)

    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if filename.lower().endswith(".pdf"):
                # Obtener la información completa del archivo
                tipo_documento, formato, tipo_id, numero_id = extract_document_identification_info(filename)
                
                if tipo_documento and numero_id:
                    file_info = {
                        'path': file_path,
                        'original_name': filename,
                        'tipo_documento': tipo_documento,
                        'formato': formato,
                        'tipo_id': tipo_id,
                        'numero_id': numero_id
                    }
                    grouping_key = create_grouping_key(tipo_documento, numero_id)
                    groups_by_key[grouping_key].append(file_info)
    
    # Separamos los duplicados de los archivos únicos (que no tienen duplicado)
    duplicate_groups = {key: files for key, files in groups_by_key.items() if len(files) > 1}

    # Obtenemos la lista completa de los archivos procesados
    all_processed_files = []
    for files in groups_by_key.values():
        all_processed_files.extend(files)
    
    # Se buscan los archivos que no se procesaron para clasificación como "únicos"
    unique_files = []
    processed_paths = {f['path'] for f in all_processed_files}

    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if filename.lower().endswith(".pdf") and file_path not in processed_paths:
                unique_files.append({
                    'path': file_path,
                    'original_name': filename
                })
    
    return duplicate_groups, unique_files


def merge_pdf(file_paths, output_path):
    """
    Unificara el contenido de varios archivos PDF.
    """
    try:
        merged_doc = fitz.open()
        for file_path in file_paths:
            try:
                doc_merge = fitz.open(file_path['path'])
                merged_doc.insert_pdf(doc_merge)
                doc_merge.close()
            except Exception as e:
                print(f"Error al procesar {file_path['original_name']}: {e}")
                continue
            
        merged_doc.save(output_path)
        merged_doc.close()
        return True
    except Exception as e:
        messagebox.showerror("Error de Unificación", f"Ocurrió un error al unificar los archivos: {e}")
        return False


def process_pdf(source_folder, destination_folder):
    """
    Este realizará el orquestamiento de los procesos de unificación y organización.
    """

    duplicate_groups, unique_files = find_duplicate_files(source_folder)

    # Se iniciara el proceso de unificación de duplicados
    unified_count = 0
    if duplicate_groups:
        for key, file_list in duplicate_groups.items():
            # Obtenemos el primero archivo del grupo para tomar formato y tipo ID
            first_file_info = file_list[0]

            tipo_doc = first_file_info['tipo_documento']
            formato = first_file_info['formato']
            tipo_id = first_file_info['tipo_id']
            numero_id = first_file_info['numero_id']
            
            if tipo_doc and formato and tipo_id and numero_id:
                clean_name = f"{tipo_doc}_900847382_{formato}_{tipo_id}{numero_id}.pdf"
            else:
                clean_name = f"UNIFICADO_DESCONOCIDO_{key}.pdf"

            output_path = os.path.join(destination_folder, clean_name)

            # Evitar sobreescribir achivos existentes
            counter = 1
            base_name, ext = os.path.splitext(clean_name)
            while os.path.exists(output_path):
                output_path = os.path.join(destination_folder, f"{base_name}_{counter}{ext}")
                counter += 1
            
            if merge_pdf(file_list, output_path):
                unified_count += 1
    
    # Copia de los archivos únicos a la carpeta destino
    copied_count = 0
    for file_info in unique_files:
        # Nos aseguramos que no haya doble extensión
        clean_name = get_display_name(file_info['original_name'])

        # Si el nombre no contiene su extensión pdf, se agregara
        if not clean_name.lower().endswith('.pdf'):
            clean_name += '.pdf'
        
        dest_path = os.path.join(destination_folder, clean_name)

        # Si el archivo ya existe en el destino, agrega el sufijo
        base, ext = os.path.splitext(clean_name)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(destination_folder, f"{base}_{counter}{ext}")
            counter += 1
        
        try:
            shutil.copy2(file_info['path'], dest_path)
            copied_count += 1
        except Exception as e:
            print(f"Error copiando {file_info['original_name']}: {e}")
    
    # Entrega del mensaje final con estadisticas
    total_groups = len(duplicate_groups)
    total_unique = len(unique_files)

    final_message = f"Proceso de organización completado: \n\n"
    final_message += f"• Grupos unificados: {unified_count} de {total_groups}\n"
    final_message += f"• Archivos únicos copiados: {copied_count} de {total_unique}\n"
    final_message += f"• Ubicación: {destination_folder}"

    messagebox.showinfo("Proceso Finalizado", final_message)


if __name__ == "__main__":
    interfaz_usuario()


