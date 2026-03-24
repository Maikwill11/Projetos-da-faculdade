#importações
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import platform
import datetime
import threading
import time #tempo
from tkinter import messagebox 



class ProtótipoFirewall:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥Firewall🔥")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e1e")

        self.os_name = platform.system()
        self.blocked_ips = []
        self.restricted_ports = []  # portas bloqueadas (ex: 21, 22, 80)
        self.monitorando = False

        # === DETECÇÃO DE SO ===
        self.label_os = tk.Label(self.root, text=f"Sistema detectado: {self.os_name} | Execute como ADMINISTRADOR/ROOT!", 
                                 fg="yellow", bg="#1e1e1e", font=("Arial", 10, "bold"))
        self.label_os.pack(pady=5)

        # === NOTEBOOK (Abas) ===
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Aba 1: Bloquear IPs
        aba_ips = ttk.Frame(notebook)
        notebook.add(aba_ips, text="🚫 Bloquear IPs")

        tk.Label(aba_ips, text="IP a bloquear (ex: 192.168.1.100):", font=("Arial", 11)).pack(pady=5)
        self.entry_ip = tk.Entry(aba_ips, width=40, font=("Arial", 12))
        self.entry_ip.pack()

        btn_frame = tk.Frame(aba_ips)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="➕ Adicionar IP", bg="#00cc00", fg="white", command=self.adicionar_ip).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Remover Selecionado", bg="#ff4444", fg="white", command=self.remover_ip).pack(side="left", padx=5)

        self.list_ips = tk.Listbox(aba_ips, height=8, font=("Arial", 11), bg="#2d2d2d", fg="white")
        self.list_ips.pack(fill="x", padx=10)

        # Aba 2: Restringir Portas
        aba_portas = ttk.Frame(notebook)
        notebook.add(aba_portas, text="🚪 Restringir Portas")

        tk.Label(aba_portas, text="Porta a bloquear (ex: 22 para SSH, 21 para FTP):", font=("Arial", 11)).pack(pady=5)
        self.entry_porta = tk.Entry(aba_portas, width=20, font=("Arial", 12))
        self.entry_porta.pack()

        btn_frame_porta = tk.Frame(aba_portas)
        btn_frame_porta.pack(pady=10)
        tk.Button(btn_frame_porta, text="➕ Bloquear Porta", bg="#00cc00", fg="white", command=self.adicionar_porta).pack(side="left", padx=5)
        tk.Button(btn_frame_porta, text="🗑 Remover Selecionado", bg="#ff4444", fg="white", command=self.remover_porta).pack(side="left", padx=5)

        self.list_portas = tk.Listbox(aba_portas, height=8, font=("Arial", 11), bg="#2d2d2d", fg="white")
        self.list_portas.pack(fill="x", padx=10)

        # Aba 3: Aplicar Regras + Logs
        aba_logs = ttk.Frame(notebook)
        notebook.add(aba_logs, text="📋 Aplicar Regras + Logs")

        tk.Button(aba_logs, text="🔥 APLICAR TODAS AS REGRAS AGORA", bg="#ff8800", fg="white", 
                  font=("Arial", 12, "bold"), command=self.aplicar_regras).pack(pady=15)

        # Área de Logs (scrollable)
        tk.Label(aba_logs, text="LOG DE CONEXÕES SUSPEITAS:", fg="cyan", bg="#1e1e1e").pack(anchor="w", padx=10)
        self.log_text = scrolledtext.ScrolledText(aba_logs, height=18, font=("Consolas", 10), bg="#0d0d0d", fg="#00ff00")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Botões de monitoramento e simulação
        btn_monitor_frame = tk.Frame(aba_logs)
        btn_monitor_frame.pack(pady=8)
        self.btn_monitor = tk.Button(btn_monitor_frame, text="▶️ Iniciar Monitoramento", bg="#00aa00", fg="white",
                                     command=self.toggle_monitoramento)
        self.btn_monitor.pack(side="left", padx=5)
        tk.Button(btn_monitor_frame, text="🧪 Simular Conexão Suspeita", bg="#aa00aa", fg="white",
                  command=self.simular_conexao).pack(side="left", padx=5)
        tk.Button(btn_monitor_frame, text="🧹 Limpar Logs", bg="#444444", fg="white", command=self.limpar_logs).pack(side="left", padx=5)

        # Rodapé
        tk.Label(self.root, text="Protótipo educacional • Linux = iptables | Windows = netsh advfirewall • Não use em produção sem testes!", 
                 fg="#888888", bg="#1e1e1e").pack(side="bottom", pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.fechar)
        self.root.mainloop()

    # ==================== FUNÇÕES DE REGRAS ====================
    def adicionar_ip(self):
        ip = self.entry_ip.get().strip()
        if ip and ip not in self.blocked_ips:
            self.blocked_ips.append(ip)
            self.list_ips.insert("end", ip)
            self.entry_ip.delete(0, tk.END)
            self.log(f"✅ IP {ip} adicionado à lista de bloqueio")

    def remover_ip(self):
        try:
            sel = self.list_ips.curselection()[0]
            ip = self.list_ips.get(sel)
            self.blocked_ips.remove(ip)
            self.list_ips.delete(sel)
            self.log(f"🗑 IP {ip} removido")
        except:
            pass

    def adicionar_porta(self):
        porta = self.entry_porta.get().strip()
        if porta.isdigit() and porta not in self.restricted_ports:
            self.restricted_ports.append(porta)
            self.list_portas.insert("end", f"Porta {porta}")
            self.entry_porta.delete(0, tk.END)
            self.log(f"✅ Porta {porta} adicionada para bloqueio")

    def remover_porta(self):
        try:
            sel = self.list_portas.curselection()[0]
            porta_txt = self.list_portas.get(sel)
            porta = porta_txt.split()[-1]
            self.restricted_ports.remove(porta)
            self.list_portas.delete(sel)
            self.log(f"🗑 Porta {porta} removida")
        except:
            pass

    # ==================== APLICAR REGRAS NO FIREWALL ====================
    def aplicar_regras(self):
        if not self.blocked_ips and not self.restricted_ports:
            messagebox.showwarning("Aviso", "Nenhuma regra para aplicar!")
            return

        try:
            if self.os_name == "Linux":
                # iptables (precisa de sudo)
                for ip in self.blocked_ips:
                    subprocess.run(f"sudo iptables -A INPUT -s {ip} -j DROP", shell=True, check=True)
                for porta in self.restricted_ports:
                    subprocess.run(f"sudo iptables -A INPUT -p tcp --dport {porta} -j DROP", shell=True, check=True)
                self.log("🔥 Regras aplicadas com iptables (Linux)")

            elif self.os_name == "Windows":
                # netsh advfirewall
                for ip in self.blocked_ips:
                    subprocess.run(f'netsh advfirewall firewall add rule name="Block_{ip}" dir=in action=block remoteip={ip}', 
                                   shell=True, check=True)
                for porta in self.restricted_ports:
                    subprocess.run(f'netsh advfirewall firewall add rule name="BlockPort_{porta}" dir=in action=block protocol=TCP localport={porta}', 
                                   shell=True, check=True)
                self.log("🔥 Regras aplicadas com netsh (Windows)")

            else:
                self.log("⚠️ Sistema não suportado para regras automáticas")
                return

            messagebox.showinfo("Sucesso", "Regras aplicadas com sucesso!\n\nVerifique com:\nLinux: sudo iptables -L\nWindows: netsh advfirewall show rule name=all")
        except subprocess.CalledProcessError:
            messagebox.showerror("Erro", "Falha ao aplicar regras!\n\nExecute o programa como ADMINISTRADOR/ROOT.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ==================== LOGS ====================
    def log(self, texto):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {texto}\n")
        self.log_text.see(tk.END)

    def limpar_logs(self):
        self.log_text.delete(1.0, tk.END)

    # ==================== SIMULAR CONEXÃO SUSPEITA ====================
    def simular_conexao(self):
        ip = "192.168.1.50" if not self.blocked_ips else self.blocked_ips[0]
        porta = "22" if not self.restricted_ports else self.restricted_ports[0]
        if ip in self.blocked_ips or porta in self.restricted_ports:
            self.log(f"🚨 CONEXÃO SUSPEITA BLOQUEADA → IP: {ip} | Porta: {porta}")
        else:
            self.log(f"⚠️ Conexão suspeita detectada → IP: {ip} | Porta: {porta} (não bloqueada)")

    # ==================== MONITORAMENTO (thread) ====================
    def toggle_monitoramento(self):
        if not self.monitorando:
            self.monitorando = True
            self.btn_monitor.config(text="⏹️ Parar Monitoramento", bg="#cc0000")
            threading.Thread(target=self.monitor_thread, daemon=True).start()
            self.log("▶️ Monitoramento iniciado (simulado + verificação de regras)")
        else:
            self.monitorando = False
            self.btn_monitor.config(text="▶️ Iniciar Monitoramento", bg="#00aa00")
            self.log("⏹️ Monitoramento parado")

    def monitor_thread(self):
        while self.monitorando:
            # Simulação realista de tráfego (a cada 3 segundos)
            if self.blocked_ips or self.restricted_ports:
                self.log(f"🔍 Verificando tráfego... {len(self.blocked_ips)} IPs e {len(self.restricted_ports)} portas monitorados")
                # Simula tentativa de conexão suspeita
                if self.blocked_ips:
                    self.log(f"🚫 Tentativa bloqueada automaticamente: IP {self.blocked_ips[0]}")
            time.sleep(3)

    def fechar(self):
        if messagebox.askokcancel("Sair", "Deseja realmente fechar? As regras aplicadas permanecem no firewall."):
            self.monitorando = False
            self.root.destroy()

if __name__ == "__main__":
    # AVISO IMPORTANTE
    print("🔴 EXECUTE COMO ADMINISTRADOR/ROOT para funcionar corretamente!")
    ProtótipoFirewall()