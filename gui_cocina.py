import tkinter as tk
from tkinter import ttk, messagebox
from modelos.pedido_dao import PedidoDAO

class VentanaCocina:
    def __init__(self, root):
        self.root = root
        self.root.title("Pantalla de Cocina - Heladería")
        self.root.geometry("600x400")

        # Título
        tk.Label(root, text="Pedidos Pendientes", font=("Arial", 14, "bold")).pack(pady=10)

        # Tabla de Pedidos
        self.tabla = ttk.Treeview(root, columns=("ID", "Mesa", "Estado", "Fecha"), show="headings")
        self.tabla.heading("ID", text="ID Pedido")
        self.tabla.heading("Mesa", text="Mesa")
        self.tabla.heading("Estado", text="Estado")
        self.tabla.heading("Fecha", text="Fecha/Hora")
        
        self.tabla.column("ID", width=70, anchor="center")
        self.tabla.column("Mesa", width=80, anchor="center")
        self.tabla.column("Estado", width=120, anchor="center")
        self.tabla.column("Fecha", width=180, anchor="center")
        self.tabla.pack(pady=10, fill="both", expand=True)

        # Panel de Botones
        frame_botones = tk.Frame(root)
        frame_botones.pack(pady=10)

        btn_cargar = tk.Button(frame_botones, text="🔄 Cargar Pedidos", command=self.cargar_pedidos, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        btn_cargar.grid(row=0, column=0, padx=5)

        btn_preparar = tk.Button(frame_botones, text="🔥 En Preparación", command=lambda: self.cambiar_estado("en preparacion"), bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        btn_preparar.grid(row=0, column=1, padx=5)

        btn_listo = tk.Button(frame_botones, text="✅ Listo", command=lambda: self.cambiar_estado("listo"), bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_listo.grid(row=0, column=2, padx=5)

        self.cargar_pedidos()

    def cargar_pedidos(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
            
        pedidos = PedidoDAO.obtener_pedidos_pendientes()
        if pedidos:
            for p in pedidos:
                # p[0]=id_pedido, p[1]=id_mesa, p[2]=fecha_hora, p[3]=estado
                self.tabla.insert("", "end", values=(p[0], f"Mesa {p[1]}", p[2], p[3]))
                
    def cambiar_estado(self, nuevo_estado):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Selecciona un pedido de la lista.")
            return

        item = self.tabla.item(seleccionado)
        id_pedido = item['values'][0]

        if PedidoDAO.cambiar_estado(id_pedido, nuevo_estado):
            messagebox.showinfo("Éxito", f"Pedido #{id_pedido} cambiado a '{nuevo_estado}'.")
            self.cargar_pedidos()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el estado.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaCocina(root)
    root.mainloop()