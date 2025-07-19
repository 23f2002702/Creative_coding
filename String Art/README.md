# 🧵 String Art Generator — Command Line Tool

**Recreate stunning string art automatically using Python!**

This project generates beautiful string art by looping a single thread around nails placed along a circle’s perimeter — all using a simple algorithm that matches an input image.

---

## 📸 How It Works

1. **Input:**  
   - Provide an image (`Hehe.jpg` in this case).
   - The script converts it to grayscale and resizes it to a square.

2. **Nail Layout:**  
   - Nails are placed evenly along the perimeter of a circle.
   - You control the nail density with `NAIL_STEP`.

3. **String Algorithm:**  
   - The script finds the next best nail to pull the thread to — maximizing how well the string matches the original image.
   - It repeats this for a set number of pulls (e.g. 4000).
   - After every 50 pulls, it saves a progress snapshot.

4. **Output:**  
   - **Automatic unique output folders:**  
     Each run creates a new `Output`, `Output_1`, `Output_2`, ... folder so previous results are never overwritten.
   - Final string art image (`Final.jpg`).
   - A `thread_sequence.txt` file with:
     - Estimated total thread length.
     - Total unique nails used.
     - The exact nail pull sequence.

---

## ✅ Features

- Hardcoded input/output paths for easy testing.
- **Auto-creates unique `Output` folders** for each run.
- Saves all snapshots every `SNAPSHOT_INTERVAL` pulls.
- Prints useful progress in the console.
- Compatible with any image size (will be cropped to square automatically).

---

## 🗂 File Structure

```plaintext
StringArt/
├── String_Art.py         # Main script (this code)
├── input.jpg             # Your input image (example)
└── Output/               # First run output
    ├── Final.jpg
    ├── thread_sequence.txt
    ├── 50.jpg
    ├── 100.jpg
    ├── ...

└── Output_1/             # Second run output
    ├── Final.jpg
    ├── thread_sequence.txt
    ├── 50.jpg
    ├── ...
```
---

## 🧵 Real-Life Build

The final `thread_sequence.txt` will help you replicate the art physically.

Total unique nails used and estimated thread length are provided for planning your wooden board and thread.

---

## 📌 Author

**Shilajit Mukherjee — IITM Data Science Student, AI/ML Enthusiast**

## 📜 License

MIT License — do whatever you like, but mention the source if you share it. ❤️
