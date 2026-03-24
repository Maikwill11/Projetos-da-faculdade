from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import mysql.connector

# ---------- Configuração de credenciais do Admin ----------
ADMIN_USERNAME = "Admincompany11@Gmail.com"
ADMIN_PASSWORD = "Corp50Comp11"

# ---------- Conexão com MySQL ----------
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sistema_clientes"
    )
    

# ---------- Funções do sistema (clientes) ----------
def add_client():
    name = entry_nome.get()
    email = entry_email.get()
    tel = entry_telefone.get()
    company = entry_empresa.get()

    if name and email and tel and company:
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients (name, email, tel, company) VALUES (%s, %s, %s, %s)",
                           (name, email, tel, company))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return
        messagebox.showinfo("Successful", "Added Client!")
        entry_nome.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_telefone.delete(0, tk.END)
        entry_empresa.delete(0, tk.END)
    else:
        messagebox.showwarning("Attention", "Please fill in all the required fields.")

def show_clients():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, tel, company FROM clients")
        resultados = cursor.fetchall()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Database error: {e}")
        return

    janela_lista = tk.Toplevel()
    janela_lista.title("List of Clients")
    janela_lista.geometry("900x600")
    janela_lista.configure(bg="#D3D3D3")

    colunas = ("id", "name", "email", "eel", "company")
    tabela = ttk.Treeview(janela_lista, columns=colunas, show="headings")
    tabela.pack(fill="both", expand=True, padx=10, pady=10)

    def ordenar(coluna):
        dados = [(tabela.set(item, coluna), item) for item in tabela.get_children()]
        try:
            if coluna == "ID":
                dados.sort(key=lambda x: int(x[0]))
            else:
                dados.sort(key=lambda x: x[0].lower())
        except Exception:
            dados.sort(key=lambda x: x[0])
        for index, (val, item) in enumerate(dados):
            tabela.move(item, '', index)

    for col in colunas:
        tabela.heading(col, text=col, command=lambda c=col: ordenar(c))
        tabela.column(col, anchor="center", width=150)

    for row in resultados:
        tabela.insert("", tk.END, values=row)

    scrollbar = ttk.Scrollbar(janela_lista, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def delete_selected():
        sel = tabela.selection()
        if not sel:
            messagebox.showwarning("Attention", "Select a client to delete.")
            return
        item = sel[0]
        values = tabela.item(item, "values")
        client_id = values[0]
        client_name = values[1]

        if messagebox.askyesno("Confirm", f"Delete client '{client_name}'?"):
            try:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
                conn.commit()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting client: {e}")
                return
            tabela.delete(item)
            messagebox.showinfo("Deleted", "Client deleted successfully.")

    btn_frame = tk.Frame(janela_lista, bg="#D3D3D3")
    btn_frame.pack(pady=8)
    btn_delete = tk.Button(btn_frame, text="Delete Selected", width=15, command=delete_selected)
    btn_delete.pack(side="left", padx=6)

    def refresh():
        for i in tabela.get_children():
            tabela.delete(i)
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, tel, company FROM clients")
            for row in cursor.fetchall():
                tabela.insert("", tk.END, values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    btn_refresh = tk.Button(btn_frame, text="Refresh", width=12, command=refresh)
    btn_refresh.pack(side="left", padx=6)

    def on_delete_key(event):
        delete_selected()
    tabela.bind("<Delete>", on_delete_key)

    def show_context(event):
        row = tabela.identify_row(event.y)
        if row:
            tabela.selection_set(row)
            menu.tk_popup(event.x_root, event.y_root)
    menu = tk.Menu(janela_lista, tearoff=0)
    menu.add_command(label="Delete", command=delete_selected)
    tabela.bind("<Button-3>", show_context)

# ---------- Search function (new) ----------
def search_clients():
    janela_busca = tk.Toplevel()
    janela_busca.title("Search Clients")
    janela_busca.geometry("900x600")
    janela_busca.configure(bg="#E8E8E8")

    frame_busca = tk.Frame(janela_busca, bg="#E8E8E8", padx=10, pady=10)
    frame_busca.pack(fill="x")

    campos = {
        "ID": tk.Entry(frame_busca, width=10),
        "Name": tk.Entry(frame_busca, width=20),
        "Email": tk.Entry(frame_busca, width=25),
        "Tel": tk.Entry(frame_busca, width=20),
        "Company": tk.Entry(frame_busca, width=20)
    }

    for i, (label, entry) in enumerate(campos.items()):
        tk.Label(frame_busca, text=label + ":", bg="#E8E8E8").grid(row=0, column=i*2, padx=4, pady=4, sticky="e")
        entry.grid(row=0, column=i*2+1, padx=4, pady=4)

    tabela = ttk.Treeview(janela_busca, columns=("ID", "Name", "Email", "Tel", "Company"), show="headings")
    for col in ("ID", "Name", "Email", "Tel", "Company"):
        tabela.heading(col, text=col)
        tabela.column(col, anchor="center", width=150)
    tabela.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(janela_busca, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def executar_busca():
        for i in tabela.get_children():
            tabela.delete(i)

        filtros = []
        valores = []

        id_val = campos["ID"].get().strip()
        if id_val:
            # if user typed a number, use exact match
            filtros.append("id = %s")
            valores.append(id_val)
        name_val = campos["Name"].get().strip()
        if name_val:
            filtros.append("name LIKE %s")
            valores.append(f"%{name_val}%")
        email_val = campos["Email"].get().strip()
        if email_val:
            filtros.append("email LIKE %s")
            valores.append(f"%{email_val}%")
        tel_val = campos["Tel"].get().strip()
        if tel_val:
            filtros.append("tel LIKE %s")
            valores.append(f"%{tel_val}%")
        company_val = campos["Company"].get().strip()
        if company_val:
            filtros.append("company LIKE %s")
            valores.append(f"%{company_val}%")

        query = "SELECT id, name, email, tel, company FROM clients"
        if filtros:
            query += " WHERE " + " AND ".join(filtros)

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(query, valores)
            resultados = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return

        for row in resultados:
            tabela.insert("", tk.END, values=row)

    btn_buscar = tk.Button(frame_busca, text="Search", command=executar_busca, width=12)
    btn_buscar.grid(row=1, column=0, columnspan=10, pady=10)

# ---------- Login and roles UI (English) ----------
def open_main_window(role, username):
    # Close login window and open main app window
    login_win.destroy()

    global janela, entry_nome, entry_email, entry_telefone, entry_empresa
    janela = tk.Tk()
    janela.title("Client Registration")
    janela.configure(bg="#B8B8B8")

    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)

    frame = tk.Frame(janela, bg="#B8B8B8", padx=20, pady=20)
    frame.grid(row=0, column=0, sticky="nsew")

    for c in range(2):
        frame.columnconfigure(c, weight=1)

    label_opts = {"bg": "#B8B8B8", "anchor": "e"}
    entry_opts = {"width": 30}

    tk.Label(frame, text=f"Logged in as: {username} ({role})", bg="#B8B8B8").grid(row=0, column=0, columnspan=2, pady=(0,12))

    tk.Label(frame, text="Name:", **label_opts).grid(row=1, column=0, padx=5, pady=8, sticky="e")
    entry_nome = tk.Entry(frame, **entry_opts)
    entry_nome.grid(row=1, column=1, padx=5, pady=8, sticky="w")

    tk.Label(frame, text="Email:", **label_opts).grid(row=2, column=0, padx=5, pady=8, sticky="e")
    entry_email = tk.Entry(frame, **entry_opts)
    entry_email.grid(row=2, column=1, padx=5, pady=8, sticky="w")

    tk.Label(frame, text="Tel:", **label_opts).grid(row=3, column=0, padx=5, pady=8, sticky="e")
    entry_telefone = tk.Entry(frame, **entry_opts)
    entry_telefone.grid(row=3, column=1, padx=5, pady=8, sticky="w")

    tk.Label(frame, text="Company:", **label_opts).grid(row=4, column=0, padx=5, pady=8, sticky="e")
    entry_empresa = tk.Entry(frame, **entry_opts)
    entry_empresa.grid(row=4, column=1, padx=5, pady=8, sticky="w")

    btn_frame = tk.Frame(frame, bg="#B8B8B8")
    btn_frame.grid(row=5, column=0, columnspan=2, pady=(12, 0))

    btn_add = tk.Button(btn_frame, text="Add", width=12, command=add_client)
    btn_add.pack(side="left", padx=8)

    btn_show = tk.Button(btn_frame, text="Show Clients", width=12, command=show_clients)
    btn_show.pack(side="left", padx=8)

    btn_search = tk.Button(btn_frame, text="Search Clients", width=14, command=search_clients)
    btn_search.pack(side="left", padx=8)

    # Role-specific control: only admin sees "Manage Employees"
    if role == "Admin":
        def manage_employees():
            messagebox.showinfo("Admin area", "This is where you manage employees (Admin only).")
        btn_manage = tk.Button(btn_frame, text="Manage Employees", width=16, command=manage_employees)
        btn_manage.pack(side="left", padx=8)

    # optional: centralize window on screen
    janela.update_idletasks()
    min_w = janela.winfo_reqwidth()
    min_h = janela.winfo_reqheight()
    janela.minsize(min_w, min_h)
    screen_w = janela.winfo_screenwidth()
    screen_h = janela.winfo_screenheight()
    x = (screen_w // 2) - (min_w // 2)
    y = (screen_h // 2) - (min_h // 2)
    janela.geometry(f"+{x}+{y}")

    # duplicate buttons at bottom (optional)
    tk.Button(janela, text="Add", command=add_client).grid(row=1, column=0, pady=10, sticky="w")
    tk.Button(janela, text="Show Clients", command=show_clients).grid(row=1, column=1, pady=10, sticky="e")

    janela.mainloop()

def attempt_login():
    username = entry_user.get().strip()
    password = entry_pass.get().strip()

    if not username or not password:
        messagebox.showwarning("Login", "Please enter username and password.")
        return

    # Admin check (hardcoded)
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        open_main_window(role="Admin", username=username)
    else:
        # For simplicity: any other credentials are accepted as "User"
        open_main_window(role="User", username=username)

# ---------- Login window creation (in English) ----------
login_win = tk.Tk()
login_win.title("Login")
login_win.geometry("360x200")
login_win.configure(bg="#f0f0f0")

tk.Label(login_win, text="Please sign in", font=("Arial", 14), bg="#f0f0f0").pack(pady=(12,6))

frm = tk.Frame(login_win, bg="#f0f0f0")
frm.pack(pady=6)

tk.Label(frm, text="Username:", bg="#f0f0f0").grid(row=0, column=0, sticky="e", padx=6, pady=6)
entry_user = tk.Entry(frm, width=30)
entry_user.grid(row=0, column=1, padx=6, pady=6)

tk.Label(frm, text="Password:", bg="#f0f0f0").grid(row=1, column=0, sticky="e", padx=6, pady=6)
entry_pass = tk.Entry(frm, width=30, show="*")
entry_pass.grid(row=1, column=1, padx=6, pady=6)

btn_login = tk.Button(login_win, text="Sign In", width=12, command=attempt_login)
btn_login.pack(pady=10)

# Allow pressing Enter to submit
login_win.bind('<Return>', lambda event: attempt_login())

login_win.mainloop()