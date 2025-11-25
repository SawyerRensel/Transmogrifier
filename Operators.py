#  █████       █████   █████████  ██████████ ██████   █████  █████████  ██████████
# ░░███       ░░███   ███░░░░░███░░███░░░░░█░░██████ ░░███  ███░░░░░███░░███░░░░░█
#  ░███        ░███  ███     ░░░  ░███  █ ░  ░███░███ ░███ ░███    ░░░  ░███  █ ░ 
#  ░███        ░███ ░███          ░██████    ░███░░███░███ ░░█████████  ░██████   
#  ░███        ░███ ░███          ░███░░█    ░███ ░░██████  ░░░░░░░░███ ░███░░█   
#  ░███      █ ░███ ░░███     ███ ░███ ░   █ ░███  ░░█████  ███    ░███ ░███ ░   █
#  ███████████ █████ ░░█████████  ██████████ █████  ░░█████░░█████████  ██████████
# ░░░░░░░░░░░ ░░░░░   ░░░░░░░░░  ░░░░░░░░░░ ░░░░░    ░░░░░  ░░░░░░░░░  ░░░░░░░░░░ 

##### BEGIN GPL LICENSE BLOCK #####

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 

##### END GPL LICENSE BLOCK #####



#  █████       █████ ███████████  ███████████     █████████   ███████████   █████ ██████████  █████████ 
# ░░███       ░░███ ░░███░░░░░███░░███░░░░░███   ███░░░░░███ ░░███░░░░░███ ░░███ ░░███░░░░░█ ███░░░░░███
#  ░███        ░███  ░███    ░███ ░███    ░███  ░███    ░███  ░███    ░███  ░███  ░███  █ ░ ░███    ░░░ 
#  ░███        ░███  ░██████████  ░██████████   ░███████████  ░██████████   ░███  ░██████   ░░█████████ 
#  ░███        ░███  ░███░░░░░███ ░███░░░░░███  ░███░░░░░███  ░███░░░░░███  ░███  ░███░░█    ░░░░░░░░███
#  ░███      █ ░███  ░███    ░███ ░███    ░███  ░███    ░███  ░███    ░███  ░███  ░███ ░   █ ███    ░███
#  ███████████ █████ ███████████  █████   █████ █████   █████ █████   █████ █████ ██████████░░█████████ 
# ░░░░░░░░░░░ ░░░░░ ░░░░░░░░░░░  ░░░░░   ░░░░░ ░░░░░   ░░░░░ ░░░░░   ░░░░░ ░░░░░ ░░░░░░░░░░  ░░░░░░░░░  

import bpy
from bpy.types import (
    Operator, 
) 
from bpy.props import (
    IntProperty,
    StringProperty
)
import os
import subprocess
import shutil
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
import webbrowser
import json
import threading
import queue
from . import Functions



#     ███████    ███████████  ██████████ ███████████     █████████   ███████████    ███████    ███████████    █████████ 
#   ███░░░░░███ ░░███░░░░░███░░███░░░░░█░░███░░░░░███   ███░░░░░███ ░█░░░███░░░█  ███░░░░░███ ░░███░░░░░███  ███░░░░░███
#  ███     ░░███ ░███    ░███ ░███  █ ░  ░███    ░███  ░███    ░███ ░   ░███  ░  ███     ░░███ ░███    ░███ ░███    ░░░ 
# ░███      ░███ ░██████████  ░██████    ░██████████   ░███████████     ░███    ░███      ░███ ░██████████  ░░█████████ 
# ░███      ░███ ░███░░░░░░   ░███░░█    ░███░░░░░███  ░███░░░░░███     ░███    ░███      ░███ ░███░░░░░███  ░░░░░░░░███
# ░░███     ███  ░███         ░███ ░   █ ░███    ░███  ░███    ░███     ░███    ░░███     ███  ░███    ░███  ███    ░███
#  ░░░███████░   █████        ██████████ █████   █████ █████   █████    █████    ░░░███████░   █████   █████░░█████████ 
#    ░░░░░░░    ░░░░░        ░░░░░░░░░░ ░░░░░   ░░░░░ ░░░░░   ░░░░░    ░░░░░       ░░░░░░░    ░░░░░   ░░░░░  ░░░░░░░░░  

# Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), addon.py, Line 638
class TRANSMOGRIFIER_OT_help(Operator):
    """Open online documentation in web browser"""
    bl_idname = "transmogrifier.help"
    bl_label = "Help"
    bl_description = "Open online documentation in a web browser\n(https://sapwoodstudio.github.io/transmogrifier)"
    
    link: StringProperty(
        name="Help",
        default="https://sapwoodstudio.github.io/transmogrifier"
    )    

    def execute(self, context):   
        try:
            webbrowser.open(self.link)
        except:
            self.report({'ERROR'}, "Could not open online documentation")
        return {'FINISHED'}   


# Operator called when pressing the Batch Convert button.
class TRANSMOGRIFIER_OT_transmogrify(Operator):
    """Batch converts 3D files and associated textures into other formats"""
    bl_idname = "transmogrifier.transmogrify"
    bl_label = "Batch Convert"
    
    _timer = None
    _thread = None
    _queue = None
    _process = None
    
    file_count = 0
    total_files = 0

    def invoke(self, context, event):
        settings = bpy.context.scene.transmogrifier_settings
        imports = bpy.context.scene.transmogrifier_imports
        exports = bpy.context.scene.transmogrifier_exports
        scripts = bpy.context.scene.transmogrifier_scripts

        # Check if there are imports and exports. Stop batch converter if there is not at least one of each.
        if not imports or not exports:
            if not imports:
                message = "Please Add Import"
            elif not exports: 
                message = "Please Add Export"

            self.report({'ERROR'}, message)
            return {'FINISHED'}

        # Check directory and file paths.  Stop batch converter if they don't check-out.
        collection_properties_to_check = [imports, exports]
        for collection_property in collection_properties_to_check:
            for index, instance in enumerate(collection_property):
                if collection_property == exports and settings.export_adjacent:  # Skip if models are getting exported adjacent to their respective imports.
                    continue
                directory_checks_out, message = Functions.check_directory_path(self, context, instance.directory)
                if not directory_checks_out:
                    self.report({'ERROR'}, message)
                    return {'FINISHED'}
        
        custom_menu_options_to_check = [settings.textures_source, settings.uv_export_location]
        directories_to_check = [settings.textures_custom_dir, settings.uv_directory_custom]
        for index, menu in enumerate(custom_menu_options_to_check):
            if menu != "Custom":
                continue
            directory_checks_out, message = Functions.check_directory_path(self, context, directories_to_check[index])
            if not directory_checks_out:
                self.report({'ERROR'}, message)
                return {'FINISHED'}
                
        for index, custom_script in enumerate(scripts):
            custom_script_checks_out, message = Functions.check_custom_script_path(self, context, custom_script.file, custom_script.name)
            if not custom_script_checks_out:
                self.report({'ERROR'}, message)
                return {'FINISHED'}

        # Calculate total files for progress bar
        self.total_files = 0
        import_files_dict = Functions.get_import_files(self, context)
        for key, value in import_files_dict.items():
            self.total_files += len(value)
            
        # If optimization is off, we might be exporting multiple formats per file, 
        # but the converter loop structure in Converter.py iterates over imports first.
        # The "CONVERTER END" message appears after each export if not optimized?
        # Let's check Converter.py logic. 
        # If optimize: loop imports -> loop exports -> converter(). 
        # If not optimize: loop imports -> converter_stage_import -> loop exports -> converter_stage_export.
        # "CONVERTER END" is printed in converter_stage_export.
        # So total steps = total imports * total exports (roughly).
        # Let's count total export actions.
        
        num_exports = len(exports)
        self.total_steps = self.total_files * num_exports
        
        # Initialize queue
        self._queue = queue.Queue()
        
        # Start the process
        self.start_transmogrification(context)
        
        # Start Progress Bar
        context.window_manager.progress_begin(0, self.total_steps)
        
        # Start Modal
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            # Read from queue
            while not self._queue.empty():
                try:
                    line = self._queue.get_nowait()
                    if "CONVERTER END:" in line:
                        self.file_count += 1
                        context.window_manager.progress_update(self.file_count)
                except queue.Empty:
                    break
            
            # Check if process is finished
            if self._process.poll() is not None:
                context.window_manager.progress_end()
                self.finish(context)
                return {'FINISHED'}
                
        elif event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}
            
        return {'PASS_THROUGH'}

    def cancel(self, context):
        if self._process:
            self._process.kill()
        context.window_manager.progress_end()
        context.window_manager.event_timer_remove(self._timer)
        self.report({'INFO'}, "Conversion Cancelled")

    def start_transmogrification(self, context):
        # Create settings_dict dictionary from transmogrifier_settings to pass to write_json function later.
        settings_dict = Functions.get_settings_dict(self, context, True, True)

        # Create path to blender.exe
        blender_dir = bpy.app.binary_path

        # Create path to Converter.blend
        converter_blend = Path(__file__).parent.resolve() / "Converter.blend"

        # Create path to Converter.py
        converter_py = Path(__file__).parent.resolve() / "Converter.py"
        
        # Create path to Transmogrifier directory
        transmogrifier_dir = Path(__file__).parent.resolve()

        # Write settings to JSON file.
        settings_json = Path(__file__).parent.resolve() / "Settings.json"
        Functions.write_json(settings_dict, settings_json)

        # Run Converter.py
        self._process = subprocess.Popen(
            [
                blender_dir,
                converter_blend,
                "--python",
                converter_py,
            ],
            cwd=transmogrifier_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        ) 
        
        # Start thread to read stdout
        self._thread = threading.Thread(target=self.read_stdout, args=(self._process, self._queue))
        self._thread.daemon = True
        self._thread.start()

    def read_stdout(self, process, queue):
        for line in iter(process.stdout.readline, ''):
            queue.put(line)
            print(line, end='') # Print to Blender console as well
        process.stdout.close()

    def select_children_recursive(self, obj, context):
        for c in obj.children:
            if obj.type in context.scene.transmogrifier.texture_resolution_include:
                c.select_set(True)
            self.select_children_recursive(c, context)

    def finish(self, context):
        context.window_manager.event_timer_remove(self._timer)
        
        # Report batch conversion results.
        converter_report_json = Path(__file__).parent.resolve() / "Converter_Report.json"
        if converter_report_json.exists():
            converter_report_dict = Functions.read_json(converter_report_json)
            conversion_count = converter_report_dict.get("conversion_count", 0)
            if conversion_count > 1:
                self.report({'INFO'}, f"Conversion complete. {conversion_count} files were converted.")
            elif conversion_count == 1:
                self.report({'INFO'}, f"Conversion complete. {conversion_count} file was converted.")
            else:
                self.report({'INFO'}, f"Could not convert or no items needed conversion. {conversion_count} files were converted.")
        else:
             self.report({'ERROR'}, "Could not convert.")



