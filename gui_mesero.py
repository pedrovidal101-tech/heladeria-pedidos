import tkinter as tk
from tkinter import ttk, messagebox
from modelos.pedido_dao import PedidoDAO
from modelos.producto_dao import ProductoDAO


class VentanaMesero:
    def __init__(self, root):
        self.root = root
        self.root.title("Tomar Pedido - Mesero")
        self.root.geometry("500x560")

        self.productos = ProductoDAO.obtener_disponibles()  # [(id, nombre, precio)]
        self.items = []  # [(id_producto, nombre, precio, cantidad)]

        # Selección de mesa
        tk.Label(root, text="Seleccionar Mesa:", font=("Arial", 11, "bold")).pack(pady=5)
        self.combo_mesa = ttk.Combobox(root, values=["Mesa 1", "Mesa 2", "Mesa 3"], state="readonly")
        self.combo_mesa.current(0)
        self.combo_mesa.pack(pady=5)

        # Selección de producto y cantidad
        tk.Label(root, text="Producto:", font=("Arial", 11, "bold")).pack(pady=(15, 5))
        nombres = [f"{p[1]} - ${float(p[2]):,.0f}" for p in self.productos]
        self.combo_producto = ttk.Combobox(root, values=nombres, state="readonly", width=40)
        if nombres:
            self.combo_producto.current(0)
        self.combo_producto.pack(pady=5)

        marco_cant = tk.Frame(root)
        marco_cant.pack(pady=5)
        tk.Label(marco_cant, text="Cantidad:").pack(side="left", padx=5)
        self.spin_cantidad = tk.Spinbox(marco_cant, from_=1, to=20, width=5)
        self.spin_cantidad.pack(side="left")
        tk.Button(marco_cant, text="Agregar", command=self.agregar_producto).pack(side="left", padx=10)

        # Lista del pedido
        self.lista = tk.Listbox(root, width=55, height=10)
        self.lista.pack(pady=10)
        self.label_total = tk.Label(root, text="Total: $0", font=("Arial", 12, "bold"))
        self.label_total.pack()

        tk.Button(root, text="Quitar seleccionado", command=self.quitar_producto).pack(pady=5)

        # Botón Enviar Pedido
        btn_enviar = tk.Button(
            root,
            text="🚀 Enviar Pedido a Cocina",
            command=self.enviar_pedido,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold")
        )
        btn_enviar.pack(pady=15)

    def agregar_producto(self):
        indice = self.combo_producto.current()
        if indice < 0:
            messagebox.showwarning("Atención", "Selecciona un producto.")
            return
        try:
            cantidad = int(self.spin_cantidad.get())
            if cantidad < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atención", "La cantidad debe ser un número mayor a 0.")
            return

        id_producto, nombre, precio = self.productos[indice]
        self.items.append((id_producto, nombre, float(precio), cantidad))
        self.refrescar_lista()

    def quitar_producto(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        self.items.pop(seleccion[0])
        self.refrescar_lista()

    def refrescar_lista(self):
        self.lista.delete(0, tk.END)
        total = 0
        for _, nombre, precio, cantidad in self.items:
            subtotal = precio * cantidad
            total += subtotal
            self.lista.insert(tk.END, f"{cantidad} x {nombre}  =  ${subtotal:,.0f}")
        self.label_total.config(text=f"Total: ${total:,.0f}")

    def enviar_pedido(self):
        if not self.items:
            messagebox.showwarning("Atención", "Agrega al menos un producto al pedido.")
            return

        mesa_texto = self.combo_mesa.get()
        id_mesa = int(mesa_texto.split(" ")[1])
        productos = [(id_producto, cantidad) for id_producto, _, _, cantidad in self.items]

        id_pedido = PedidoDAO.guardar_pedido(id_mesa, productos)
        if id_pedido:
            messagebox.showinfo("Éxito", f"Pedido #{id_pedido} enviado a la cocina.")
            self.items.clear()
            self.refrescar_lista()
        else:
            messagebox.showerror("Error", "No se pudo registrar el pedido.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaMesero(root)
    root.mainloop()