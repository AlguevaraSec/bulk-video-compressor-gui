import json
import os
import shutil
import subprocess
import sys
import threading
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional, Tuple

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

def format_size(size_bytes: int) -> str:
    """Converts a byte count into a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"

class ResultDialog(ctk.CTkToplevel):
    """Modal dialog displaying the final results of the bulk compression process."""
    
    def __init__(self, parent: ctk.CTk, output_dir: str, original_size: int, compressed_size: int, file_count: int, file_stats: List[Dict[str, Any]]) -> None:
        super().__init__(parent)
        self.title("Compression Complete")
        self.geometry("550x500")
        self.resizable(False, False)
        
        self._center_window(parent)
        self.transient(parent)
        self.grab_set()
        
        self.output_dir = output_dir
        self.original_size = original_size
        self.compressed_size = compressed_size
        self.file_count = file_count
        self.file_stats = file_stats
        
        self._build_ui()
        
    def _center_window(self, parent: ctk.CTk) -> None:
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 550) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.geometry(f"+{x}+{y}")
        
    def _build_ui(self) -> None:
        success_label = ctk.CTkLabel(
            self, text="🎉 All Videos Processed!", 
            font=ctk.CTkFont(size=20, weight="bold"), 
            text_color="#2FA572"
        )
        success_label.pack(pady=(20, 15))
        
        stats_frame = ctk.CTkFrame(self, corner_radius=10)
        stats_frame.pack(fill="x", padx=25, pady=(0, 15))
        stats_frame.columnconfigure((0, 1), weight=1)
        
        orig_str = format_size(self.original_size)
        comp_str = format_size(self.compressed_size)
        saved_bytes = self.original_size - self.compressed_size
        saved_str = format_size(max(0, saved_bytes))
        savings_pct = (saved_bytes / self.original_size) * 100 if self.original_size > 0 else 0
        
        lbl_style = ctk.CTkFont(size=13, weight="normal")
        val_style = ctk.CTkFont(size=14, weight="bold")
        
        ctk.CTkLabel(stats_frame, text="Files Processed:", font=lbl_style).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=str(self.file_count), font=val_style).grid(row=0, column=1, sticky="e", padx=20, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Total Original Size:", font=lbl_style).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=orig_str, font=val_style).grid(row=1, column=1, sticky="e", padx=20, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Total Compressed Size:", font=lbl_style).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=comp_str, font=val_style, text_color="#3B8ED0").grid(row=2, column=1, sticky="e", padx=20, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Total Reduction:", font=lbl_style).grid(row=3, column=0, sticky="w", padx=20, pady=10)
        
        savings_text = f"{saved_str} (-{savings_pct:.1f}%)" if saved_bytes > 0 else "0 B (0%)"
        savings_color = "#2FA572" if saved_bytes > 0 else "gray"
        ctk.CTkLabel(stats_frame, text=savings_text, font=val_style, text_color=savings_color).grid(row=3, column=1, sticky="e", padx=20, pady=10)

        list_frame = ctk.CTkScrollableFrame(self, height=130, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        for stat in self.file_stats:
            orig = format_size(stat["orig"])
            comp = format_size(stat["comp"])
            row = ctk.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=stat["name"], font=ctk.CTkFont(weight="bold", size=11)).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{orig} ➔ {comp}", text_color="#3B8ED0", font=ctk.CTkFont(size=11)).pack(side="right", padx=5)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        ctk.CTkButton(btn_frame, text="Open Output Folder", command=self._show_in_folder).pack(side="left", padx=(0, 10), expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Close", width=100, fg_color="gray", hover_color="#555555", command=self.destroy).pack(side="right")
            
    def _show_in_folder(self) -> None:
        try:
            clean_path = os.path.normpath(self.output_dir)
            subprocess.run(f'explorer "{clean_path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not locate folder: {e}")

class TkinterDnD_CTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class VideoCompressorApp(TkinterDnD_CTk):
    """Main application class for the Guevara Bulk Video Compressor."""
    
    def __init__(self) -> None:
        super().__init__()
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.title("Guevara Videos Compressor")
        self.geometry("700x900")
        self.minsize(700, 900)
        
        self.input_files: List[str] = []
        self.queue_ui_elements: Dict[str, ctk.CTkLabel] = {}
        self.output_dir = ctk.StringVar()
        self.prefix_var = ctk.StringVar(value="compressed_")
        self.is_processing = False
        
        self._build_main_ui()
        self.after(100, self._verify_dependencies)
        
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._handle_drop_inputs)

    def _build_main_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 
        
        ctk.CTkLabel(self, text="Guevara Bulk Video Compressor", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(20, 10))
        
        self.main_container = ctk.CTkScrollableFrame(self)
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        self._build_input_queue_section()
        self._build_output_section()
        self._build_settings_section()
        self._build_crf_section()
        self._build_action_section()

    def _build_input_queue_section(self) -> None:
        self.input_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.input_frame.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(header_frame, text="1. Select Videos (Drag & Drop Supported)", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="+ Add Videos", font=ctk.CTkFont(weight="bold"), command=self._handle_browse_inputs).pack(side="right")

        self.queue_frame = ctk.CTkScrollableFrame(self.input_frame, height=150, corner_radius=5)
        self.queue_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.queue_frame.grid_columnconfigure(0, weight=1)
        
        self.empty_queue_label = ctk.CTkLabel(self.queue_frame, text="Drag & drop videos here, or click 'Add Videos'", text_color="gray", font=ctk.CTkFont(slant="italic"))
        self.empty_queue_label.grid(row=0, column=0, pady=50)

    def _build_output_section(self) -> None:
        self.output_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.output_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(self.output_frame, text="2. Output Destination", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        dir_row = ctk.CTkFrame(self.output_frame, fg_color="transparent")
        dir_row.pack(fill="x", padx=15, pady=5)
        
        self.dir_entry = ctk.CTkEntry(dir_row, textvariable=self.output_dir, placeholder_text="Folder will default to the original video's location...", state="disabled")
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(dir_row, text="Change Folder", width=120, command=self._handle_browse_output).pack(side="right")

        prefix_row = ctk.CTkFrame(self.output_frame, fg_color="transparent")
        prefix_row.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(prefix_row, text="Filename Prefix:").pack(side="left", padx=(0, 10))
        ctk.CTkEntry(prefix_row, textvariable=self.prefix_var, width=150, placeholder_text="e.g. compressed_").pack(side="left")

    def _build_settings_section(self) -> None:
        self.settings_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.settings_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(self.settings_frame, text="3. Encoding Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        grid_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=15, pady=(0, 15))
        grid_frame.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(grid_frame, text="Target Resolution:").grid(row=0, column=0, sticky="w", pady=5)
        self.res_combo = ctk.CTkComboBox(grid_frame, values=["Original", "1080p (1920x1080)", "720p (1280x720)", "480p (854x480)"], state="readonly")
        self.res_combo.set("Original")
        self.res_combo.grid(row=0, column=1, sticky="e", pady=5)

        ctk.CTkLabel(grid_frame, text="Target Framerate:").grid(row=1, column=0, sticky="w", pady=5)
        self.fps_combo = ctk.CTkComboBox(grid_frame, values=["Original", "240", "120", "60", "30", "24"], state="readonly")
        self.fps_combo.set("Original")
        self.fps_combo.grid(row=1, column=1, sticky="e", pady=5)

        ctk.CTkLabel(grid_frame, text="Video Codec:").grid(row=2, column=0, sticky="w", pady=5)
        self.codec_combo = ctk.CTkComboBox(grid_frame, values=["libx265 (HEVC - Best Compression)", "libx264 (H.264 - Best Compatibility)"], state="readonly")
        self.codec_combo.set("libx265 (HEVC - Best Compression)")
        self.codec_combo.grid(row=2, column=1, sticky="e", pady=5)

        ctk.CTkLabel(grid_frame, text="Encoding Speed:").grid(row=3, column=0, sticky="w", pady=5)
        self.preset_combo = ctk.CTkComboBox(grid_frame, values=["medium (Default - Slow)", "fast", "veryfast (Recommended)", "superfast", "ultrafast (Fastest)"], state="readonly")
        self.preset_combo.set("veryfast (Recommended)")
        self.preset_combo.grid(row=3, column=1, sticky="e", pady=5)

    def _build_crf_section(self) -> None:
        self.crf_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.crf_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(self.crf_frame, text="Compression Level (CRF)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 0))
        ctk.CTkLabel(self.crf_frame, text="Higher number = Smaller file size (Lower quality)", text_color="gray", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
        
        self.crf_val_label = ctk.CTkLabel(self.crf_frame, text="28", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3B8ED0")
        self.crf_val_label.pack(pady=(10, 0))

        self.crf_slider = ctk.CTkSlider(self.crf_frame, from_=18, to=35, number_of_steps=17, command=self._update_crf_display)
        self.crf_slider.set(28) 
        self.crf_slider.pack(fill="x", padx=20, pady=(5, 20))

    def _build_action_section(self) -> None:
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.action_frame.grid_columnconfigure(0, weight=1)

        self.start_btn = ctk.CTkButton(self.action_frame, text="Start Bulk Compression", height=45, font=ctk.CTkFont(size=15, weight="bold"), command=self._initiate_compression)
        self.start_btn.grid(row=0, column=0, sticky="ew", pady=(10, 10))

        self.overall_progress = ctk.CTkProgressBar(self.action_frame, mode="determinate", height=8)
        self.overall_progress.set(0)
        
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(self.action_frame, textvariable=self.status_var, text_color="gray", font=ctk.CTkFont(slant="italic"))
        self.status_label.grid(row=2, column=0, pady=5)

    def _update_crf_display(self, value: float) -> None:
        self.crf_val_label.configure(text=str(int(value)))

    def _verify_dependencies(self) -> None:
        if shutil.which("ffmpeg") and shutil.which("ffprobe"):
            self.status_var.set("Ready (System FFmpeg detected)")
            return
            
        try:
            import static_ffmpeg
            static_ffmpeg.add_paths()
            self.status_var.set("Ready (static-ffmpeg detected)")
            return
        except ImportError:
            pass
            
        self.status_var.set("FFmpeg not found!")
        
        confirm = messagebox.askyesno(
            "FFmpeg Required",
            "FFmpeg was not found on your system.\n\n"
            "Would you like Guevara Videos Compressor to automatically download and install "
            "'static-ffmpeg' now via pip?"
        )
        
        if confirm:
            self._install_ffmpeg_async()
        else:
            messagebox.showwarning("FFmpeg Missing", "Please install FFmpeg manually or restart the app to install automatically.")

    def _install_ffmpeg_async(self) -> None:
        self.status_var.set("Installing static-ffmpeg... Please wait.")
        self.start_btn.configure(state="disabled", text="Installing dependency...")
        self.overall_progress.grid(row=1, column=0, sticky="ew", pady=5)
        self.overall_progress.configure(mode="indeterminate")
        self.overall_progress.start()
        
        threading.Thread(target=self._execute_ffmpeg_installation, daemon=True).start()

    def _execute_ffmpeg_installation(self) -> None:
        try:
            process = subprocess.run([sys.executable, "-m", "pip", "install", "static-ffmpeg>=2.5"], capture_output=True, text=True)
            if process.returncode == 0:
                import static_ffmpeg
                static_ffmpeg.add_paths()
                self.after(0, lambda: self.status_var.set("Ready (static-ffmpeg installed)"))
            else:
                self.after(0, lambda: messagebox.showerror("Installation Failed", f"Could not install static-ffmpeg:\n{process.stderr}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Installation error:\n{str(e)}"))
        finally:
            self.after(0, self._reset_ui_state)

    def _handle_drop_inputs(self, event) -> None:
        files = self.tk.splitlist(event.data)
        valid_exts = ('.mp4', '.mov', '.avi', '.mkv')
        valid_files = [f for f in files if f.lower().endswith(valid_exts)]
        if valid_files:
            self._add_to_queue(valid_files)

    def _handle_browse_inputs(self) -> None:
        filenames = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")])
        if filenames:
            self._add_to_queue(list(filenames))

    def _add_to_queue(self, filenames: List[str]) -> None:
        for widget in self.queue_frame.winfo_children():
            widget.destroy()
            
        self.input_files = filenames
        self.queue_ui_elements.clear()
        
        for idx, file_path in enumerate(self.input_files):
            filename = os.path.basename(file_path)
            size_str = format_size(os.path.getsize(file_path))
            
            row_frame = ctk.CTkFrame(self.queue_frame, fg_color="transparent")
            row_frame.grid(row=idx, column=0, sticky="ew", pady=2, padx=5)
            row_frame.grid_columnconfigure(0, weight=1)
            
            file_lbl = ctk.CTkLabel(row_frame, text=f"⏱️ {filename} ({size_str})", anchor="w")
            file_lbl.grid(row=0, column=0, sticky="ew")
            
            status_lbl = ctk.CTkLabel(row_frame, text="Pending", text_color="gray", width=120, anchor="e")
            status_lbl.grid(row=0, column=1, sticky="e")
            
            self.queue_ui_elements[file_path] = status_lbl

        if not self.output_dir.get():
            self.output_dir.set(os.path.dirname(self.input_files[0]))
            self.dir_entry.configure(state="normal")
            
        self.status_var.set(f"Loaded {len(self.input_files)} videos into the queue.")

    def _handle_browse_output(self) -> None:
        directory = filedialog.askdirectory(title="Select Output Folder")
        if directory:
            self.output_dir.set(directory)
            self.dir_entry.configure(state="normal")

    def _get_video_metadata(self, filename: str) -> Tuple[int, int, float]:
        """Analyzes a single video file to retrieve dimensions and framerate."""
        try:
            cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'json', filename]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            if 'streams' in info and info['streams']:
                stream = info['streams'][0]
                width = int(stream.get('width', 0))
                height = int(stream.get('height', 0))
                
                fps_str = stream.get('r_frame_rate', '0/1')
                num, den = map(int, fps_str.split('/'))
                fps = num / den if den != 0 else 0
                return width, height, fps
        except Exception:
            pass
        return 0, 0, 0.0

    def _initiate_compression(self) -> None:
        if self.is_processing:
            return
            
        if not self.input_files:
            messagebox.showerror("Error", "Please add videos to the queue first.")
            return

        out_dir = self.output_dir.get()
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {e}")
                return

        self.is_processing = True
        self.start_btn.configure(state="disabled", text="Compressing...")
        
        self.overall_progress.grid(row=1, column=0, sticky="ew", pady=5)
        self.overall_progress.configure(mode="determinate")
        self.overall_progress.set(0)
        
        for path, label in self.queue_ui_elements.items():
            label.configure(text="Pending", text_color="gray")
        
        threading.Thread(target=self._execute_bulk_compression, args=(out_dir,), daemon=True).start()

    def _update_queue_item_ui(self, file_path: str, status_text: str, color: str) -> None:
        """Safely updates a specific item's status label from a background thread."""
        if file_path in self.queue_ui_elements:
            lbl = self.queue_ui_elements[file_path]
            self.after(0, lambda l=lbl, t=status_text, c=color: l.configure(text=t, text_color=c))

    def _execute_bulk_compression(self, out_dir: str) -> None:
        total_files = len(self.input_files)
        total_orig_size = 0
        total_comp_size = 0
        successful_files = 0
        file_stats = []
        
        codec_choice = "libx265" if "libx265" in self.codec_combo.get() else "libx264"
        preset_choice = self.preset_combo.get().split()[0]
        crf_value = str(int(self.crf_slider.get()))
        prefix = self.prefix_var.get()
        res_choice = self.res_combo.get()
        fps_choice = self.fps_combo.get()

        for idx, input_path in enumerate(self.input_files):
            filename = os.path.basename(input_path)
            
            try:
                self.after(0, lambda i=idx: self.status_var.set(f"Processing ({i+1}/{total_files})..."))
                self._update_queue_item_ui(input_path, "Processing...", "#3B8ED0")

                output_filename = f"{prefix}{filename}"
                output_path = os.path.join(out_dir, output_filename)
                
                orig_width, orig_height, orig_fps = self._get_video_metadata(input_path)
                cmd = ['ffmpeg', '-y', '-i', input_path]

                scale_filter: Optional[str] = None
                if "1080p" in res_choice and orig_height > 1080: scale_filter = "scale=-2:1080"
                elif "720p" in res_choice and orig_height > 720: scale_filter = "scale=-2:720"
                elif "480p" in res_choice and orig_height > 480: scale_filter = "scale=-2:480"
                if scale_filter: cmd.extend(['-vf', scale_filter])

                if fps_choice != "Original":
                    try:
                        target_fps = int(fps_choice)
                        if orig_fps == 0 or target_fps < (orig_fps + 2):
                            cmd.extend(['-r', fps_choice])
                    except ValueError:
                        pass

                cmd.extend(['-c:v', codec_choice, '-crf', crf_value, '-preset', preset_choice, '-c:a', 'aac', '-b:a', '128k', output_path])

                process = subprocess.run(cmd, capture_output=True, text=True)
                
                if process.returncode == 0:
                    orig_size = os.path.getsize(input_path)
                    comp_size = os.path.getsize(output_path)
                    total_orig_size += orig_size
                    total_comp_size += comp_size
                    successful_files += 1
                    file_stats.append({"name": filename, "orig": orig_size, "comp": comp_size})
                    
                    saved_mb = (orig_size - comp_size) / (1024 * 1024)
                    self._update_queue_item_ui(input_path, f"Done (Saved {saved_mb:.1f}MB)", "#2FA572")
                else:
                    self._update_queue_item_ui(input_path, "Failed", "#D35B58")
                    
            except Exception as e:
                self._update_queue_item_ui(input_path, "Error", "#D35B58")

            self.after(0, lambda i=idx+1, t=total_files: self.overall_progress.set(i / t))

        self.after(0, self._reset_ui_state)
        
        if successful_files > 0:
            self.after(0, lambda: self.status_var.set("All tasks complete."))
            self.after(0, lambda: ResultDialog(self, out_dir, total_orig_size, total_comp_size, successful_files, file_stats))
        else:
            self.after(0, lambda: self.status_var.set("Compression failed for all files."))
            self.after(0, lambda: messagebox.showerror("Error", "No files were compressed successfully."))

    def _reset_ui_state(self) -> None:
        self.is_processing = False
        self.start_btn.configure(state="normal", text="Start Bulk Compression")
        
        try:
            self.overall_progress.stop()
        except Exception:
            pass
            
        self.overall_progress.set(1)

if __name__ == "__main__":
    app = VideoCompressorApp()
    app.mainloop()