class TRANSMOGRIFIER_OT_forecast(Operator):
    """Calculate batch conversion and display info message of the forecast"""
    bl_idname = "transmogrifier.forecast"
    bl_label = "Conversion Forecast"

    def execute(self, context):
        settings = bpy.context.scene.transmogrifier_settings
        imports = bpy.context.scene.transmogrifier_imports
        exports = bpy.context.scene.transmogrifier_exports
        
        # Check if any imports exist.
        if not imports or not exports:
            if not imports:
                message = "Please Add Import"
            elif not exports:
                message = "Please Add Export"
            self.popup_message(context, message=message, title="Forecast", icon='INFO')
            self.report({'INFO'}, message)
            return {'FINISHED'}


        # Check to make sure import directories exist.
        for i in imports:
            directory_checks_out, message = Functions.check_directory_path(self, context, i.directory)
            if not directory_checks_out:
                self.report({'ERROR'}, message)
                return {'FINISHED'}
        
        # If import directories exist, get import files.
        import_files_dict = Functions.get_import_files(self, context)

        # Concatenate import formats with the respective number of files found for each.
        imports_string = ""
        count_total = 0
        for key, value in import_files_dict.items():
            count = len(import_files_dict[key])
            count_total += count
            imports_string += f"{count} {key}, "

        # Concatenate exports formats with the total count.
        exports_string = ""
        for index, instance in enumerate(exports):
            exports_string += f"{count_total} {instance.name}, "

        # Trim off ending space and comma.
        imports_string = imports_string[:-2]
        exports_string = exports_string[:-2]

        # Info message.
        message = f"{imports_string}  ⇒  {exports_string}"

        # Report message.
        self.popup_message(context, message=message, title="Forecast", icon='INFO')
        self.report({'INFO'}, message)
        return {'FINISHED'}


    # Message box pop-up.
    def popup_message(self, context, message="", title="Message Box", icon='INFO'):

        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)



