# 🎬 Guevara Bulk Video Compressor

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-2FA572?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![FFmpeg](https://img.shields.io/badge/Powered_by-FFmpeg-green?style=for-the-badge)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

### 🚀 Modern Batch Video Compression Made Simple

*A sleek, lightning-fast desktop application for compressing multiple videos with a beautiful interface powered by FFmpeg.*

<img src="https://i.ibb.co/WWGdmKSk/Screenshot-2026-06-28-035726.png" width="100%" alt="Guevara Bulk Video Compressor"/>

</div>

---

# ✨ Features

## 📦 Batch Compression

* Compress multiple videos in one operation
* Queue management with live status updates
* Sequential processing for maximum stability
* Automatic output filename generation

---

## 🎬 Video Compression

* 🎥 H.265 (HEVC) support
* 🎥 H.264 (AVC) support
* 📉 Adjustable CRF quality slider
* ⚡ Multiple encoding presets
* 📺 Resolution scaling
* 🎞 FPS conversion
* 🔊 AAC audio encoding

---

## 🎨 Modern User Interface

* Beautiful CustomTkinter design
* Dark & Light mode support
* Easy-to-use controls
* Live compression progress
* Compression summary dialog
* Output folder shortcut

---

## ⚙ Smart Features

* Automatic FFmpeg detection
* Automatic static-ffmpeg installation
* Human-readable file sizes
* Storage savings statistics
* Compression percentage calculation
* Output filename prefix customization

---

# 📸 Screenshot

<div align="center">

<img src="https://i.ibb.co/WWGdmKSk/Screenshot-2026-06-28-035726.png" width="100%">

</div>

---

# 🚀 Installation

## Clone the repository

```bash
git clone https://github.com/AlguevaraSec/bulk-video-compressor-gui.git

cd bulk-video-compressor-gui
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Launch the application

```bash
python main.py
```

---

# 📂 Supported Formats

## Input

* MP4
* MKV
* MOV
* AVI

## Output

* MP4

---

# 💻 Usage

## 1️⃣ Add Videos

Click **Add Videos** and select one or more files to create a compression queue.

---

## 2️⃣ Choose Output Folder

The application automatically uses the original video's directory.

You can also choose another destination folder and customize the filename prefix.

Example:

```
compressed_video.mp4
compressed_movie.mp4
compressed_clip.mp4
```

---

## 3️⃣ Configure Compression

Select:

* Resolution
* Frame Rate
* Codec
* Encoding Speed
* Compression Level (CRF)

Recommended settings:

| Setting    | Recommendation |
| ---------- | -------------- |
| Codec      | HEVC (libx265) |
| CRF        | 28             |
| Preset     | veryfast       |
| Resolution | Original       |

---

## 4️⃣ Start Compression

Click **Start Bulk Compression**.

The application automatically:

* Processes every video
* Updates the queue
* Shows progress
* Displays storage savings when finished

---

# 📊 Compression Summary

After completion you'll see:

* ✅ Files Processed
* 💾 Original Size
* 📦 Compressed Size
* 📉 Space Saved
* 📊 Compression Percentage

---

# ⚡ Automatic FFmpeg Installation

If FFmpeg is not installed, the application automatically detects the missing dependency and offers to install **static-ffmpeg**.

No manual setup is required.

---

# 🛠 Built With

* Python
* CustomTkinter
* FFmpeg
* FFprobe
* static-ffmpeg
* threading
* subprocess
* JSON

---

# 🎯 Why Guevara Bulk Video Compressor?

Unlike many outdated FFmpeg frontends, this project focuses on simplicity and productivity.

* 🚀 Modern interface
* ⚡ Fast workflow
* 🎬 Batch processing
* 📦 High compression ratio
* 💾 Significant storage savings
* 🖥 Native desktop experience
* 🔧 Automatic dependency installation
* 🔧 Bulk videos support
---

# 📈 Roadmap

* ✅ Batch compression
* ✅ Queue management
* ✅ HEVC support
* ✅ Compression statistics
* ✅ Automatic FFmpeg installation
* ✅ Resolution presets
* ✅ FPS presets
* ✅ Drag & Drop support

---

# 🤝 Contributing

Contributions, bug reports, feature requests, and pull requests are always welcome.

If you find this project useful, consider giving it a ⭐ on GitHub.

---

# 📄 License

This project is licensed under the **MIT License**.

See the **LICENSE** file for more information.

---

<div align="center">

## 🚀 Made by AlguevaraSec

**Modern • Fast • Lightweight**

⭐ If you like this project, don't forget to star the repository.

</div>
