#!/usr/bin/env python3
"""
Password Generator (CLI + optional GUI)

Usage:
  python password_generator.py        # run CLI interactive mode
  python password_generator.py --gui  # open the Tkinter GUI
"""

import secrets
import string
import sys

# Try to import pyperclip for clipboard support; fallback to None
try:
    import pyperclip
except Exception:
    pyperclip = None

# --- Generator logic ---
AMBIGUOUS = set("O0oIl1|`'\".,;:")  # characters some users find ambiguous


def build_charset(use_lower, use_upper, use_digits, use_symbols, avoid_ambiguous):
    charset = []
    if use_lower:
        charset += list(string.ascii_lowercase)
    if use_upper:
        charset += list(string.ascii_uppercase)
    if use_digits:
        charset += list(string.digits)
    if use_symbols:
        # A conservative set of symbols (you can expand if needed)
        charset += list("!@#$%^&*()-_=+[]{}<>?/\\~")
    if avoid_ambiguous:
        charset = [c for c in charset if c not in AMBIGUOUS]
    return ''.join(sorted(set(charset)))  # deduplicate & return as string


def generate_password(length, charset):
    if not charset:
        raise ValueError("Character set is empty. Enable at least one character type.")
    # Use secrets.choice for cryptographic randomness
    return ''.join(secrets.choice(charset) for _ in range(length))


def copy_to_clipboard(text):
    if pyperclip:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            pass
    # fallback: use tkinter clipboard if available
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # now it stays on clipboard after the window is destroyed
        root.destroy()
        return True
    except Exception:
        return False


# --- Console (CLI) interface ---
def run_cli():
    print("\nSecure Password Generator (console)\n" + "-" * 36)
    try:
        length = int(input("Password length (e.g. 16): ").strip() or "16")
    except Exception:
        print("Invalid length, using 16.")
        length = 16

    def yn(prompt, default=True):
        d = "Y/n" if default else "y/N"
        val = input(f"{prompt} [{d}]: ").strip().lower()
        if val == "":
            return default
        return val in ("y", "yes")

    use_lower = yn("Include lowercase letters", True)
    use_upper = yn("Include UPPERCASE letters", True)
    use_digits = yn("Include digits (0-9)", True)
    use_symbols = yn("Include symbols (e.g. !@#...)", True)
    avoid_ambiguous = yn("Exclude ambiguous characters (O,0,l,1 etc.)", True)

    charset = build_charset(use_lower, use_upper, use_digits, use_symbols, avoid_ambiguous)
    if not charset:
        print("No characters selected. Exiting.")
        return

    try:
        count = int(input("How many passwords to generate? (1): ").strip() or "1")
    except Exception:
        count = 1

    print("\nGenerated password(s):")
    for i in range(count):
        pwd = generate_password(length, charset)
        print(f"{i+1}. {pwd}")

    if copy_to_clipboard(pwd):
        print("\n(last generated password copied to clipboard)")
    else:
        print("\nCould not copy to clipboard automatically. Install 'pyperclip' or use a GUI.")


# --- Simple Tkinter GUI ---
def run_gui():
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except Exception as e:
        print("Tkinter is not available on this system.", e)
        return

    root = tk.Tk()
    root.title("Password Generator")
    root.resizable(False, False)
    pad = 10

    frm = ttk.Frame(root, padding=pad)
    frm.grid(row=0, column=0, sticky="nsew")

    # Options
    ttk.Label(frm, text="Length:").grid(row=0, column=0, sticky="w")
    length_var = tk.IntVar(value=16)
    length_spin = ttk.Spinbox(frm, from_=4, to=128, textvariable=length_var, width=6)
    length_spin.grid(row=0, column=1, sticky="w")

    lower_var = tk.BooleanVar(value=True)
    upper_var = tk.BooleanVar(value=True)
    digits_var = tk.BooleanVar(value=True)
    symbols_var = tk.BooleanVar(value=True)
    avoid_var = tk.BooleanVar(value=True)

    ttk.Checkbutton(frm, text="Lowercase", variable=lower_var).grid(row=1, column=0, sticky="w")
    ttk.Checkbutton(frm, text="Uppercase", variable=upper_var).grid(row=1, column=1, sticky="w")
    ttk.Checkbutton(frm, text="Digits", variable=digits_var).grid(row=2, column=0, sticky="w")
    ttk.Checkbutton(frm, text="Symbols", variable=symbols_var).grid(row=2, column=1, sticky="w")
    ttk.Checkbutton(frm, text="Exclude ambiguous", variable=avoid_var).grid(row=3, column=0, columnspan=2, sticky="w")

    # Output
    output_var = tk.StringVar()
    ttk.Label(frm, text="Password:").grid(row=4, column=0, sticky="w", pady=(8, 0))
    out_entry = ttk.Entry(frm, textvariable=output_var, width=40)
    out_entry.grid(row=5, column=0, columnspan=2, pady=(0, 8))

    def on_generate():
        length = int(length_var.get())
        charset = build_charset(lower_var.get(), upper_var.get(), digits_var.get(), symbols_var.get(), avoid_var.get())
        if not charset:
            messagebox.showerror("Error", "No character types selected.")
            return
        pwd = generate_password(length, charset)
        output_var.set(pwd)

    def on_copy():
        txt = output_var.get()
        if not txt:
            messagebox.showinfo("Info", "No password to copy.")
            return
        ok = copy_to_clipboard(txt)
        if ok:
            messagebox.showinfo("Copied", "Password copied to clipboard.")
        else:
            messagebox.showwarning("Clipboard failed", "Could not copy to clipboard automatically.")

    gen_btn = ttk.Button(frm, text="Generate", command=on_generate)
    gen_btn.grid(row=6, column=0, sticky="ew", pady=(4, 0))
    copy_btn = ttk.Button(frm, text="Copy", command=on_copy)
    copy_btn.grid(row=6, column=1, sticky="ew", pady=(4, 0))

    # Quick presets
    def preset(length, lower, upper, digits, symbols, avoid):
        length_var.set(length)
        lower_var.set(lower)
        upper_var.set(upper)
        digits_var.set(digits)
        symbols_var.set(symbols)
        avoid_var.set(avoid)
        on_generate()

    ttk.Button(frm, text="Preset: 16 (strong)", command=lambda: preset(16, True, True, True, True, True)).grid(row=7, column=0, sticky="ew", pady=(8, 0))
    ttk.Button(frm, text="Preset: 12 (memorable)", command=lambda: preset(12, True, True, True, False, True)).grid(row=7, column=1, sticky="ew", pady=(8, 0))

    # Start with one password
    on_generate()
    root.mainloop()


# --- Entry point ---
if _name_ == "_main_":
    gui_flag = "--gui" in sys.argv or "-g" in sys.argv
    if gui_flag:
        run_gui()
    else:
        # Offer user a choice to open GUI from CLI
        if len(sys.argv) > 1:
            # any unknown args: show help
            print(_doc_)
            sys.exit(0)

        print("Password Generator")
        choice = input("Open GUI? (Y/n): ").strip().lower()
        if choice in ("", "y", "yes"):
            run_gui()
        else:
            run_cli()