# Install import/export/transmogrifier presets shipped with Transmogrifier to relevant Blender Preferences directory.
class TRANSMOGRIFIER_OT_install_presets(Operator):
    """Copy example presets shipped with Transmogrifier to User Preferences"""
    bl_idname = "transmogrifier.install_presets"
    bl_label = "Install Example Presets"

    def execute(self, context):
        # Define paths.
        presets_dir_src = Path(__file__).parent / "presets" / "operator"
        presets_dir_dest = Path(bpy.utils.user_resource('SCRIPTS', path="presets/operator"))

        # Make list of source paths and destination paths (parents).
        dir_src_list = [presets_dir_src]
        dir_dest_list = [presets_dir_dest]
        
        # Loop through list of source paths and copy files to parent- (or operator) specific destinations. Overwrite original files to ensure they get updated with each release.
        for dir_src in dir_src_list:
            for subdir, dirs, files in os.walk(dir_src):
                for file in files:
                    operator = Path(subdir).name
                    file_src = Path(subdir, file)
                    dir_dest_parent = dir_dest_list[dir_src_list.index(dir_src)]
                    file_dest = Path(dir_dest_parent, operator, file)
                    dir_dest = Path(file_dest).parent
                    if not Path(dir_dest).exists():
                        Path(dir_dest).mkdir(parents=True, exist_ok=True)
                    shutil.copy(file_src, file_dest)
        
        self.report({'INFO'}, "Installed Example Presets")

        return {'FINISHED'}


class TRANSMOGRIFIER_OT_add_preset(Operator):
    """Creates a Transmogrifier preset from current settings"""
    bl_idname = "transmogrifier.add_preset"
    bl_label = "Add Transmogrifier Preset"

    # Captured preset name from pop-up dialog window.
    preset_name: bpy.props.StringProperty(name="Name", default="")

    def execute(self, context):
        # Set Transmogrifier operator preset directory and new preset file.
        add_preset_name = f"{self.preset_name}.json"
        transmogrifier_preset_dir = Path(bpy.utils.user_resource('SCRIPTS', path="presets/operator")) / "transmogrifier"
        if not Path(transmogrifier_preset_dir).exists():  # Check if operator preset directory exists.
            Path(transmogrifier_preset_dir).mkdir(parents=True, exist_ok=True)  # Make Transmogrifier operator preset directory.
        preset_json = transmogrifier_preset_dir / add_preset_name

        # Get current Transmogrifier settings.
        settings_dict = Functions.get_settings_dict(self, context, False, False)

        # Save new Transmogrifier operator preset as JSON file.
        Functions.write_json(settings_dict, preset_json)
        self.report({'INFO'}, f"Added Transmogrifier preset: {add_preset_name}")
        return {'FINISHED'}
    
    # Pop-up dialog window to capture new preset name.
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
    

class TRANSMOGRIFIER_OT_remove_preset(Operator):
    """Removes currently selected Transmogrifier preset"""
    bl_idname = "transmogrifier.remove_preset"
    bl_label = "Remove Transmogrifier Preset"

    def execute(self, context):
        # Get selected Transmogrifier operator preset.
        settings = bpy.context.scene.transmogrifier_settings
        remove_preset_name = f"{settings.transmogrifier_preset_enum}.json"

        # Set Transmogrifier operator preset directory and preset file to be removed.
        transmogrifier_preset_dir = Path(bpy.utils.user_resource('SCRIPTS', path="presets/operator")) / "transmogrifier"
        if not Path(transmogrifier_preset_dir).exists():  # Check if operator preset directory exists.
            Path(transmogrifier_preset_dir).mkdir(parents=True, exist_ok=True)  # Make Transmogrifier operator preset directory.
        preset_json = transmogrifier_preset_dir / remove_preset_name

        # Return early and report error if Transmogrifier operator preset does not exist.
        if not preset_json.is_file():
            self.report({'ERROR'}, f"Transmogrifier preset does not exist: {remove_preset_name}")
            return {'CANCELLED'}

        # Remove Transmogrifier operator preset.
        self.report({'INFO'}, f"Removed Transmogrifier preset: {remove_preset_name}")
        Path.unlink(preset_json)
        return {'FINISHED'}


# Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), preset_manager.py, Line 124
class TRANSMOGRIFIER_OT_load_preset(Operator, ImportHelper):
    """Load a Transmogrifier preset from a JSON file"""
    bl_idname = "transmogrifier.load_preset"
    bl_label = "Load Preset"
    bl_options = {'UNDO'}

    filename_ext = '.json'

    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )

    def execute(self, context):
        settings = bpy.context.scene.transmogrifier_settings
        
        # Get filepath from browser.
        preset_src = Path(self.filepath)

        # Get preset name.
        preset_name = preset_src.name
        
        # Check if Transmogrifier preset directory exists.
        transmogrifier_preset_dir = Path(bpy.utils.user_resource('SCRIPTS', path="presets/operator")) / "transmogrifier"
        if not Path(transmogrifier_preset_dir).exists():  # Check if operator preset directory exists.
            Path(transmogrifier_preset_dir).mkdir(parents=True, exist_ok=True)  # Make Transmogrifier operator preset directory.
        preset_dest = transmogrifier_preset_dir / preset_name
        
        # Copy preset file to preset directory.  Overwrite existing.
        shutil.copy(preset_src, preset_dest)
        
        # Concatenate the current property assignment.
        property_assignment = f"settings.transmogrifier_preset = {repr(preset_src.stem)}"

        # Make the property (key) equal to the preset (value).
        exec(property_assignment)
        
        # Load preset (Update settings and UI from preset file).
        Functions.set_settings(self, context)

        self.report({'INFO'}, f"Added Transmogrifier preset: {preset_name}")
        return {'FINISHED'}


# Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), UI.py, Line 782
class TRANSMOGRIFIER_OT_add_import(Operator):
    '''Add new import to UI'''

    bl_idname = "transmogrifier.add_import"
    bl_label = "Add Import"
    bl_description = "Add new import to UI"

    def execute(self, context):
        settings = bpy.context.scene.transmogrifier_settings
        new_import = context.scene.transmogrifier_imports.add()
        new_import.name = new_import.format

        if settings.link_import_settings:
            Functions.link_import_settings(self, context)
        return {'FINISHED'}


class TRANSMOGRIFIER_OT_remove_import(Operator):
    '''Remove import from UI'''

    bl_idname = "transmogrifier.remove_import"
    bl_label = "Remove Import"
    bl_description = "Remove import from UI"

    index: IntProperty(
        name="Index to remove",
        description="Index of the import to remove",
        min=0, 
    )   

    def execute(self, context):
        context.scene.transmogrifier_imports.remove(self.index)
        return {'FINISHED'}


# Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), UI.py, Line 782
class TRANSMOGRIFIER_OT_add_export(Operator):
    '''Add new export to UI'''

    bl_idname = "transmogrifier.add_export"
    bl_label = "Add Export"
    bl_description = "Add new export to UI"

    def execute(self, context):
        settings = bpy.context.scene.transmogrifier_settings
        new_export = context.scene.transmogrifier_exports.add()
        
        if settings.link_export_settings:
            Functions.link_export_settings(self, context)
        return {'FINISHED'}


class TRANSMOGRIFIER_OT_remove_export(Operator):
    '''Remove export from UI'''

    bl_idname = "transmogrifier.remove_export"
    bl_label = "Remove Export"
    bl_description = "Remove export from UI"

    index: IntProperty(
        name="Index to remove",
        description="Index of the export to remove",
        min=0, 
    )   

    def execute(self, context):
        context.scene.transmogrifier_exports.remove(self.index)
        return {'FINISHED'}


