@@
 def play_mp3(self, file_path):
@@
     def show_ai_chat_window(self):
-        win = Toplevel(self.root)
-        win.title("Ask Kinito (AI)")
-        win.geometry("400x200")
-        tk.Label(win, text="Ask me anything:").pack(pady=6)
-        entry = tk.Entry(win, width=60)
-        entry.pack(pady=6)
-        result = tk.Text(win, height=6, width=48)
-        result.pack(pady=6)
-
-        def submit():
-            prompt = entry.get().strip()
-            if not prompt:
-                return
-            # Simple local "AI" that echoes and adds a friendly reply.
-            reply = f"You asked: {prompt}\nI'm still learning — here's a helpful tip: try to be specific about what you want."
-            result.delete('1.0', tk.END)
-            result.insert(tk.END, reply)
-            self.speak(reply)
-
-        tk.Button(win, text="Send", command=submit).pack(pady=4)
+        # AI chat window that uses Ollama (local server) to query qwen-3-0.6b
+        win = Toplevel(self.root)
+        win.title("Ask Kinito (AI)")
+        win.geometry("500x300")
+        tk.Label(win, text="Ask me anything:").pack(pady=6)
+        entry = tk.Entry(win, width=64)
+        entry.pack(pady=6)
+        result = tk.Text(win, height=10, width=60)
+        result.pack(pady=6)
+
+        def call_ollama(prompt):
+            host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
+            model = os.environ.get("OLLAMA_MODEL", "qwen-3-0.6b")
+            url = host.rstrip("/") + "/api/generate"
+            payload = {
+                "model": model,
+                "prompt": prompt,
+                "max_tokens": 512,
+                "temperature": 0.2
+            }
+            try:
+                resp = requests.post(url, json=payload, timeout=60)
+                resp.raise_for_status()
+                data = resp.json()
+                # Try common response shapes
+                if isinstance(data, dict):
+                    # Ollama may return a top-level 'output' or 'results' list depending on version
+                    if "results" in data and isinstance(data["results"], list) and data["results"]:
+                        first = data["results"][0]
+                        if isinstance(first, dict) and "content" in first:
+                            return first["content"].strip()
+                    if "output" in data and isinstance(data["output"], str):
+                        return data["output"].strip()
+                    if "text" in data and isinstance(data["text"], str):
+                        return data["text"].strip()
+                # Fallback to raw text
+                return resp.text[:4000]
+            except Exception as e:
+                raise
+
+        def submit():
+            prompt = entry.get().strip()
+            if not prompt:
+                return
+            result.delete('1.0', tk.END)
+            result.insert(tk.END, "Thinking...\n")
+
+            def do_call():
+                try:
+                    reply = call_ollama(prompt)
+                except Exception as e:
+                    reply = f"Ollama error: {e}.\nMake sure Ollama is running and qwen-3-0.6b is available at OLLAMA_HOST."
+
+                def update_ui():
+                    result.delete('1.0', tk.END)
+                    result.insert(tk.END, reply)
+                    self.speak(reply)
+
+                self.root.after(0, update_ui)
+
+            threading.Thread(target=do_call, daemon=True).start()
+
+        tk.Button(win, text="Send", command=submit).pack(pady=4)
+        entry.bind('<Return>', lambda ev: submit())
@@
 def main():
     root = tk.Tk()
     app = FloatingAssistant(root, sprite_path_moving)
     root.mainloop()
