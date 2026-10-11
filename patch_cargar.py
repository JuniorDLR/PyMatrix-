with open("src/ui/matrix_ops_view.py", "r", encoding="utf-8") as f:
    content = f.read()

old_code = """        if tab_id == "ops":"""

new_code = """        try:
            if tab_id == "ops":"""

content = content.replace(old_code, new_code)

old_end = """        popup.destroy()"""

new_end = """        except Exception as e:
            import traceback
            err = traceback.format_exc()
            print("CRASH IN LOAD:", err)
            try:
                self._log_ops(f"CRASH IN LOAD: {e}\\n{err}", limpiar=False)
            except:
                pass
        popup.destroy()"""

content = content.replace(old_end, new_end)

with open("src/ui/matrix_ops_view.py", "w", encoding="utf-8") as f:
    f.write(content)