class TRANSMOGRIFIER_OT_edit_textures_add_preset(Operator):
    """Creates an Edit Textures preset from current settings"""
    bl_idname = "transmogrifier.edit_textures_add_preset"
    bl_label = "Add 'Edit Textures' Preset"

    # Captured preset name from pop-up dialog window.
    preset_name: bpy.props.StringProperty(name="Name", default="")

    def execute(self, context):
        # Set Edit Textures operator preset directory and new preset file.
        add_preset_name = f"{self.preset_name}.json"
        edit_textures_preset_dir = Path(bpy.utils.user_resource('SCRIPTS', path="presets/operator")) / "transmogrifier" / "edit_textures"
        if not Path(edit_textures_preset_dir).exists():  # Check if operator preset directory exists.
            Path(edit_textures_preset_dir).mkdir(parents=True, exist_ok=True)  # Make Edit Textures operator preset directory.
        preset_json = edit_textures_preset_dir / add_preset_name

        # Get current Edit Textures settings.
        settings_dict = Functions.get_edit_textures_settings_dict(self, context)

        # Save new Edit Textures operator preset as JSON file.
        Functions.write_json(settings_dict, preset_json)
        self.report({'INFO'}, f"Added 'Edit Textures' preset: {add_preset_name}")
        return {'FINISHED'}
    
    # Pop-up dialog window to capture new preset name.
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
    

class TRANSMOGRIFIER_OT_edit_textures_remove_preset(Operator):
    """Removes currently selected Transmogrifier preset"""
    bl_idname = "transmogrifier.edit_textures_remove_preset"
    bl_label = "Remove 'Edit Textures' Preset"

    def execute(self, context):
        # Get selected Edit Textures operator preset.
        settings = bpy.context.scene.transmogrifier_settings
        remove_preset_name = f"{settings.edit_textures_preset_enum}.json"

        # Set Edit Textures operator preset directory and preset file to be removed.
        edit_textures_preset_dir = Path(bpy.utils.user_resource('SCRIPTS', path="presets/operator")) / "transmogrifier" / "edit_textures"
        if not Path(edit_textures_preset_dir).exists():  # Check if operator preset directory exists.
            Path(edit_textures_preset_dir).mkdir(parents=True, exist_ok=True)  # Make Edit Textures operator preset directory.
        preset_json = edit_textures_preset_dir / remove_preset_name

        # Return early and report error if Edit Textures operator preset does not exist.
        if not preset_json.is_file():
            self.report({'ERROR'}, f"'Edit Textures' preset does not exist: {remove_preset_name}")
            return {'CANCELLED'}

        # Remove Edit Textures operator preset.
        self.report({'INFO'}, f"Removed 'Edit Textures' preset: {remove_preset_name}")
        Path.unlink(preset_json)
        return {'FINISHED'}


# Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), preset_manager.py, Line 124
class TRANSMOGRIFIER_OT_edit_textures_load_preset(Operator, ImportHelper):
    """Load an Edit Textures preset from a JSON file"""
    bl_idname = "transmogrifier.edit_textures_load_preset"
    bl_label = "Load 'Edit Textures' Preset"
    bl_options = {'UNDO'}

    filename_ext = '.json'

    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )

    def execute(self, context):
        settings = bpy.context.scene.transmogrifier_settings
        
        # Get filepath from browser.
        preset_src = Path(self.filepath)

        # Get preset name.
        preset_name = preset_src.name
        
        # Check if Edit Textures preset directory exists.
        edit_textures_preset_dir = Path(bpy.utils.user_resource('SCRIPTS', path="presets/operator")) / "transmogrifier" / "edit_textures"
        if not Path(edit_textures_preset_dir).exists():  # Check if operator preset directory exists.
            Path(edit_textures_preset_dir).mkdir(parents=True, exist_ok=True)  # Make Edit Texture operator preset directory.
        preset_dest = edit_textures_preset_dir / preset_name
        
        # Copy preset file to preset directory.  Overwrite existing.
        shutil.copy(preset_src, preset_dest)
        
        # Concatenate the current property assignment.
        property_assignment = f"settings.edit_textures_preset = {repr(preset_src.stem)}"

        # Make the property (key) equal to the preset (value).
        exec(property_assignment)
        
        # Load preset (Update settings and UI from preset file).
        Functions.set_texture_settings(self, context)

        self.report({'INFO'}, f"Loaded 'Edit Textures' preset: {preset_name}")
        return {'FINISHED'}


# Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), UI.py, Line 782
class TRANSMOGRIFIER_OT_add_texture(Operator):
    '''Add new texture map to UI'''

    bl_idname = "transmogrifier.add_texture"
    bl_label = "Add Texture Edit"
    bl_description = "Add a texture map to edit"

    def execute(self, context):
        new_export = context.scene.transmogrifier_textures.add()
        return {'FINISHED'}


class TRANSMOGRIFIER_OT_remove_texture(Operator):
    '''Remove texture map from UI'''

    bl_idname = "transmogrifier.remove_texture"
    bl_label = "Remove Map"
    bl_description = "Remove texture map from editing"

    index: IntProperty(
        name="Index to remove",
        description="Index of the texture to remove",
        min=0, 
    )   

    def execute(self, context):
        context.scene.transmogrifier_textures.remove(self.index)
        return {'FINISHED'}


# Adapted from Bystedts Blender Baker (GPL-3.0 License, https://3dbystedt.gumroad.com/l/JAqLT), UI.py, Line 782
class TRANSMOGRIFIER_OT_add_custom_script(Operator):
    '''Add new custom script to UI'''

    bl_idname = "transmogrifier.add_custom_script"
    bl_label = "Add Script"
    bl_description = "Add new custom script to UI"

    def execute(self, context):
        # Import Functions
        Functions.add_custom_script(self, context)
        Functions.update_custom_script_names(self, context)
        return {'FINISHED'}


class TRANSMOGRIFIER_OT_remove_custom_script(Operator):
    '''Remove custom script from UI'''

    bl_idname = "transmogrifier.remove_custom_script"
    bl_label = "Remove Custom Script"
    bl_description = "Remove custom script from UI"

    custom_script_index: IntProperty(
        name="Index to remove",
        description="Index of the custom script to remove",
        min=0, 
    )   

    def execute(self, context):
        context.scene.transmogrifier_scripts.remove(self.custom_script_index)
        Functions.update_custom_script_names(self, context)
        return {'FINISHED'}




#  ███████████   ██████████   █████████  █████  █████████  ███████████ ███████████   █████ █████
# ░░███░░░░░███ ░░███░░░░░█  ███░░░░░███░░███  ███░░░░░███░█░░░███░░░█░░███░░░░░███ ░░███ ░░███ 
#  ░███    ░███  ░███  █ ░  ███     ░░░  ░███ ░███    ░░░ ░   ░███  ░  ░███    ░███  ░░███ ███  
#  ░██████████   ░██████   ░███          ░███ ░░█████████     ░███     ░██████████    ░░█████   
#  ░███░░░░░███  ░███░░█   ░███    █████ ░███  ░░░░░░░░███    ░███     ░███░░░░░███    ░░███    
#  ░███    ░███  ░███ ░   █░░███  ░░███  ░███  ███    ░███    ░███     ░███    ░███     ░███    
#  █████   █████ ██████████ ░░█████████  █████░░█████████     █████    █████   █████    █████   
# ░░░░░   ░░░░░ ░░░░░░░░░░   ░░░░░░░░░  ░░░░░  ░░░░░░░░░     ░░░░░    ░░░░░   ░░░░░    ░░░░░    

classes = (
    TRANSMOGRIFIER_OT_help,
    TRANSMOGRIFIER_OT_transmogrify,
    TRANSMOGRIFIER_OT_forecast,
    TRANSMOGRIFIER_OT_install_presets,
    TRANSMOGRIFIER_OT_add_preset,
    TRANSMOGRIFIER_OT_remove_preset,
    TRANSMOGRIFIER_OT_load_preset,
    TRANSMOGRIFIER_OT_add_import, 
    TRANSMOGRIFIER_OT_remove_import,
    TRANSMOGRIFIER_OT_add_export, 
    TRANSMOGRIFIER_OT_remove_export, 
    TRANSMOGRIFIER_OT_edit_textures_add_preset, 
    TRANSMOGRIFIER_OT_edit_textures_remove_preset, 
    TRANSMOGRIFIER_OT_edit_textures_load_preset, 
    TRANSMOGRIFIER_OT_add_texture, 
    TRANSMOGRIFIER_OT_remove_texture, 
    TRANSMOGRIFIER_OT_add_custom_script,
    TRANSMOGRIFIER_OT_remove_custom_script,
)

# Register Classes.
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

# Unregister Classes.
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)